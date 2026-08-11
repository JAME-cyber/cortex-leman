#!/usr/bin/env python3
"""
anti_sycophancy.py — Protocole anti-sycophancie en 8 étapes.

Deux couches indépendantes:
  1. RULE-BASED (gratuit, immédiat): détecte patterns problematiques sans LLM
  2. LLM ADVERSARIAL (optionnel): envoie à un modèle différent pour critique structurée

Usage:
    # Analyse rule-based seulement (rapide, gratuit)
    echo "Texte à analyser" | python3 anti_sycophancy.py
    python3 anti_sycophancy.py --file analyse.txt

    # Avec LLM adversarial (coût ~$0.01-0.05)
    python3 anti_sycophancy.py --file analyse.txt --model openai/gpt-5.6-luna

    # Pipe depuis une commande
    hermes -z "Analyse X" --cli | python3 anti_sycophancy.py --model anthropic/claude-sonnet-4

Sortie: JSON structuré ou formaté terminal.

Auteur: Hermes Agent (prototype, 2026-07-27)
"""

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

# ═══════════════════════════════════════════════════════════════════════
# COUCHE 1: ANALYSE RULE-BASED (sans LLM)
# ═══════════════════════════════════════════════════════════════════════

# Patterns de langage promotionnel / sycophantique
PROMOTIONAL_MARKERS = [
    (r"\b(révolutionnaire|game.changer|disrupt|disruptif|paradigm.shift)\b", "promotionnel", 3),
    (r"\b(inédit|sans.précédent|historique|exceptionnel)\b", "superlatif_absolu", 2),
    (r"\b(toujours|jamais|tout.le.monde|personne|chacun)\b", "généralisation", 2),
    (r"\b(il.faut|on.doit|il.est.indispensable|il.est.essentiel)\b", "prescription_impérative", 1),
    (r"\b(évidemment|clairement|manifestement|bien.sûr|bien.évidemment)\b", "évidence_assumée", 2),
    (r"\b(cela.prouve|ce.qui.prouve|cela.démontre|cela.montre.clairement)\b", "preuve_affirmée", 3),
    (r"\b(seulement|juste|simplement|rien.que)\b.{0,30}\b(cliquer|essayer|adopter|utiliser)\b", "call_to_action_déguisé", 3),
]

# Patterns de faux dilemme
FALSE_DILEMMA_MARKERS = [
    r"\b(soit\b.{0,80}\bsoit\b|ou.bien.{0,80}ou.bien)",
    r"\b(la.seule.option|l'unique.solution|pas.d'autre.choix|inévitablement)\b",
    r"\b(si.vous.ne.{0,40}\balors)\b",
]

# Patterns de conflit d'intérêts potentiel
COI_HINTS = [
    (r"\b(notre|nos|ma|mon)\b.{0,30}\b(produit|service|solution|plateforme|startup|entreprise)\b", "promotion_produit_propre"),
    (r"\b(on.lance|je.lance|nous.lançons|nouveau|lancement)\b", "lancement_commercial"),
    (r"\binvest\w+|actionnaire|levée|série.[a-z]|valuation|IPO\b", "contexte_financier"),
    (r"\b(partenaire|sponsor|commanditaire|soutenu.par)\b", "sponsor_perçu"),
]

# Détection de chiffres non sourcés
NUMBER_PATTERN = re.compile(
    r"(?<!\w)(?:\$?\d{1,3}(?:[.,]\d{3})+(?:\.\d+)?|\$?\d+(?:\.\d+)?\s*(?:%|M€|M\$|Md\$|millions?|milliards?| billions?|x|fois|par.jour|par.heure|par.mois|/an|/jour|/mois|k|K))"
)


