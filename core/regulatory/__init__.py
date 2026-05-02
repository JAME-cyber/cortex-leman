"""
Cortex Leman v5 — Échéancier Réglementaire Vivant
Calendrier des obligations FR + CH, auto-génération d'intentions.
"""
from datetime import datetime, date, timedelta
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class RegulatoryDeadline:
    """Échéance réglementaire"""
    id: str
    label: str
    description: str
    verticals: list[str]
    jurisdiction: str  # FR, CH, FR-CH
    frequency: str  # mensuel, trimestriel, annuel, ponctuel
    severity: str  # critical, high, medium
    month: Optional[int] = None  # mois pour annuel
    day: Optional[int] = None  # jour dans le mois
    quarter: Optional[int] = None  # trimestre pour trimestriel
    month_day: Optional[int] = None  # jour du mois pour mensuel
    reference: str = ""
    auto_intention: bool = True  # génère une intention automatiquement


# ── Base de connaissances réglementaire FR-CH ──
DEADLINES: list[RegulatoryDeadline] = [
    # === COMPTABLE ===
    RegulatoryDeadline(
        id="comptable-tva-mensuelle",
        label="Déclaration TVA mensuelle",
        description="Déclaration de TVA auprès de l'administration fiscale. Mensuel si CA > 4M€.",
        verticals=["comptable"], jurisdiction="FR", frequency="mensuel",
        severity="critical", month_day=19,
        reference="Art. 287 CGI — Déclaration de TVA",
    ),
    RegulatoryDeadline(
        id="comptable-tva-trimestrielle",
        label="Déclaration TVA trimestrielle",
        description="Déclaration de TVA trimestrielle pour CA < 4M€.",
        verticals=["comptable"], jurisdiction="FR", frequency="trimestriel",
        severity="high", quarter=1, month_day=19,
        reference="Art. 287 CGI",
    ),
    RegulatoryDeadline(
        id="comptable-tva-suisse",
        label="Déclaration TVA suisse",
        description="Déclaration TVA trimestrielle auprès de l'AFC.",
        verticals=["comptable"], jurisdiction="CH", frequency="trimestriel",
        severity="critical", quarter=1, month_day=60,  # 60 jours après fin de trimestre
        reference="LTVA Art. 53",
    ),
    RegulatoryDeadline(
        id="comptable-bilan-annuel",
        label="Dépôt bilan annuel",
        description="Dépôt des comptes annuels au greffe du tribunal de commerce.",
        verticals=["comptable"], jurisdiction="FR", frequency="annuel",
        severity="critical", month=7, day=31,
        reference="Art. L232-20 Code commerce",
    ),
    RegulatoryDeadline(
        id="comptable-impot-societes",
        label="Déclaration IS/IPP",
        description="Déclaration d'impôt sur les sociétés ou revenus. Mai pour IS.",
        verticals=["comptable"], jurisdiction="FR", frequency="annuel",
        severity="critical", month=5, day=20,
        reference="Art. 223 CGI",
    ),
    RegulatoryDeadline(
        id="comptable-impot-suisse",
        label="Déclaration d'impôt cantonal/fédéral",
        description="Déclaration fiscale suisse. Date varie par canton (mars-septembre).",
        verticals=["comptable"], jurisdiction="CH", frequency="annuel",
        severity="critical", month=3, day=31,
        reference="LIFD Art. 65",
    ),
    RegulatoryDeadline(
        id="comptable-dsn",
        label="DSN (Déclaration Sociale Nominative)",
        description="Déclaration mensuelle obligatoire pour les employeurs.",
        verticals=["comptable"], jurisdiction="FR", frequency="mensuel",
        severity="critical", month_day=15,
        reference="Code de la sécurité sociale Art. R133-5",
    ),

    # === AVOCAT ===
    RegulatoryDeadline(
        id="avocat-cnpaj",
        label="Déclaration CNPAJ (ou PAJ)",
        description="Déclaration des paies et cotisations au barreau.",
        verticals=["avocat"], jurisdiction="FR", frequency="annuel",
        severity="high", month=1, day=31,
        reference="Décret 91-1197 Art. 93",
    ),
    RegulatoryDeadline(
        id="avocat-carpa",
        label="Compte CARPA — Relevé trimestriel",
        description="Relevé des fonds détenus sur le compte CARPA.",
        verticals=["avocat"], jurisdiction="FR", frequency="trimestriel",
        severity="high", quarter=1, month_day=30,
        reference="Décret 91-1197 Art. 107",
    ),
    RegulatoryDeadline(
        id="avocat-rc-pro",
        label="Renouvellement RC Pro",
        description="Renouvellement de l'assurance responsabilité civile professionnelle.",
        verticals=["avocat"], jurisdiction="FR-CH", frequency="annuel",
        severity="high", month=1, day=15,
        reference="Décret 91-1197 Art. 108",
    ),

    # === SANTÉ ===
    RegulatoryDeadline(
        id="sante-certification-hds",
        label="Audit certification HDS",
        description="Audit annuel de conformité HDS pour l'hébergement de données de santé.",
        verticals=["sante"], jurisdiction="FR", frequency="annuel",
        severity="critical", month=12, day=31,
        reference="Arrêté HDS 24/01/2019",
    ),
    RegulatoryDeadline(
        id="sante-cnil-declaration",
        label="Déclaration CNIL — Activité IA",
        description="Déclaration annuelle des traitements automatisés de données de santé.",
        verticals=["sante"], jurisdiction="FR", frequency="annuel",
        severity="high", month=6, day=30,
        reference="RGPD Art. 36 — AIPD",
    ),
    RegulatoryDeadline(
        id="sante-lpd-suisse",
        label="Rapport LPD — Protection des données",
        description="Rapport annuel de conformité LPD (Suisse).",
        verticals=["sante"], jurisdiction="CH", frequency="annuel",
        severity="high", month=9, day=30,
        reference="LPD Art. 22-24",
    ),

    # === BANQUE ===
    RegulatoryDeadline(
        id="banque-finma-reporting",
        label="Reporting FINMA trimestriel",
        description="Rapport trimestriel à la FINMA sur les risques et la conformité.",
        verticals=["banque"], jurisdiction="CH", frequency="trimestriel",
        severity="critical", quarter=1, month_day=45,
        reference="FINMA Circ. 2016/7",
    ),
    RegulatoryDeadline(
        id="banque-acpr-reporting",
        label="Reporting ACPR",
        description="Rapport trimestriel à l'ACPR (France).",
        verticals=["banque"], jurisdiction="FR", frequency="trimestriel",
        severity="critical", quarter=1, month_day=30,
        reference="Code monétaire Art. L612-1",
    ),
    RegulatoryDeadline(
        id="banque-kyc-review",
        label="Revue KYC annuelle",
        description="Revue annuelle des dossiers clients KYC. Obligatoire FINMA + ACPR.",
        verticals=["banque"], jurisdiction="FR-CH", frequency="annuel",
        severity="high", month=12, day=31,
        reference="FINMA Circ. 2016/7 Art. 14",
    ),

    # === RH ===
    RegulatoryDeadline(
        id="rh-dsn-mensuelle",
        label="DSN mensuelle",
        description="Déclaration Sociale Nominative — obligatoire tous les 5 ou 15 du mois.",
        verticals=["rh", "comptable"], jurisdiction="FR", frequency="mensuel",
        severity="critical", month_day=15,
        reference="Code de la sécurité sociale Art. R133-5",
    ),
    RegulatoryDeadline(
        id="rh-mass-salarial",
        label="Déclaration Masse Salariale (Suisse)",
        description="Déclaration annuelle des salaires à l'AFC.",
        verticals=["rh"], jurisdiction="CH", frequency="annuel",
        severity="high", month=1, day=31,
        reference="LTVA Art. 53 + LAA Art. 52",
    ),
    RegulatoryDeadline(
        id="rh-index-egalite",
        label="Index Égalité Professionnelle",
        description="Calcul et publication de l'index égalité F/H. Obligatoire si ≥50 salariés.",
        verticals=["rh"], jurisdiction="FR", frequency="annuel",
        severity="high", month=3, day=1,
        reference="Loi Rixain Art. 13",
    ),
    RegulatoryDeadline(
        id="rh-ai-act-register",
        label="Registre IA — AI Act",
        description="Mise à jour du registre des systèmes d'IA utilisés en RH.",
        verticals=["rh"], jurisdiction="FR", frequency="annuel",
        severity="high", month=9, day=1,
        reference="AI Act Art. 49 — Documentation",
    ),

    # === STARTUP ===
    RegulatoryDeadline(
        id="startup-rgpd-aipd",
        label="AIPD (DPIA) annuelle",
        description="Analyse d'Impact sur la Protection des Données si profiling.",
        verticals=["startup"], jurisdiction="FR", frequency="annuel",
        severity="high", month=6, day=30,
        reference="RGPD Art. 35",
    ),
    RegulatoryDeadline(
        id="startup-cnil-registration",
        label="Enregistrement CNIL — Traitements IA",
        description="Déclaration des nouveaux traitements IA. Obligatoire avant mise en production.",
        verticals=["startup"], jurisdiction="FR", frequency="annuel",
        severity="high", month=1, day=31,
        reference="RGPD Art. 33",
    ),
    RegulatoryDeadline(
        id="startup-ai-act-classification",
        label="Classification AI Act",
        description="Revue annuelle de la classification des systèmes IA selon l'AI Act.",
        verticals=["startup"], jurisdiction="FR", frequency="annuel",
        severity="critical", month=12, day=31,
        reference="AI Act Art. 6",
    ),

    # === TRANSVERSAL ===
    RegulatoryDeadline(
        id="all-rgpd-audit",
        label="Audit RGPD annuel",
        description="Revue annuelle de conformité RGPD. Obligatoire pour DPO.",
        verticals=["comptable", "avocat", "sante", "banque", "startup", "rh"],
        jurisdiction="FR", frequency="annuel",
        severity="high", month=5, day=25,
        reference="RGPD Art. 39 — Mission du DPO",
    ),
    RegulatoryDeadline(
        id="all-lpd-audit",
        label="Audit LPD annuel (Suisse)",
        description="Revue annuelle de conformité LPD.",
        verticals=["comptable", "avocat", "sante", "banque", "rh"],
        jurisdiction="CH", frequency="annuel",
        severity="high", month=9, day=30,
        reference="LPD Art. 22",
    ),
]


