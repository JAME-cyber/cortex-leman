#!/usr/bin/env python3
"""
Cortex Leman — Web Compliance Scanner
Scanne un site web pour des vérifications de conformité RGPD/IA.
Génère un rapport structuré utilisable dans un audit.

Usage:
    python web_compliance_scanner.py <URL> [--json] [--pdf]

Checks:
    1. Trackers & analytics tiers (GA, Meta Pixel, etc.)
    2. Bandeau cookies / CMP
    3. Formulaires collectant des PII
    4. Headers de sécurité (CSP, HSTS, etc.)
    5. Politique de confidentialité (présence)
    6. Mentions IA / chatbot
    7. TLS / HTTPS
"""

import argparse
import json
import re
import sys
from datetime import datetime
from urllib.parse import urlparse, urljoin

import httpx
from bs4 import BeautifulSoup

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

TIMEOUT = 15
USER_AGENT = "CortexLeman-ComplianceScanner/1.0 (+https://cortexleman.ch)"

# Trackers connus: (pattern dans le HTML/JS, nom, catégorie, sévérité)
TRACKERS_DB = [
    # Google
    ("googletagmanager.com/gtm.js", "Google Tag Manager", "Analytics", "medium"),
    ("google-analytics.com/analytics.js", "Google Analytics (UA)", "Analytics", "high"),
    ("google-analytics.com/ga.js", "Google Analytics (legacy)", "Analytics", "high"),
    ("gtag/js?id=", "Google gtag", "Analytics", "medium"),
    ("googletagservices.com", "Google Ads", "Advertising", "high"),
    ("doubleclick.net", "DoubleClick / Google Ads", "Advertising", "high"),
    ("adsbygoogle.js", "Google AdSense", "Advertising", "high"),
    # Meta
    ("connect.facebook.net", "Meta Pixel", "Advertising", "high"),
    ("fbq(", "Meta Pixel", "Advertising", "high"),
    ("fbevents.js", "Meta Pixel", "Advertising", "high"),
    # Autres réseaux sociaux
    ("platform.twitter.com", "Twitter/X Embed", "Social", "low"),
    ("platform.linkedin.com", "LinkedIn Embed", "Social", "low"),
    ("instagram.com/embed", "Instagram Embed", "Social", "low"),
    # Hotjar / Clarity / FullStory
    ("hotjar.com", "Hotjar", "Session Recording", "high"),
    ("clarity.ms", "Microsoft Clarity", "Session Recording", "high"),
    ("fullstory.com", "FullStory", "Session Recording", "high"),
    # Autres analytics
    ("mixpanel.com", "Mixpanel", "Analytics", "medium"),
    ("segment.com", "Segment", "Analytics", "medium"),
    ("amplitude.com", "Amplitude", "Analytics", "medium"),
    ("matomo.cloud", "Matomo Cloud", "Analytics", "low"),
    ("matomo.js", "Matomo", "Analytics", "low"),
    ("plausible.io", "Plausible", "Analytics", "low"),
    # Chatbots / IA
    ("intercom.io", "Intercom (Chat)", "Chatbot", "medium"),
    ("crisp.chat", "Crisp (Chat)", "Chatbot", "medium"),
    ("tawk.to", "Tawk.to (Chat)", "Chatbot", "medium"),
    ("drift.com", "Drift (Chat)", "Chatbot", "medium"),
    ("chatgpt", "ChatGPT / OpenAI", "AI Widget", "high"),
    ("dialogflow", "Google Dialogflow", "AI Chatbot", "high"),
    ("ibm-watson", "IBM Watson", "AI Chatbot", "high"),
    # CRM / Marketing
    ("hubspot.com", "HubSpot", "CRM/Marketing", "medium"),
    ("mailchimp.com", "Mailchimp", "Marketing", "medium"),
    ("salesforce.com", "Salesforce", "CRM", "medium"),
    # A/B testing
    ("optimizely.com", "Optimizely", "A/B Testing", "medium"),
    ("abtasty.com", "ABTasty", "A/B Testing", "medium"),
]

