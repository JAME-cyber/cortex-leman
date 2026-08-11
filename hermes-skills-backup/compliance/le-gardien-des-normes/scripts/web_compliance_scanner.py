#!/usr/bin/env python3
"""
Cortex Leman — Web Compliance Scanner
Scanne un site web pour des vérifications de conformité RGPD/IA.
Génère un rapport structuré utilisable dans un audit.

Usage:
    python web_compliance_scanner.py <URL> [--json] [--output rapport.txt]

Checks (7):
    1. Trackers & analytics tiers (GA, Meta Pixel, Hotjar, chatbots IA, etc.)
    2. Bandeau cookies / CMP (Didomi, tarteaucitron, OneTrust, etc.)
    3. Formulaires collectant des PII (email, téléphone, CB, SSN, etc.)
    4. Headers de sécurité (CSP, HSTS, X-Frame-Options, etc.)
    5. Politique de confidentialité (présence, liens)
    6. Mentions IA / chatbot (déclenche Art. 22 RGPD + AI Act)
    7. TLS / HTTPS

Requirements: pip install httpx beautifulsoup4 lxml

Limitation: analyse le HTML statique uniquement. Les sites JS-heavy (SPA)
peuvent nécessiter un rendu headless (Playwright) pour détecter les trackers
chargés dynamiquement.
"""

import argparse
import json
import re
import sys
from datetime import datetime
from urllib.parse import urlparse, urljoin

try:
    import httpx
    from bs4 import BeautifulSoup
except ImportError:
    print("Install dependencies: pip install httpx beautifulsoup4 lxml", file=sys.stderr)
    sys.exit(1)

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

TIMEOUT = 15
USER_AGENT = "CortexLeman-ComplianceScanner/1.0 (+https://cortexleman.ch)"

# Trackers: (pattern, name, category, severity)
TRACKERS_DB = [
    ("googletagmanager.com/gtm.js", "Google Tag Manager", "Analytics", "medium"),
    ("google-analytics.com/analytics.js", "Google Analytics (UA)", "Analytics", "high"),
    ("google-analytics.com/ga.js", "Google Analytics (legacy)", "Analytics", "high"),
    ("gtag/js?id=", "Google gtag", "Analytics", "medium"),
    ("googletagservices.com", "Google Ads", "Advertising", "high"),
    ("doubleclick.net", "DoubleClick / Google Ads", "Advertising", "high"),
    ("adsbygoogle.js", "Google AdSense", "Advertising", "high"),
    ("connect.facebook.net", "Meta Pixel", "Advertising", "high"),
    ("fbq(", "Meta Pixel", "Advertising", "high"),
    ("fbevents.js", "Meta Pixel", "Advertising", "high"),
    ("platform.twitter.com", "Twitter/X Embed", "Social", "low"),
    ("platform.linkedin.com", "LinkedIn Embed", "Social", "low"),
    ("instagram.com/embed", "Instagram Embed", "Social", "low"),
    ("hotjar.com", "Hotjar", "Session Recording", "high"),
    ("clarity.ms", "Microsoft Clarity", "Session Recording", "high"),
    ("fullstory.com", "FullStory", "Session Recording", "high"),
    ("mixpanel.com", "Mixpanel", "Analytics", "medium"),
    ("segment.com", "Segment", "Analytics", "medium"),
    ("amplitude.com", "Amplitude", "Analytics", "medium"),
    ("matomo.cloud", "Matomo Cloud", "Analytics", "low"),
    ("matomo.js", "Matomo", "Analytics", "low"),
    ("plausible.io", "Plausible", "Analytics", "low"),
    ("intercom.io", "Intercom (Chat)", "Chatbot", "medium"),
    ("crisp.chat", "Crisp (Chat)", "Chatbot", "medium"),
    ("tawk.to", "Tawk.to (Chat)", "Chatbot", "medium"),
    ("drift.com", "Drift (Chat)", "Chatbot", "medium"),
    ("chatgpt", "ChatGPT / OpenAI", "AI Widget", "high"),
    ("dialogflow", "Google Dialogflow", "AI Chatbot", "high"),
    ("ibm-watson", "IBM Watson", "AI Chatbot", "high"),
    ("hubspot.com", "HubSpot", "CRM/Marketing", "medium"),
    ("mailchimp.com", "Mailchimp", "Marketing", "medium"),
    ("salesforce.com", "Salesforce", "CRM", "medium"),
    ("optimizely.com", "Optimizely", "A/B Testing", "medium"),
    ("abtasty.com", "ABTasty", "A/B Testing", "medium"),
]

