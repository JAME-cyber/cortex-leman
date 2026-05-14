#!/usr/bin/env python3
"""
CORTEX LEMAN v5 — Napkin Math RGPD
=====================================
Calculateur de coût de non-conformité intégré au Médiateur.

Estime en temps réel le coût financier d'une violation RGPD/AI Act
pour aider les DPO et décideurs à prioriser les actions de mise en conformité.

Usage:
  python3 napkin_math.py --vertical sante --data-types sante,biometrique --persons 500
  python3 napkin_math.py --vertical banque --intent malveillance --persons 10000
  python3 napkin_math.py --vertical agent-ia --action deploiement_sans_audit
  python3 napkin_math.py --report  # Rapport toutes verticales
"""

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

# ── Barème des amendes ─────────────────────────────────────────

# RGPD — Article 83
RGPD_TIER1_MAX = 10_000_000       # 10M EUR ou 2% CA global
RGPD_TIER2_MAX = 20_000_000       # 20M EUR ou 4% CA global

# AI Act — Article 99
AI_ACT_TIER1_MAX = 15_000_000     # 15M EUR ou 3% CA (obligations transparence)
AI_ACT_TIER2_MAX = 35_000_000     # 35M EUR ou 7% CA (pratiques interdites)

# LPD Suisse
LPD_MAX_CHF = 250_000             # 250K CHF (art. 60 LPerD)

# Secret professionnel suisse
SECRET_PROF_AMENDE_CHF = 20_000   # Art. 321 CP —jusqu'à 3 ans prison
SECRET_PROF_PRISON_MAX = 3        # Années

# CNIL — Barème pratique (moyenne des sanctions 2023-2025)
CNIL_AVERAGE_FINE_LOW = 5_000     # Notification tardive
CNIL_AVERAGE_FINE_MID = 150_000   # Manquement grave
CNIL_AVERAGE_FINE_HIGH = 1_500_000  # Violation massive

# FDPIC Suisse
FDPIC_MAX_CHF = 250_000

# ── Modèles de données ─────────────────────────────────────────

@dataclass
class NonComplianceEstimate:
    """Estimation de coût de non-conformité."""
    vertical: str
    risk_score: float                         # 0-1
    severity: str                             # CRITICAL, HIGH, MEDIUM, LOW

    # Coûts estimés (EUR)
    amende_rgpd: int = 0
    amende_ai_act: int = 0
    amende_lpd_chf: int = 0
    frais_juridiques: int = 0
    notification_personnes: int = 0
    remediation_technique: int = 0
    perte_reputation: int = 0
    arret_activite_jours: int = 0
    perte_revenus_arret: int = 0

    # Totaux
    cout_total_eur: int = 0
    cout_total_chf: int = 0

    # Contexte
    personnes_affectees: int = 0
    types_donnees: list = None
    intention: str = "negligence"
    references: list = None

    # Recommandations
    recommandations: list = None

    def __post_init__(self):
        if self.types_donnees is None:
            self.types_donnees = []
        if self.references is None:
            self.references = []
        if self.recommandations is None:
            self.recommandations = []


# ── Calculateur ─────────────────────────────────────────────────

# Sensibilité des données (multiplier risk_score)
DATA_SENSITIVITY = {
    "sante": 1.4,
    "biometrique": 1.5,
    "genetique": 1.6,
    "financiere": 1.3,
    "judiciaire": 1.3,
    "enfant": 1.5,
    "ethnique": 1.4,
    "religion": 1.3,
    "orientation": 1.3,
    "localisation": 1.1,
    "identification": 1.0,
    "contact": 0.8,
    "navigation": 0.6,
}

# Base risk par verticale
VERTICAL_BASE_RISK = {
    "sante": 0.70,
    "banque": 0.65,
    "avocat": 0.75,
    "rh": 0.55,
    "comptable": 0.35,
    "startup": 0.30,
    "agent-ia": 0.40,
}

# Intention modifier
INTENT_MODIFIER = {
    "negligence": 0.10,
    "erreur": 0.05,
    "malveillance": 0.25,
    "force_majeure": 0.00,
}

# Coût notification par personne (RGPD Art. 33-34)
COST_NOTIFICATION_PER_PERSON = 5  # EUR

# Coût remédiation technique par incident
BASE_REMEDIATION = {
    "sante": 50_000,
    "banque": 80_000,
    "avocat": 40_000,
    "rh": 30_000,
    "comptable": 20_000,
    "startup": 15_000,
    "agent-ia": 25_000,
}

# Frais juridiques par incident
LEGAL_FEES = {
    "CRITICAL": 100_000,
    "HIGH": 50_000,
    "MEDIUM": 20_000,
    "LOW": 5_000,
}

# Perte de réputation estimée (en % du CA annuel moyen)
REPUTATION_LOSS_PCT = {
    "sante": 0.08,
    "banque": 0.10,
    "avocat": 0.15,
    "rh": 0.06,
    "comptable": 0.05,
    "startup": 0.04,
    "agent-ia": 0.05,
}