def get_calendar(
    vertical: Optional[str] = None,
    jurisdiction: Optional[str] = None,
    months_ahead: int = 6,
) -> list[dict]:
    """Générer l'échéancier réglementaire pour les N prochains mois"""
    today = date.today()
    results = []

    for d in DEADLINES:
        # Filter
        if vertical and vertical not in d.verticals:
            continue
        if jurisdiction and d.jurisdiction != jurisdiction and d.jurisdiction != "FR-CH":
            continue

        # Compute next occurrence
        next_dates = _compute_next_dates(d, today, months_ahead)
        for next_date in next_dates:
            days_until = (next_date - today).days
            results.append({
                "id": d.id,
                "label": d.label,
                "description": d.description,
                "verticals": d.verticals,
                "jurisdiction": d.jurisdiction,
                "frequency": d.frequency,
                "severity": d.severity,
                "reference": d.reference,
                "next_date": next_date.isoformat(),
                "days_until": days_until,
                "urgency": "overdue" if days_until < 0 else "critical" if days_until <= 7 else "high" if days_until <= 30 else "normal",
                "auto_intention": d.auto_intention,
            })

    # Sort by days_until
    results.sort(key=lambda x: x["days_until"])
    return results


def get_deadline_stats(vertical: Optional[str] = None) -> dict:
    """Statistiques sur les échéances"""
    cal = get_calendar(vertical=vertical)
    today_overdue = [d for d in cal if d["days_until"] < 0]
    this_week = [d for d in cal if 0 <= d["days_until"] <= 7]
    this_month = [d for d in cal if 7 < d["days_until"] <= 30]
    return {
        "total": len(cal),
        "overdue": len(today_overdue),
        "this_week": len(this_week),
        "this_month": len(this_month),
        "next_quarter": len([d for d in cal if 30 < d["days_until"] <= 90]),
        "jurisdictions": {
            "FR": len([d for d in cal if "FR" in d["jurisdiction"]]),
            "CH": len([d for d in cal if "CH" in d["jurisdiction"]]),
        },
        "overdue_deadlines": [
            {"label": d["label"], "days_overdue": abs(d["days_until"]), "jurisdiction": d["jurisdiction"]}
            for d in today_overdue
        ],
    }