CMP_DB = [
    "didomi", "tarteaucitron", "cookiebot", "trustarc", "onetrust",
    "consentmanager", "quantcast", "sourcepoint", "axeptio", "appconsent",
    "commandersact", "brevo-consent", "klaro", "termly",
]

PII_PATTERNS = [
    (r'type=["\']email["\']', "Email", "high"),
    (r'type=["\']tel["\']', "Téléphone", "high"),
    (r'name=["\'].*(name|nom|prenom|firstname|lastname).*["\']', "Nom/Prénom", "high"),
    (r'name=["\'].*(address|adresse|rue|street).*["\']', "Adresse postale", "high"),
    (r'name=["\'].*(date.*naiss|birthdate|dob).*["\']', "Date de naissance", "high"),
    (r'name=["\'].*(company|societe|entreprise).*["\']', "Entreprise", "low"),
    (r'type=["\']password["\']', "Mot de passe", "high"),
    (r'name=["\'].*(card|carte|cb|credit).*["\']', "Carte de paiement", "critical"),
    (r'name=["\'].*(ssn|secu|sociale|national).*["\']', "Numéro sécurité sociale", "critical"),
    (r'type=["\']file["\']', "Upload de fichier", "medium"),
]

SECURITY_HEADERS = {
    "strict-transport-security": ("HSTS", "high"),
    "content-security-policy": ("CSP", "high"),
    "x-frame-options": ("X-Frame-Options", "medium"),
    "x-content-type-options": ("X-Content-Type-Options", "medium"),
    "referrer-policy": ("Referrer-Policy", "low"),
    "permissions-policy": ("Permissions-Policy", "low"),
    "cross-origin-opener-policy": ("COOP", "low"),
    "cross-origin-resource-policy": ("CORP", "low"),
}

PRIVACY_PATTERNS = [
    r'privacy.?policy', r'politique.?de.?confidentialit',
    r'datenschutz', r'privacy.?notice', r'mentions.?légales',
    r'rgpd', r'gdpr', r'data.?protection',
    r'protection.?des.?données', r'protection.?der.?daten',
    r'déclaration.?de.?confidentialit', r'datenschutzerklärung',
    r'confidentialité',
]

AI_PATTERNS = [
    (r'\bchatbot\b', "Chatbot mentionné"),
    (r'\bartificial.?intelligence\b', "IA mentionnée"),
    (r'\bmachine.?learning\b', "ML mentionné"),
    (r'\bautomatique?.?r ponse\b', "Réponse automatique"),
    (r'\bassistant.?virtuel\b', "Assistant virtuel"),
    (r'\bIA\b', "IA (sigle)"),
    (r'\bAI\b', "AI (sigle)"),
    (r'\bGPT\b', "GPT mentionné"),
    (r'\bautomatis', "Automatisation"),
]