# CA moyen estimé par type de client (EUR/an)
AVERAGE_REVENUE = {
    "sante": 2_000_000,
    "banque": 10_000_000,
    "avocat": 1_500_000,
    "rh": 3_000_000,
    "comptable": 800_000,
    "startup": 500_000,
    "agent-ia": 2_000_000,
}


def calculate_risk_score(
    vertical: str,
    data_types: list[str],
    persons: int,
    intent: str,
    context: dict = None,
) -> float:
    """Calculer le score de risque 0-1."""
    base = VERTICAL_BASE_RISK.get(vertical, 0.3)

    # Adjust for data sensitivity
    max_sensitivity = 1.0
    for dt in data_types:
        max_sensitivity = max(max_sensitivity, DATA_SENSITIVITY.get(dt.lower(), 1.0))

    # Adjust for number of persons
    persons_mod = min(0.2, persons / 100_000)

    # Adjust for intent
    intent_mod = INTENT_MODIFIER.get(intent, 0.05)

    score = base * max_sensitivity + persons_mod + intent_mod

    # Context adjustments
    if context:
        if context.get("consentement_obtenu"):
            score -= 0.1
        if context.get("chiffrement_actif"):
            score -= 0.05
        if context.get("dpia_realisee"):
            score -= 0.1
        if context.get("deja_conforme"):
            score -= 0.15
        if context.get("reoffense"):
            score += 0.2

    return max(0.0, min(1.0, score))


def calculate_estimate(
    vertical: str,
    data_types: list[str],
    persons: int = 100,
    intent: str = "negligence",
    context: dict = None,
) -> NonComplianceEstimate:
    """Calculer l'estimation complète de non-conformité."""

    risk_score = calculate_risk_score(vertical, data_types, persons, intent, context)

    # Severity
    if risk_score >= 0.8:
        severity = "CRITICAL"
    elif risk_score >= 0.6:
        severity = "HIGH"
    elif risk_score >= 0.3:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    # ── Amende RGPD ──
    if severity in ("CRITICAL", "HIGH"):
        # Tier 2: 4% CA ou 20M
        ca = AVERAGE_REVENUE.get(vertical, 1_000_000)
        amende_rgpd = min(int(ca * 0.04 * risk_score), RGPD_TIER2_MAX)
    elif severity == "MEDIUM":
        # Tier 1: 2% CA ou 10M
        ca = AVERAGE_REVENUE.get(vertical, 1_000_000)
        amende_rgpd = min(int(ca * 0.02 * risk_score), RGPD_TIER1_MAX)
    else:
        amende_rgpd = CNIL_AVERAGE_FINE_LOW

    # ── Amende AI Act ──
    sensitive_data = {"sante", "biometrique", "genetique", "enfant"}
    if any(dt.lower() in sensitive_data for dt in data_types):
        amende_ai_act = min(int(AI_ACT_TIER2_MAX * risk_score * 0.5), AI_ACT_TIER2_MAX)
    elif vertical == "agent-ia":
        amende_ai_act = min(int(AI_ACT_TIER1_MAX * risk_score * 0.3), AI_ACT_TIER1_MAX)
    else:
        amende_ai_act = 0

    # ── Amende LPD Suisse ──
    amende_lpd = int(FDPIC_MAX_CHF * risk_score) if risk_score > 0.5 else 0

    # ── Frais annexes ──
    frais_juridiques = LEGAL_FEES.get(severity, 5_000)
    notification = persons * COST_NOTIFICATION_PER_PERSON
    remediation = int(BASE_REMEDIATION.get(vertical, 20_000) * risk_score)
    ca = AVERAGE_REVENUE.get(vertical, 1_000_000)
    perte_reputation = int(ca * REPUTATION_LOSS_PCT.get(vertical, 0.05) * risk_score)

    # ── Arrêt d'activité ──
    arret_jours = 0
    if severity == "CRITICAL":
        arret_jours = 30
    elif severity == "HIGH":
        arret_jours = 7
    perte_arret = int(ca * (arret_jours / 365))

    # ── Total ──
    total_eur = amende_rgpd + amende_ai_act + frais_juridiques + notification + remediation + perte_reputation + perte_arret
    total_chf = amende_lpd  # Additional Swiss costs

    # ── References ──
    refs = ["RGPD Art. 83 (amendes)"]
    if amende_ai_act > 0:
        refs.append("AI Act Art. 99 (amendes)")
    if amende_lpd > 0:
        refs.append("LPerD Art. 60 (amendes suisses)")
    if any(dt.lower() in sensitive_data for dt in data_types):
        refs.append("RGPD Art. 9 (données sensibles)")

    # ── Recommandations ──
    recos = []
    if risk_score > 0.7:
        recos.append("🔴 URGENT: Nommer un DPO et réaliser une AIPD/DPIA immédiatement")
    if "sante" in [dt.lower() for dt in data_types]:
        recos.append("🩺 Activer le Mode Haute Protection (Ollama local, zero réseau)")
    if "biometrique" in [dt.lower() for dt in data_types]:
        recos.append("🔐 Consentement biometrique explicite obligatoire (RGPD Art. 9(2)(a))")
    if vertical == "agent-ia":
        recos.append("🤖 Audit AI Act obligatoire avant déploiement (Art. 6-7)")
    if persons > 1000:
        recos.append("📢 Plan de notification de masse obligatoire (RGPD Art. 33-34)")
    if intent == "malveillance":
        recos.append("⚖️ Risque pénal — consultation avocat urgente")
    recos.append("📋 Audit Cortex Leman recommandé — diagnostic en 48h")

    return NonComplianceEstimate(
        vertical=vertical,
        risk_score=round(risk_score, 3),
        severity=severity,
        amende_rgpd=amende_rgpd,
        amende_ai_act=amende_ai_act,
        amende_lpd_chf=amende_lpd,
        frais_juridiques=frais_juridiques,
        notification_personnes=notification,
        remediation_technique=remediation,
        perte_reputation=perte_reputation,
        arret_activite_jours=arret_jours,
        perte_revenus_arret=perte_arret,
        cout_total_eur=total_eur,
        cout_total_chf=total_chf,
        personnes_affectees=persons,
        types_donnees=data_types,
        intention=intent,
        references=refs,
        recommandations=recos,
    )