# CMP (Consent Management Platforms) connus
CMP_DB = [
    "didomi", "tarteaucitron", "cookiebot", "trustarc", "onetrust",
    "consentmanager", "quantcast", "sourcepoint", "axeptio", "appconsent",
    "commandersact", "brevo-consent", "klaro", "termly",
]

# Patterns de champs PII dans les formulaires
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

# Headers de sécurité attendus
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

# Patterns de politique de confidentialité
PRIVACY_PATTERNS = [
    r'privacy.?policy', r'politique.?de.?confidentialit',
    r'datenschutz', r'privacy.?notice', r'mentions.?légales',
    r'rgpd', r'gdpr', r'data.?protection',
    r'protection.?des.?données', r'protection.?der.?daten',
    r'déclaration.?de.?confidentialit', r'datenschutzerklärung',
    r'confidentialité', r'datenschutz',
]

# Patterns de mentions IA
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


# ──────────────────────────────────────────────
# Scanner
# ──────────────────────────────────────────────

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

    def fetch(self, url: str) -> httpx.Response | None:
        try:
            resp = httpx.get(
                url,
                headers={"User-Agent": USER_AGENT},
                follow_redirects=True,
                timeout=TIMEOUT,
                verify=True,
            )
            return resp
        except httpx.ConnectError:
            return None
        except httpx.TimeoutException:
            return None
        except Exception:
            return None

    def run(self) -> dict:
        print(f"  Scan de {self.url}...")

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

    # ── 1. TLS / HTTPS ──────────────────────

    def _check_tls(self, resp):
        is_https = self.url.startswith("https://")
        hsts = "strict-transport-security" in resp.headers

        check = {
            "title": "TLS / HTTPS",
            "status": "pass" if is_https else "fail",
            "severity": "critical" if not is_https else None,
            "details": {
                "https_enabled": is_https,
                "hsts_present": hsts,
                "protocol": self.parsed.scheme.upper(),
            },
            "findings": [],
        }
        if not is_https:
            check["findings"].append("🔴 Le site n'utilise pas HTTPS — données en clair sur le réseau")
        elif not hsts:
            check["findings"].append("🟡 HTTPS actif mais HSTS absent — risque de downgrade attack")
        else:
            check["findings"].append("✅ HTTPS + HSTS actifs")

        self.results["checks"]["tls"] = check

    # ── 2. Trackers & Analytics ─────────────

    def _check_trackers(self, html: str):
        html_lower = html.lower()
        found = []

        for pattern, name, category, severity in TRACKERS_DB:
            if pattern.lower() in html_lower:
                found.append({
                    "name": name,
                    "category": category,
                    "severity": severity,
                    "pattern": pattern,
                })

        # Dédupliquer: un même tracker peut matcher plusieurs patterns
        seen = set()
        unique_found = []
        for t in found:
            key = t["name"]
            if key not in seen:
                seen.add(key)
                unique_found.append(t)
        found = unique_found

        high_count = sum(1 for t in found if t["severity"] in ("high", "critical"))
        status = "pass" if len(found) == 0 else ("fail" if high_count > 0 else "warn")

        check = {
            "title": "Trackers & Analytics tiers",
            "status": status,
            "severity": "high" if high_count > 0 else "low",
            "tracker_count": len(found),
            "high_severity_count": high_count,
            "findings": [],
        }

        if not found:
            check["findings"].append("✅ Aucun tracker tiers détecté dans le code source")
        else:
            check["findings"].append(f"⚠️ {len(found)} tracker(s) détecté(s):")
            for t in found:
                icon = {"critical": "🔴", "high": "🔴", "medium": "🟡", "low": "🟢"}[t["severity"]]
                check["findings"].append(f"  {icon} {t['name']} — catégorie: {t['category']}")

            if high_count > 0:
                check["findings"].append(
                    f"🔴 {high_count} tracker(s) haute sévérité — consentement explicite requis (RGPD Art. 7)"
                )

        # Catégoriser
        categories = {}
        for t in found:
            cat = t["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(t["name"])
        check["categories"] = categories

        self.results["checks"]["trackers"] = check

    # ── 3. CMP / Bandeau cookies ────────────

    def _check_cmp(self, html: str, soup: BeautifulSoup):
        html_lower = html.lower()
        found_cmp = []
        for cmp in CMP_DB:
            if cmp in html_lower:
                found_cmp.append(cmp)

        # Détecter aussi des divs/banners génériques
        cookie_keywords = ["cookie", "consentement", "einwilligung"]
        has_cookie_text = any(kw in html_lower for kw in cookie_keywords)

        has_cmp = len(found_cmp) > 0
        has_banner = has_cmp or (has_cookie_text and ("banner" in html_lower or "banner" in html_lower))

        status = "pass" if has_cmp else ("warn" if has_cookie_text else "fail")

        check = {
            "title": "Bandeau cookies / CMP",
            "status": status,
            "severity": "high" if not has_cmp and not has_cookie_text else None,
            "details": {
                "cmp_detected": has_cmp,
                "cmp_name": found_cmp[0] if found_cmp else None,
                "cookie_text_present": has_cookie_text,
            },
            "findings": [],
        }

        if has_cmp:
            check["findings"].append(f"✅ CMP détecté: {found_cmp[0]}")
        elif has_cookie_text:
            check["findings"].append("🟡 Mention 'cookies' présente mais pas de CMP reconnu — vérifier manuellement")
        else:
            check["findings"].append("🔴 Aucun bandeau cookies / CMP détecté — non-conforme RGPD si trackers présents")

        self.results["checks"]["cookie_consent"] = check

    # ── 4. Formulaires & PII ────────────────

    def _check_forms(self, html: str):
        forms = re.findall(r'<form[^>]*>.*?</form>', html, re.DOTALL | re.IGNORECASE)
        form_findings = []

        for i, form_html in enumerate(forms):
            fields = []
            for pattern, name, severity in PII_PATTERNS:
                if re.search(pattern, form_html, re.IGNORECASE):
                    fields.append({"name": name, "severity": severity})

            if fields:
                critical = [f for f in fields if f["severity"] == "critical"]
                high = [f for f in fields if f["severity"] == "high"]
                form_findings.append({
                    "form_index": i,
                    "pii_fields": fields,
                    "critical_count": len(critical),
                    "high_count": len(high),
                })

        has_pii = len(form_findings) > 0
        has_critical = any(f["critical_count"] > 0 for f in form_findings)

        status = "warn" if has_critical else ("warn" if has_pii else "pass")

        check = {
            "title": "Formulaires & collecte de données personnelles",
            "status": status,
            "severity": "high" if has_pii else None,
            "form_count": len(forms),
            "forms_with_pii": len(form_findings),
            "findings": [],
        }

        if not forms:
            check["findings"].append("ℹ️ Aucun formulaire détecté sur la page")
        elif not has_pii:
            check["findings"].append("✅ Formulaires présents mais aucun champ PII évident détecté")
        else:
            for ff in form_findings:
                icons = " ".join(
                    {"critical": "🔴", "high": "🔴", "medium": "🟡", "low": "🟢"}[f["severity"]]
                    for f in ff["pii_fields"]
                )
                fields_str = ", ".join(f["name"] for f in ff["pii_fields"])
                check["findings"].append(f"⚠️ Formulaire #{ff['form_index']}: {fields_str}")
                check["findings"].append(
                    f"    → Vérifier: mention de finalité (Art. 5), consentement (Art. 6/7), "
                    f"droits d'accès/rectification (Art. 15-17)"
                )

        self.results["checks"]["forms"] = check

    # ── 5. Headers de sécurité ──────────────

    def _check_headers(self, resp: httpx.Response):
        present = {}
        missing = {}

        for header, (name, severity) in SECURITY_HEADERS.items():
            value = resp.headers.get(header)
            if value:
                present[name] = {"header": header, "value": value[:100], "severity": severity}
            else:
                missing[name] = {"header": header, "severity": severity}

        critical_missing = [k for k, v in missing.items() if v["severity"] == "high"]
        status = "pass" if not missing else ("fail" if critical_missing else "warn")

        check = {
            "title": "Headers de sécurité HTTP",
            "status": status,
            "severity": "high" if critical_missing else "low",
            "headers_present": len(present),
            "headers_missing": len(missing),
            "findings": [],
        }

        for name, info in present.items():
            check["findings"].append(f"✅ {name}: présent")

        for name, info in missing.items():
            icon = "🔴" if info["severity"] == "high" else "🟡"
            check["findings"].append(f"{icon} {name}: absent")

        self.results["checks"]["security_headers"] = check

    # ── 6. Politique de confidentialité ─────

    def _check_privacy_policy(self, resp: httpx.Response, soup: BeautifulSoup):
        links = soup.find_all("a", href=True)
        found_links = []

        for link in links:
            href = link.get("href", "")
            text = link.get_text(strip=True).lower()
            combined = f"{href} {text}".lower()

            for pattern in PRIVACY_PATTERNS:
                if re.search(pattern, combined):
                    absolute_url = urljoin(str(resp.url), href)
                    found_links.append({"text": text[:50], "url": absolute_url})
                    break

        # Vérifier aussi dans le texte de la page
        page_text = soup.get_text().lower()
        has_mention = any(re.search(p, page_text) for p in PRIVACY_PATTERNS)

        status = "pass" if found_links else ("warn" if has_mention else "fail")

        check = {
            "title": "Politique de confidentialité",
            "status": status,
            "severity": "high" if not found_links and not has_mention else None,
            "details": {
                "policy_link_found": bool(found_links),
                "policy_mention_found": has_mention,
                "links": [l["url"] for l in found_links],
            },
            "findings": [],
        }

        if found_links:
            for l in found_links[:3]:
                check["findings"].append(f"✅ Lien trouvé: '{l['text']}' → {l['url']}")
        elif has_mention:
            check["findings"].append("🟡 Mention RGPD/confidentialité dans le texte mais aucun lien dédié trouvé")
        else:
            check["findings"].append("🔴 Aucune politique de confidentialité détectée — non-conforme RGPD")

        self.results["checks"]["privacy_policy"] = check

    # ── 7. Mentions IA ──────────────────────

    def _check_ai_mentions(self, html: str):
        # Extraire le texte visible (sans scripts/styles)
        soup = BeautifulSoup(html, "lxml")
        for script in soup(["script", "style"]):
            script.decompose()
        visible_text = soup.get_text().lower()

        found = []
        for pattern, description in AI_PATTERNS:
            matches = re.findall(pattern, visible_text)
            if matches:
                found.append({"description": description, "count": len(matches)})

        check = {
            "title": "Mentions d'IA / Chatbot",
            "status": "info",
            "severity": None,
            "ai_mentions_count": len(found),
            "findings": [],
        }

        if not found:
            check["findings"].append("ℹ️ Aucune mention d'IA ou de chatbot détectée sur la page")
        else:
            check["findings"].append(f"ℹ️ {len(found)} mention(s) d'IA détectée(s):")
            for item in found:
                check["findings"].append(f"    → {item['description']} ({item['count']} occurrence(s))")

            check["findings"].append(
                "    → Si l'IA traite des données personnelles: évaluation requise "
                "(RGPD Art. 22, AI Act)"
            )

        self.results["checks"]["ai_mentions"] = check

    # ── Verdict global ──────────────────────

    def _compute_verdict(self):
        checks = self.results["checks"]
        fails = [k for k, v in checks.items() if v.get("status") == "fail"]
        warns = [k for k, v in checks.items() if v.get("status") == "warn"]
        criticals = [k for k, v in checks.items() if v.get("severity") == "critical" or v.get("severity") == "high"]

        if fails:
            verdict = "NON-CONFORME"
            color = "🔴"
        elif len(warns) >= 2:
            verdict = "CONFORMITÉ PARTIELLE"
            color = "🟡"
        elif warns:
            verdict = "CONFORME AVEC RÉSERVES"
            color = "🟡"
        else:
            verdict = "CONFORME"
            color = "✅"

        # Dédupliquer les zones critiques (fails + warns haute sévérité)
        critical_areas = list(dict.fromkeys(fails + [k for k in warns if k in criticals]))

        self.results["verdict"] = {
            "label": verdict,
            "color": color,
            "fail_count": len(fails),
            "warn_count": len(warns),
            "critical_areas": critical_areas,
        }


# ──────────────────────────────────────────────
# Rapport
# ──────────────────────────────────────────────

def generate_report(results: dict, output_format: str = "text") -> str:
    if output_format == "json":
        return json.dumps(results, indent=2, ensure_ascii=False)

    # Format texte
    lines = []
    lines.append("=" * 60)
    lines.append("  CORTEX LEMAN — RAPPORT DE CONFORMITÉ WEB")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"  URL scannée: {results.get('url', 'N/A')}")
    lines.append(f"  Domaine:    {results.get('domain', 'N/A')}")
    lines.append(f"  Date:       {results.get('scan_date', 'N/A')[:19]}")
    lines.append(f"  Statut HTTP: {results.get('status_code', 'N/A')}")
    lines.append("")

    v = results.get("verdict", {})
    lines.append(f"  VERDICT: {v.get('color', '')} {v.get('label', 'N/A')}")
    lines.append(f"  Non-conformités critiques: {v.get('fail_count', 0)}")
    lines.append(f"  Points d'attention:        {v.get('warn_count', 0)}")
    lines.append("")
    lines.append("-" * 60)
    lines.append("")

    check_names = {
        "tls": "1. TLS / HTTPS",
        "trackers": "2. Trackers & Analytics",
        "cookie_consent": "3. Bandeau cookies / CMP",
        "forms": "4. Formulaires & PII",
        "security_headers": "5. Headers de sécurité",
        "privacy_policy": "6. Politique de confidentialité",
        "ai_mentions": "7. Mentions IA / Chatbot",
    }

    for key, title in check_names.items():
        check = results["checks"].get(key)
        if not check:
            continue
        lines.append(f"  {title}")
        lines.append(f"  Statut: {check['status'].upper()}")
        lines.append("")
        for finding in check["findings"]:
            lines.append(f"    {finding}")
        lines.append("")
        lines.append("-" * 60)
        lines.append("")

    lines.append("  Recommandations prioritaires:")
    lines.append("")
    for area in v.get("critical_areas", []):
        lines.append(f"    → Corriger: {area}")
    if not v.get("critical_areas"):
        lines.append("    → Aucune action critique requise")
    lines.append("")
    lines.append("=" * 60)

    return "\n".join(lines)


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Cortex Leman — Web Compliance Scanner"
    )
    parser.add_argument("url", help="URL à scanner (ex: https://exemple.ch)")
    parser.add_argument("--json", action="store_true", help="Sortie JSON")
    parser.add_argument("--output", "-o", help="Fichier de sortie", default=None)

    args = parser.parse_args()

    url = args.url
    if not url.startswith("http"):
        url = f"https://{url}"

    scanner = ComplianceScanner(url)
    results = scanner.run()

    if "error" in results:
        print(f"ERREUR: {results['error']}", file=sys.stderr)
        sys.exit(1)

    report = generate_report(results, "json" if args.json else "text")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Rapport sauvegardé: {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