class ComplianceScanner:
    def __init__(self, url: str):
        self.url = url
        self.parsed = urlparse(url)
        self.domain = self.parsed.netloc
        self.results = {
            "url": url,
            "domain": self.domain,
            "scan_date": datetime.now().isoformat(),
            "checks": {},
        }

    def fetch(self, url: str):
        try:
            return httpx.get(
                url, headers={"User-Agent": USER_AGENT},
                follow_redirects=True, timeout=TIMEOUT, verify=True,
            )
        except Exception:
            return None

    def run(self) -> dict:
        resp = self.fetch(self.url)
        if not resp:
            self.results["error"] = f"Impossible de joindre {self.url}"
            self.results["status"] = "unreachable"
            return self.results

        html = resp.text
        soup = BeautifulSoup(html, "lxml")
        self.results["status_code"] = resp.status_code
        self.results["final_url"] = str(resp.url)

        self._check_tls(resp)
        self._check_trackers(html)
        self._check_cmp(html, soup)
        self._check_forms(html)
        self._check_headers(resp)
        self._check_privacy_policy(resp, soup)
        self._check_ai_mentions(html)
        self._compute_verdict()
        return self.results

    def _check_tls(self, resp):
        is_https = self.url.startswith("https://")
        hsts = "strict-transport-security" in resp.headers
        check = {"title": "TLS / HTTPS", "status": "pass" if is_https else "fail",
                 "severity": "critical" if not is_https else None,
                 "details": {"https_enabled": is_https, "hsts_present": hsts}, "findings": []}
        if not is_https:
            check["findings"].append("🔴 Le site n'utilise pas HTTPS — données en clair sur le réseau")
        elif not hsts:
            check["findings"].append("🟡 HTTPS actif mais HSTS absent — risque de downgrade attack")
        else:
            check["findings"].append("✅ HTTPS + HSTS actifs")
        self.results["checks"]["tls"] = check

    def _check_trackers(self, html: str):
        html_lower = html.lower()
        found = []
        for pattern, name, category, severity in TRACKERS_DB:
            if pattern.lower() in html_lower:
                found.append({"name": name, "category": category, "severity": severity})
        seen, unique = set(), []
        for t in found:
            if t["name"] not in seen:
                seen.add(t["name"]); unique.append(t)
        found = unique
        high_count = sum(1 for t in found if t["severity"] in ("high", "critical"))
        status = "pass" if not found else ("fail" if high_count > 0 else "warn")
        check = {"title": "Trackers & Analytics tiers", "status": status,
                 "tracker_count": len(found), "high_severity_count": high_count, "findings": []}
        if not found:
            check["findings"].append("✅ Aucun tracker tiers détecté")
        else:
            check["findings"].append(f"⚠️ {len(found)} tracker(s) détecté(s):")
            for t in found:
                icon = {"critical": "🔴", "high": "🔴", "medium": "🟡", "low": "🟢"}[t["severity"]]
                check["findings"].append(f"  {icon} {t['name']} — {t['category']}")
            if high_count:
                check["findings"].append(f"🔴 {high_count} tracker(s) haute sévérité — consentement explicite requis (RGPD Art. 7)")
        cats = {}
        for t in found:
            cats.setdefault(t["category"], []).append(t["name"])
        check["categories"] = cats
        self.results["checks"]["trackers"] = check

    def _check_cmp(self, html: str, soup):
        html_lower = html.lower()
        found_cmp = [c for c in CMP_DB if c in html_lower]
        cookie_kw = ["cookie", "consentement", "einwilligung"]
        has_cookie_text = any(k in html_lower for k in cookie_kw)
        has_cmp = bool(found_cmp)
        status = "pass" if has_cmp else ("warn" if has_cookie_text else "fail")
        check = {"title": "Bandeau cookies / CMP", "status": status,
                 "details": {"cmp_detected": has_cmp, "cmp_name": found_cmp[0] if found_cmp else None,
                             "cookie_text_present": has_cookie_text}, "findings": []}
        if has_cmp:
            check["findings"].append(f"✅ CMP détecté: {found_cmp[0]}")
        elif has_cookie_text:
            check["findings"].append("🟡 Mention 'cookies' présente mais pas de CMP reconnu — vérifier manuellement")
        else:
            check["findings"].append("🔴 Aucun bandeau cookies / CMP détecté — non-conforme RGPD si trackers présents")
        self.results["checks"]["cookie_consent"] = check

    def _check_forms(self, html: str):
        forms = re.findall(r'<form[^>]*>.*?</form>', html, re.DOTALL | re.IGNORECASE)
        form_findings = []
        for i, form_html in enumerate(forms):
            fields = []
            for pattern, name, severity in PII_PATTERNS:
                if re.search(pattern, form_html, re.IGNORECASE):
                    fields.append({"name": name, "severity": severity})
            if fields:
                form_findings.append({"form_index": i, "pii_fields": fields})
        has_pii = bool(form_findings)
        status = "warn" if has_pii else "pass"
        check = {"title": "Formulaires & collecte de données personnelles", "status": status,
                 "form_count": len(forms), "forms_with_pii": len(form_findings), "findings": []}
        if not forms:
            check["findings"].append("ℹ️ Aucun formulaire détecté")
        elif not has_pii:
            check["findings"].append("✅ Formulaires présents mais aucun champ PII évident")
        else:
            for ff in form_findings:
                fields_str = ", ".join(f["name"] for f in ff["pii_fields"])
                check["findings"].append(f"⚠️ Formulaire #{ff['form_index']}: {fields_str}")
                check["findings"].append(f"    → Vérifier: finalité (Art. 5), consentement (Art. 6/7), droits (Art. 15-17)")
        self.results["checks"]["forms"] = check

    def _check_headers(self, resp):
        present, missing = {}, {}
        for header, (name, severity) in SECURITY_HEADERS.items():
            value = resp.headers.get(header)
            if value:
                present[name] = value[:100]
            else:
                missing[name] = severity
        crit = [k for k, v in missing.items() if v == "high"]
        status = "pass" if not missing else ("fail" if crit else "warn")
        check = {"title": "Headers de sécurité HTTP", "status": status,
                 "headers_present": len(present), "headers_missing": len(missing), "findings": []}
        for name, val in present.items():
            check["findings"].append(f"✅ {name}: présent")
        for name, sev in missing.items():
            icon = "🔴" if sev == "high" else "🟡"
            check["findings"].append(f"{icon} {name}: absent")
        self.results["checks"]["security_headers"] = check

    def _check_privacy_policy(self, resp, soup):
        links = soup.find_all("a", href=True)
        found_links = []
        for link in links:
            href = link.get("href", "")
            text = link.get_text(strip=True).lower()
            combined = f"{href} {text}".lower()
            for pattern in PRIVACY_PATTERNS:
                if re.search(pattern, combined):
                    found_links.append({"text": text[:50], "url": urljoin(str(resp.url), href)})
                    break
        page_text = soup.get_text().lower()
        has_mention = any(re.search(p, page_text) for p in PRIVACY_PATTERNS)
        status = "pass" if found_links else ("warn" if has_mention else "fail")
        check = {"title": "Politique de confidentialité", "status": status,
                 "details": {"policy_link_found": bool(found_links), "links": [l["url"] for l in found_links[:3]]},
                 "findings": []}
        if found_links:
            for l in found_links[:3]:
                check["findings"].append(f"✅ Lien trouvé: '{l['text']}' → {l['url']}")
        elif has_mention:
            check["findings"].append("🟡 Mention RGPD dans le texte mais aucun lien dédié")
        else:
            check["findings"].append("🔴 Aucune politique de confidentialité détectée — non-conforme RGPD")
        self.results["checks"]["privacy_policy"] = check

    def _check_ai_mentions(self, html: str):
        soup = BeautifulSoup(html, "lxml")
        for s in soup(["script", "style"]):
            s.decompose()
        text = soup.get_text().lower()
        found = []
        for pattern, desc in AI_PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                found.append({"description": desc, "count": len(matches)})
        check = {"title": "Mentions d'IA / Chatbot", "status": "info",
                 "ai_mentions_count": len(found), "findings": []}
        if not found:
            check["findings"].append("ℹ️ Aucune mention d'IA détectée")
        else:
            check["findings"].append(f"ℹ️ {len(found)} mention(s) d'IA:")
            for item in found:
                check["findings"].append(f"    → {item['description']} ({item['count']}x)")
            check["findings"].append("    → Si IA traite des données personnelles: évaluation requise (RGPD Art. 22, AI Act)")
        self.results["checks"]["ai_mentions"] = check

    def _compute_verdict(self):
        checks = self.results["checks"]
        fails = [k for k, v in checks.items() if v.get("status") == "fail"]
        warns = [k for k, v in checks.items() if v.get("status") == "warn"]
        criticals = [k for k, v in checks.items() if v.get("severity") in ("critical", "high")]
        if fails:
            verdict, color = "NON-CONFORME", "🔴"
        elif len(warns) >= 2:
            verdict, color = "CONFORMITÉ PARTIELLE", "🟡"
        elif warns:
            verdict, color = "CONFORME AVEC RÉSERVES", "🟡"
        else:
            verdict, color = "CONFORME", "✅"
        critical_areas = list(dict.fromkeys(fails + [k for k in warns if k in criticals]))
        self.results["verdict"] = {"label": verdict, "color": color,
                                   "fail_count": len(fails), "warn_count": len(warns),
                                   "critical_areas": critical_areas}