def _compute_next_dates(deadline: RegulatoryDeadline, today: date, months_ahead: int) -> list[date]:
    """Calculer les prochaines occurrences d'une échéance"""
    results = []
    end = today + timedelta(days=months_ahead * 31)

    if deadline.frequency == "mensuel":
        # Monthly deadline: day X of each month
        current = today.replace(day=1)
        while current <= end:
            day = min(deadline.month_day or 15, 28)
            d = current.replace(day=day)
            if d >= today - timedelta(days=5):
                results.append(d)
            # Next month
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

    elif deadline.frequency == "trimestriel":
        # Quarterly: after each quarter end
        for year in [today.year, today.year + 1]:
            for q in range(1, 5):
                q_end_month = q * 3
                offset_days = deadline.month_day or 30
                base = date(year, q_end_month, 1) + timedelta(days=32)
                base = base.replace(day=1) - timedelta(days=1)  # last day of quarter
                d = base + timedelta(days=offset_days)
                if today - timedelta(days=15) <= d <= end:
                    results.append(d)

    elif deadline.frequency == "annuel":
        if deadline.month and deadline.day:
            for year in [today.year - 1, today.year, today.year + 1]:
                d = date(year, deadline.month, deadline.day)
                if today - timedelta(days=30) <= d <= end:
                    results.append(d)

    return sorted(set(results))