def extract_claims(text: str) -> list[dict]:
    """Extrait les phrases contenant des assertions factuelles."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    claims = []
    for i, sent in enumerate(sentences):
        sent = sent.strip()
        if len(sent) < 15:
            continue
        has_number = bool(NUMBER_PATTERN.search(sent))
        has_source = bool(re.search(r'\b(source|selon|d["\']après|rapporté.par|en.{0,10}\d{4}|https?://|étude|sondage|enquête|research|paper|article)\b', sent, re.IGNORECASE))
        is_factual = has_number or re.search(r'\b(est|sont|était|représente|atteint|a.atteint|totalise|génère|coûte|consomme)\b', sent, re.IGNORECASE) is not None

        if is_factual:
            claim_type = "fact" if has_number else "assertion"
            if has_number and not has_source:
                claim_type = "unsourced_number"
            claims.append({
                "index": i,
                "type": claim_type,
                "text": sent[:200],
                "has_number": has_number,
                "has_source": has_source,
            })
    return claims


def detect_promotional_language(text: str) -> list[dict]:
    """Détecte le langage promotionnel/sycophantique."""
    findings = []
    text_lower = text.lower()
    for pattern, label, severity in PROMOTIONAL_MARKERS:
        matches = re.finditer(pattern, text_lower)
        for m in matches:
            findings.append({
                "type": label,
                "severity": severity,
                "match": m.group()[:50],
                "position": m.start(),
            })
    return findings


def detect_false_dilemmas(text: str) -> list[dict]:
    """Détecte les faux dilemmes."""
    findings = []
    text_lower = text.lower()
    for pattern in FALSE_DILEMMA_MARKERS:
        for m in re.finditer(pattern, text_lower):
            findings.append({
                "type": "false_dilemma",
                "severity": 3,
                "match": m.group()[:80],
                "position": m.start(),
            })
    return findings


def detect_conflict_of_interest(text: str) -> list[dict]:
    """Détecte les indices de conflit d'intérêts."""
    findings = []
    text_lower = text.lower()
    for pattern, label in COI_HINTS:
        for m in re.finditer(pattern, text_lower):
            findings.append({
                "type": label,
                "severity": 3,
                "match": m.group()[:50],
                "position": m.start(),
            })
    return findings


def detect_unsourced_numbers(text: str) -> list[dict]:
    """Détecte les chiffres avancés sans source citée."""
    findings = []
    sentences = re.split(r'(?<=[.!?])\s+', text)
    for sent in sentences:
        numbers = NUMBER_PATTERN.findall(sent)
        if numbers:
            has_source = bool(re.search(r'\b(source|selon|d["\']après|https?://|étude|enquête|rapport|report|paper)\b', sent, re.IGNORECASE))
            if not has_source:
                findings.append({
                    "type": "unsourced_number",
                    "severity": 3,
                    "numbers": numbers[:5],
                    "context": sent.strip()[:150],
                })
    return findings


def rule_based_analysis(text: str) -> dict:
    """Analyse rule-based complète — sans LLM."""
    claims = extract_claims(text)
    promotional = detect_promotional_language(text)
    dilemmas = detect_false_dilemmas(text)
    coi = detect_conflict_of_interest(text)
    unsourced = detect_unsourced_numbers(text)

    # Score de risque (0-100)
    risk_score = 0
    risk_score += min(30, len(promotional) * 3)
    risk_score += min(25, len(dilemmas) * 8)
    risk_score += min(30, len(coi) * 10)
    risk_score += min(20, len(unsourced) * 4)
    unsourced_claims = [c for c in claims if c["type"] == "unsourced_number"]
    risk_score += min(15, len(unsourced_claims) * 5)
    risk_score = min(100, risk_score)

    if risk_score >= 70:
        risk_level = "CRITICAL"
    elif risk_score >= 40:
        risk_level = "WARNING"
    elif risk_score >= 15:
        risk_level = "CAUTION"
    else:
        risk_level = "LOW"

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "claims_extracted": len(claims),
        "unsourced_claims": len(unsourced_claims),
        "findings": {
            "promotional_language": promotional,
            "false_dilemmas": dilemmas,
            "conflict_of_interest": coi,
            "unsourced_numbers": unsourced,
        },
        "claims": claims,
    }


# ═══════════════════════════════════════════════════════════════════════
# COUCHE 2: LLM ADVERSARIAL (optionnel)
# ═══════════════════════════════════════════════════════════════════════

