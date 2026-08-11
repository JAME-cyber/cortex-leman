#!/usr/bin/env python3
"""fetch_source.py — récupère du contenu source pour les clips L'EFFET COMPOSÉ.

Passe Cloudflare et autres antibots basiques via curl_cffi (impersonation Chrome).
Cache disque pour éviter de re-fetcher. Extrait le texte propre (HTML → plain text).

Usage:
    python3 fetch_source.py <url>                          # fetch + texte propre
    python3 fetch_source.py <url> --raw                    # HTML brut
    python3 fetch_source.py <url> --json                   # structuré (status, body, meta)
    python3 fetch_source.py <url> --md                     # formaté markdown (défaut)
    python3 fetch_source.py <url> --ttl 86400              # cache 24h (défaut: 7 jours)
    python3 fetch_source.py <url> --no-cache               # bypass cache
    python3 fetch_source.py <url> -o research/iea.md       # écrire dans fichier

Détection de blocage: Cloudflare challenge, captcha Turnstile, paywall, 403/404.
Sortie: texte prêt à l'analyse, avec source URL + date fetch en en-tête.

Install: pip install curl-cffi   (ou dans le venv du projet)
Validé Jul 2026 sur IEA (passe Cloudflare), DigiTimes (paywall détecté), Euronext (OK).
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from curl_cffi import requests as cffi_req

UA = "EffetCompose-Research/1.0 (finance channel research)"
CACHE_DIR = Path(__file__).resolve().parent.parent / "research_cache"
DEFAULT_TTL = 7 * 24 * 3600  # 7 jours
IMPERSONATE = "chrome131"  # profil fingerprint le plus récent
TIMEOUT = 25

# Signaux de blocage (regex, case-insensitive)
BLOCK_PATTERNS = [
    (r"jschl_vc|cf-mitigated|cf-browser-verification|just a moment.*?checking your browser", "cloudflare_challenge"),
    (r"challenges\.cloudflare\.com/turnstile", "cloudflare_turnstile"),
    (r"<form[^>]*captcha|hcaptcha|recaptcha|g-recaptcha", "captcha_form"),
    (r"access denied|403 forbidden|not authorized", "access_denied"),
]
# Signaux de paywall (informatif — pas un blocage technique)
PAYWALL_PATTERNS = [
    r"subscribe to (read|continue|unlock)",
    r"premium content",
    r"sign in to continue reading",
    r"register to read",
    r"this article is for subscribers",
]


def cache_key(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def cache_path(url: str) -> Path:
    return CACHE_DIR / f"{cache_key(url)}.json"


def read_cache(url: str, ttl: int):
    p = cache_path(url)
    if not p.exists():
        return None
    age = time.time() - p.stat().st_mtime
    if age > ttl:
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def write_cache(url: str, data: dict):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path(url).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def fetch(url: str, ttl: int = DEFAULT_TTL, no_cache: bool = False) -> dict:
    """Fetch une URL avec impersonation Chrome. Retourne un dict structuré."""
    if not no_cache:
        cached = read_cache(url, ttl)
        if cached:
            cached["from_cache"] = True
            return cached

    headers = {
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    t0 = time.time()
    r = cffi_req.get(url, impersonate=IMPERSONATE, headers=headers, timeout=TIMEOUT, allow_redirects=True)
    elapsed = time.time() - t0
    text = r.text

    blocks_found = []
    for pat, label in BLOCK_PATTERNS:
        if re.search(pat, text, re.I | re.S):
            blocks_found.append(label)
    paywall_found = [pat for pat in PAYWALL_PATTERNS if re.search(pat, text, re.I)]

    title_m = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
    title = title_m.group(1).strip() if title_m else None
    meta_desc = None
    md_m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', text, re.I | re.S)
    if md_m:
        meta_desc = md_m.group(1).strip()

    data = {
        "url": url,
        "final_url": str(r.url),
        "status": r.status_code,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_s": round(elapsed, 2),
        "title": title,
        "meta_description": meta_desc,
        "html": text,
        "len": len(text),
        "blocks": blocks_found,
        "paywall_signals": paywall_found,
        "from_cache": False,
    }
    write_cache(url, data)
    return data


def html_to_text(html: str) -> str:
    """Conversion HTML → texte propre pour analyse."""
    html = re.sub(r"<(script|style|nav|footer|header|aside)[^>]*>.*?</\1>", "", html, flags=re.I | re.S)
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.I)
    text = re.sub(r"</(p|div|h[1-6]|li|tr)>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = (text.replace("&nbsp;", " ").replace("&amp;", "&")
                .replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
                .replace("&#39;", "'").replace("&apos;", "'"))
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def to_markdown(data: dict) -> str:
    """Format markdown avec en-tête source."""
    lines = [
        f"# {data.get('title') or '(sans titre)'}",
        "",
        f"**Source :** {data['url']}",
        f"**URL finale :** {data['final_url']}",
        f"**Fetché le :** {data['fetched_at']} ({data['elapsed_s']}s){'  [cache]' if data.get('from_cache') else ''}",
        f"**HTTP :** {data['status']} · **Taille :** {data['len']:,} chars",
    ]
    if data.get("meta_description"):
        lines.append(f"**Description :** {data['meta_description']}")
    if data["blocks"]:
        lines.append(f"**⚠ Blocage détecté :** {', '.join(data['blocks'])}")
    if data["paywall_signals"]:
        lines.append(f"**⚠ Paywall potentiel :** {len(data['paywall_signals'])} signaux")
    lines.append("")
    body = html_to_text(data["html"])
    if len(body) > 50000:
        body = body[:50000] + "\n\n...[tronqué — cache complet dans research_cache/]"
    lines.append(body)
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Fetch source LEC avec bypass antibot + cache")
    ap.add_argument("url", help="URL à fetcher")
    ap.add_argument("-o", "--output", help="Fichier de sortie (défaut: stdout)")
    fmt = ap.add_mutually_exclusive_group()
    fmt.add_argument("--raw", action="store_true", help="HTML brut")
    fmt.add_argument("--json", action="store_true", help="JSON structuré")
    fmt.add_argument("--md", action="store_true", help="Markdown formaté (défaut)")
    ap.add_argument("--ttl", type=int, default=DEFAULT_TTL, help=f"TTL cache en sec (défaut: {DEFAULT_TTL})")
    ap.add_argument("--no-cache", action="store_true", help="Bypass cache")
    args = ap.parse_args()

    data = fetch(args.url, ttl=args.ttl, no_cache=args.no_cache)

    if args.raw:
        out = data["html"]
    elif args.json:
        out = json.dumps(data, ensure_ascii=False, indent=2)
    else:
        out = to_markdown(data)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"✓ Écrit: {args.output} ({len(out):,} chars)", file=sys.stderr)
    else:
        print(out)

    if data["blocks"]:
        print(f"\n⚠ ATTENTION: blocage détecté ({', '.join(data['blocks'])}) — contenu peut être incomplet", file=sys.stderr)
    if data["paywall_signals"]:
        print(f"⚠ ATTENTION: {len(data['paywall_signals'])} signaux de paywall — contenu article peut être tronqué", file=sys.stderr)


if __name__ == "__main__":
    main()