def generate_report(results: dict, output_format: str = "text") -> str:
    if output_format == "json":
        return json.dumps(results, indent=2, ensure_ascii=False)
    lines = []
    lines.append("=" * 60)
    lines.append("  CORTEX LEMAN — RAPPORT DE CONFORMITÉ WEB")
    lines.append("=" * 60)
    lines.append(f"\n  URL: {results.get('url', 'N/A')}")
    lines.append(f"  Domaine: {results.get('domain', 'N/A')}")
    lines.append(f"  Date: {results.get('scan_date', 'N/A')[:19]}")
    lines.append(f"  Statut HTTP: {results.get('status_code', 'N/A')}\n")
    v = results.get("verdict", {})
    lines.append(f"  VERDICT: {v.get('color', '')} {v.get('label', 'N/A')}")
    lines.append(f"  Non-conformités: {v.get('fail_count', 0)} | Points d'attention: {v.get('warn_count', 0)}\n")
    lines.append("-" * 60 + "\n")
    names = {"tls": "1. TLS / HTTPS", "trackers": "2. Trackers & Analytics",
             "cookie_consent": "3. Bandeau cookies / CMP", "forms": "4. Formulaires & PII",
             "security_headers": "5. Headers de sécurité", "privacy_policy": "6. Politique de confidentialité",
             "ai_mentions": "7. Mentions IA / Chatbot"}
    for key, title in names.items():
        check = results["checks"].get(key)
        if not check:
            continue
        lines.append(f"  {title}\n  Statut: {check['status'].upper()}\n")
        for f in check["findings"]:
            lines.append(f"    {f}")
        lines.append(f"\n{'-' * 60}\n")
    lines.append("  Recommandations prioritaires:\n")
    for area in v.get("critical_areas", []):
        lines.append(f"    → Corriger: {area}")
    if not v.get("critical_areas"):
        lines.append("    → Aucune action critique requise")
    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Cortex Leman — Web Compliance Scanner")
    parser.add_argument("url", help="URL à scanner")
    parser.add_argument("--json", action="store_true", help="Sortie JSON")
    parser.add_argument("--output", "-o", help="Fichier de sortie")
    args = parser.parse_args()
    url = args.url if args.url.startswith("http") else f"https://{args.url}"
    scanner = ComplianceScanner(url)
    results = scanner.run()
    if "error" in results:
        print(f"ERREUR: {results['error']}", file=sys.stderr); sys.exit(1)
    report = generate_report(results, "json" if args.json else "text")
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Rapport sauvegardé: {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