ADVERSARIAL_PROMPT = """Tu es un critique féroce et indépendant. Ta mission est de démolir l'analyse ci-dessous — pas par malice, mais par rigueur.

PROTOCOLE EN 8 ÉTAPES (applique TOUTES):

1. SÉPARATION: Classe chaque claim comme: [FAIT], [INTERPRÉTATION], ou [RECOMMANDATION].

2. OBJECTIONS FORTEES: Produis au moins 2 objections qui affaiblissent ou invalident les claims centraux. Sois spécifique.

3. HYPOTHÈSES FRAGILES: Identifie les suppositions non démontrées sur lesquelles le raisonnement repose.

4. DONNÉES MANQUANTES: Quelles informations vérifiables manque-t-il pour valider les conclusions?

5. CONSÉQUENCES D'ERREUR: Si les claims sont faux, quelles sont les conséquences concrètes (financières, réputationnelles, légales)?

6. CONTRAINTES DURES: Y a-t-il des règles légales, réglementaires, ou éthiques qui s'appliquent et ne sont pas mentionnées?

7. NIVEAU DE CONFIANCE: Pour chaque claim central, attribue: ÉLEVÉ / MOYEN / FAIBLE / INDÉTERMINÉ.

8. VERDICT: Peux-tu confirmer cette analyse? Si non, dis-le explicitement.

RÈGLES:
- Ne flatte JAMAIS. Ne dis pas "bonne analyse" ou "point intéressant".
- Si un chiffre est cité sans source, traite-le comme NON CRÉDIBLE.
- Si l'auteur a un intérêt financier dans la conclusion, signale-le.
- Si tu n'as pas assez d'informations pour conclure, REFUSE de conclure.

Réponds en JSON valide avec cette structure exacte:
{
  "claims_classified": [{"text": "...", "type": "FAIT|INTERPRÉTATION|RECOMMANDATION", "confidence": "ÉLEVÉ|MOYEN|FAIBLE|INDÉTERMINÉ"}],
  "objections": [{"claim": "...", "objection": "...", "severity": 1-5}],
  "fragile_assumptions": ["...", "..."],
  "missing_data": ["...", "..."],
  "error_consequences": ["...", "..."],
  "hard_constraints": ["...", "..."],
  "conflict_of_interest": "none detected" | "description",
  "overall_confidence": "ÉLEVÉ | MOYEN | FAIBLE | INDÉTERMINÉ",
  "verdict": "confirmé | partiellement validé | invalidé | données insuffisantes",
  "refusal_to_conclude": true | false,
  "summary": "2-3 phrases maximum"
}
"""