def format_estimate(est: NonComplianceEstimate) -> str:
    """Formater l'estimation en rapport lisible."""
    severity_emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}

    lines = [
        "═" * 60,
        f"  NAPKIN MATH RGPD — Cortex Leman v5",
        "═" * 60,
        "",
        f"  Verticale:        {est.vertical}",
        f"  Score de risque:  {est.risk_score:.1%}  {severity_emoji.get(est.severity, '')} {est.severity}",
        f"  Personnes:        {est.personnes_affectees:,}",
        f"  Données:          {', '.join(est.types_donnees) or 'non spécifié'}",
        f"  Intention:        {est.intention}",
        "",
        "─" * 40,
        "  DÉTAIL DES COÛTS (EUR)",
        "─" * 40,
        f"  Amende RGPD:              {est.amende_rgpd:>12,} €",
        f"  Amende AI Act:             {est.amende_ai_act:>12,} €",
        f"  Frais juridiques:          {est.frais_juridiques:>12,} €",
        f"  Notification personnes:    {est.notification_personnes:>12,} €",
        f"  Remédiation technique:     {est.remediation_technique:>12,} €",
        f"  Perte réputation:          {est.perte_reputation:>12,} €",
    ]

    if est.arret_activite_jours > 0:
        lines.append(f"  Arrêt activité ({est.arret_activite_jours}j):   {est.perte_revenus_arret:>12,} €")

    lines += [
        "─" * 40,
        f"  TOTAL EUR:                {est.cout_total_eur:>12,} €",
    ]

    if est.amende_lpd_chf > 0:
        lines.append(f"  + Amende LPD Suisse:      {est.amende_lpd_chf:>12,} CHF")

    lines += [
        "",
        "─" * 40,
        "  RÉFÉRENCES LÉGALES",
        "─" * 40,
    ]
    for ref in est.references:
        lines.append(f"  • {ref}")

    lines += [
        "",
        "─" * 40,
        "  RECOMMANDATIONS",
        "─" * 40,
    ]
    for reco in est.recommandations:
        lines.append(f"  {reco}")

    lines += [
        "",
        "═" * 60,
        "  cortexleman.ch · Excellence by Design",
        "═" * 60,
    ]

    return "\n".join(lines)


# ── Main ────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Napkin Math RGPD — Cortex Leman v5")
    parser.add_argument("--vertical", required=True,
                        choices=["comptable", "avocat", "sante", "banque", "rh", "startup", "agent-ia"])
    parser.add_argument("--data-types", default="identification",
                        help="Types de données séparés par virgule (sante,biometrique,financiere...)")
    parser.add_argument("--persons", type=int, default=100,
                        help="Nombre de personnes affectées")
    parser.add_argument("--intent", default="negligence",
                        choices=["negligence", "erreur", "malveillance", "force_majeure"])
    parser.add_argument("--report", action="store_true",
                        help="Rapport toutes verticales")
    parser.add_argument("--json", action="store_true",
                        help="Sortie JSON")

    args = parser.parse_args()

    data_types = [dt.strip() for dt in args.data_types.split(",")]

    if args.report:
        print("\n📊 RAPPORT NAPKIN MATH — TOUTES VERTICALES\n")
        for v in ["sante", "banque", "avocat", "rh", "comptable", "startup", "agent-ia"]:
            est = calculate_estimate(v, data_types=["identification"], persons=100)
            emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}
            print(f"  {emoji.get(est.severity, '⚪')} {v:12s}  risque={est.risk_score:.0%}  "
                  f"coût={est.cout_total_eur:>10,} €  sévérité={est.severity}")
        print()
        return

    est = calculate_estimate(
        vertical=args.vertical,
        data_types=data_types,
        persons=args.persons,
        intent=args.intent,
    )

    if args.json:
        from dataclasses import asdict
        print(json.dumps(asdict(est), indent=2, ensure_ascii=False))
    else:
        print(format_estimate(est))


if __name__ == "__main__":
    main()