def call_llm_adversarial(text: str, model: str, api_key: str, base_url: str = "https://openrouter.ai/api/v1") -> dict:
    """Appelle un LLM avec le prompt adversarial."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": ADVERSARIAL_PROMPT},
            {"role": "user", "content": f"ANALYSE À CRITIQUER:\n\n{text}"},
        ],
        "temperature": 0.3,
        "max_tokens": 4000,
    }

    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode())
            content = result["choices"][0]["message"]["content"]
            usage = result.get("usage", {})

            # Essayer de parser le JSON
            try:
                # Strip markdown code fences si présents
                content_clean = content.strip()
                if content_clean.startswith("```"):
                    content_clean = re.sub(r'^```(?:json)?\s*', '', content_clean)
                    content_clean = re.sub(r'\s*```$', '', content_clean)
                parsed = json.loads(content_clean)
                parsed["_usage"] = usage
                return parsed
            except json.JSONDecodeError:
                return {
                    "error": "JSON parse failed",
                    "raw_response": content[:2000],
                    "_usage": usage,
                }
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500]
        return {"error": f"HTTP {e.code}", "detail": body}
    except Exception as e:
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════════════
# OUTPUT FORMATTERS
# ═══════════════════════════════════════════════════════════════════════

def print_terminal(rule_analysis: dict, llm_analysis: dict = None, model: str = None):
    ra = rule_analysis
    risk = ra["risk_level"]
    emoji = {"CRITICAL": "🚨", "WARNING": "⚠️", "CAUTION": "⚡", "LOW": "✅"}
    e = emoji.get(risk, "❓")

    print("=" * 70)
    print(f"  {e} ANTI-SYCOPHANCIE — Score: {ra['risk_score']}/100 ({risk})")
    print("=" * 70)

    # Rule-based findings
    f = ra["findings"]
    print(f"\n📋 COUCHE 1: ANALYSE AUTOMATISÉE (rule-based)")
    print(f"   Claims extraits:      {ra['claims_extracted']}")
    print(f"   Claims non sourcés:   {ra['unsourced_claims']}")

    if f["promotional_language"]:
        print(f"\n   ⚡ Langage promotionnel ({len(f['promotional_language'])}):")
        for item in f["promotional_language"][:5]:
            print(f"      [{item['severity']}] {item['type']}: \"{item['match']}\"")

    if f["false_dilemmas"]:
        print(f"\n   ⚡ Faux dilemmes ({len(f['false_dilemmas'])}):")
        for item in f["false_dilemmas"][:3]:
            print(f"      \"{item['match'][:70]}\"")

    if f["conflict_of_interest"]:
        print(f"\n   ⚠️ Conflit d'intérêts potentiel ({len(f['conflict_of_interest'])}):")
        for item in f["conflict_of_interest"][:3]:
            print(f"      {item['type']}: \"{item['match']}\"")

    if f["unsourced_numbers"]:
        print(f"\n   ⚠️ Chiffres non sourcés ({len(f['unsourced_numbers'])}):")
        for item in f["unsourced_numbers"][:5]:
            print(f"      {item['numbers']} → \"{item['context'][:80]}\"")

    if ra["risk_score"] < 15:
        print("\n   Aucun pattern problematique majeur détecté.")

    # LLM adversarial
    if llm_analysis:
        print(f"\n📋 COUCHE 2: CRITIQUE LLM ADVERSARIAL ({model})")
        print("-" * 70)

        if "error" in llm_analysis:
            print(f"   ❌ Erreur: {llm_analysis['error']}")
            if "detail" in llm_analysis:
                print(f"   {llm_analysis['detail'][:200]}")
        else:
            verdict = llm_analysis.get("verdict", "?")
            confidence = llm_analysis.get("overall_confidence", "?")
            refusal = llm_analysis.get("refusal_to_conclude", False)
            v_emoji = "✅" if "confirm" in verdict else "⚠️" if "partiel" in verdict else "❌" if "invalid" in verdict else "❓"

            print(f"\n   {v_emoji} Verdict: {verdict}")
            print(f"   Confiance globale: {confidence}")
            if refusal:
                print(f"   🚫 Refus de conclure: données insuffisantes")

            coi = llm_analysis.get("conflict_of_interest", "none detected")
            if coi != "none detected":
                print(f"\n   ⚠️ Conflit d'intérêts: {coi}")

            objections = llm_analysis.get("objections", [])
            if objections:
                print(f"\n   🎯 Objections ({len(objections)}):")
                for obj in objections[:5]:
                    sev = obj.get("severity", "?")
                    print(f"      [{sev}/5] {obj.get('objection', '')[:100]}")

            fragile = llm_analysis.get("fragile_assumptions", [])
            if fragile:
                print(f"\n   💭 Hypothèses fragiles ({len(fragile)}):")
                for a in fragile[:5]:
                    print(f"      • {a[:100]}")

            missing = llm_analysis.get("missing_data", [])
            if missing:
                print(f"\n   ❓ Données manquantes ({len(missing)}):")
                for m in missing[:5]:
                    print(f"      • {m[:100]}")

            consequences = llm_analysis.get("error_consequences", [])
            if consequences:
                print(f"\n   💥 Conséquences d'erreur ({len(consequences)}):")
                for c in consequences[:3]:
                    print(f"      • {c[:100]}")

            constraints = llm_analysis.get("hard_constraints", [])
            if constraints:
                print(f"\n   ⚖️ Contraintes dures ({len(constraints)}):")
                for c in constraints[:3]:
                    print(f"      • {c[:100]}")

            summary = llm_analysis.get("summary", "")
            if summary:
                print(f"\n   📝 Résumé: {summary}")

            usage = llm_analysis.get("_usage", {})
            if usage:
                in_tok = usage.get("prompt_tokens", 0)
                out_tok = usage.get("completion_tokens", 0)
                print(f"\n   💰 Tokens: {in_tok:,} in / {out_tok:,} out")

    print()


def main():
    parser = argparse.ArgumentParser(description="Anti-sycophancie — protocole de critique en 8 étapes")
    parser.add_argument("--file", "-f", type=str, help="Fichier à analyser")
    parser.add_argument("--model", "-m", type=str, default=None, help="Modèle LLM pour critique adversariale (ex: openai/gpt-5.6-luna)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--stdin", action="store_true", help="Lire depuis stdin")
    args = parser.parse_args()

    # Input
    if args.file:
        with open(args.file, "r") as f:
            text = f.read()
    elif args.stdin or not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        print("Erreur: fournir --file, --stdin, ou pipe", file=sys.stderr)
        sys.exit(1)

    if not text.strip():
        print("Erreur: texte vide", file=sys.stderr)
        sys.exit(1)

    # Couche 1: rule-based
    rule_result = rule_based_analysis(text)

    # Couche 2: LLM adversarial (optionnel)
    llm_result = None
    model_used = None
    if args.model:
        model_used = args.model
        api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("GLM_API_KEY")
        if not api_key:
            print("Erreur: OPENROUTER_API_KEY ou GLM_API_KEY non trouvé", file=sys.stderr)
            sys.exit(1)

        # Si le modèle commence par "glm", utiliser l'API Z.ai
        base_url = "https://openrouter.ai/api/v1"
        if "glm" in args.model.lower() and os.environ.get("GLM_API_KEY"):
            base_url = "https://api.z.ai/api/coding/paas/v4"
            api_key = os.environ.get("GLM_API_KEY")

        llm_result = call_llm_adversarial(text, args.model, api_key, base_url)

    if args.json:
        output = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "rule_based": rule_result,
        }
        if llm_result is not None:
            output["llm_adversarial"] = {
                "model": model_used,
                "result": llm_result,
            }
        print(json.dumps(output, indent=2, ensure_ascii=False, default=str))
    else:
        print_terminal(rule_result, llm_result, model_used)


if __name__ == "__main__":
    main()
