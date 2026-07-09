"""
Cortex Leman v5 — Vertical Connectors Registry

Registre des connecteurs verticaux.
Chaque vertical expose: validate, enrich, templates, calendar.
"""
import logging
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Résultat de validation d'une action verticale."""
    valid: bool
    vertical: str
    checks: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    blocks: list[str] = field(default_factory=list)
    compliance_score: float = 1.0

    def to_dict(self) -> dict:
        return {
            "valid": self.valid,
            "vertical": self.vertical,
            "checks": self.checks,
            "warnings": self.warnings,
            "blocks": self.blocks,
            "compliance_score": self.compliance_score,
        }


@dataclass
class DeadlineEvent:
    """Échéance réglementaire."""
    id: str
    title: str
    date: str
    vertical: str
    category: str
    description: str
    urgency: str = "normal"  # normal, urgent, critical
    action_required: str = ""
    regulation_ref: str = ""


@dataclass
class DocumentTemplate:
    """Template de document réglementaire."""
    id: str
    title: str
    vertical: str
    category: str
    description: str
    fields: list[str] = field(default_factory=list)
    regulation_ref: str = ""


class BaseVertical:
    """Classe de base pour les connecteurs verticaux."""

    VERTICAL_ID: str = "unknown"
    VERTICAL_LABEL: str = "Inconnu"
    VERTICAL_ICON: str = "❓"
    REGULATIONS: list[str] = field(default_factory=list)

    def validate(self, action: str, context: dict) -> ValidationResult:
        raise NotImplementedError

    def enrich(self, context: dict) -> dict:
        return context

    def templates(self) -> list[DocumentTemplate]:
        return []

    def calendar(self, year: int = None) -> list[DeadlineEvent]:
        return []


# ═══════════════════════════════════════════════════════════════
# COMPTABLE
# ═══════════════════════════════════════════════════════════════

class ComptableVertical(BaseVertical):
    """Connecteur vertical Comptable — TVA, bilans, déclarations fiscales."""

    VERTICAL_ID = "comptable"
    VERTICAL_LABEL = "Comptable / Fiduciaire"
    VERTICAL_ICON = "📊"

    TVA_RATES = {
        "standard": 8.1,    # Taux normal CH
        "reduit": 2.6,      # Taux réduit (hébergement, alimentation)
        "special": 3.8,     # Taux spécial (hôtellerie)
        "exempt": 0.0,      # Exempté
    }

    def validate(self, action: str, context: dict) -> ValidationResult:
        checks = []
        warnings = []
        blocks = []
        score = 1.0

        montant = context.get("montant", 0)
        action_type = context.get("action_type", action)

        # Vérification TVA
        if action_type in ("ecriture_comptable", "virement", "facturation"):
            tva_rate = context.get("tva_rate")
            if tva_rate is not None:
                valid_rates = list(self.TVA_RATES.values())
                if tva_rate not in valid_rates:
                    blocks.append(f"Taux TVA {tva_rate}% non conforme en Suisse. Taux valides: {valid_rates}")
                    score -= 0.3
                checks.append({"id": "tva_rate", "status": "ok" if tva_rate in valid_rates else "invalid", "value": tva_rate})

        # Seuil déclaration TVA
        if montant and montant >= 100000:
            warnings.append(f"Montant CHF {montant:,.0f} — vérifier les obligations TVA annuelles (seuil CHF 100'000)")
            checks.append({"id": "tva_threshold", "status": "warning", "value": montant})

        # Anti-blanchiment
        if montant and montant >= 15000:
            warnings.append(f"Montant CHF {montant:,.0f} — obligation de déclaration selon la LBA (seuil CHF 15'000)")
            checks.append({"id": "aml_threshold", "status": "warning", "value": montant})

        if montant and montant >= 100000:
            blocks.append(f"Montant CHF {montant:,.0f} — KYC renforcé obligatoire. Gel préventif du Médiateur.")
            score -= 0.5

        # Vérification CRCR (Commission de révision)
        if action_type == "revision" and context.get("client_size") == "large":
            warnings.append("CRCR: Entité d'intérêt public — révision complète requise")

        return ValidationResult(
            valid=len(blocks) == 0,
            vertical=self.VERTICAL_ID,
            checks=checks,
            warnings=warnings,
            blocks=blocks,
            compliance_score=max(0, score),
        )

    def enrich(self, context: dict) -> dict:
        """Enrichir avec les données fiscales suisses."""
        montant = context.get("montant", 0)
        if montant:
            context["tva_estimated"] = round(montant * self.TVA_RATES["standard"] / 100, 2)
            context["tva_reduit_estimated"] = round(montant * self.TVA_RATES["reduit"] / 100, 2)
        return context

    def templates(self) -> list[DocumentTemplate]:
        return [
            DocumentTemplate(
                id="decl_tva_trimestrielle",
                title="Déclaration TVA trimestrielle",
                vertical=self.VERTICAL_ID,
                category="fiscal",
                description="Template de déclaration TVA trimestrielle selon l'AFF",
                fields=["periode", "chiffre_affaires", "tva_collectee", "tva_deductible", "tva_nette"],
                regulation_ref="LTVA art. 38-42",
            ),
            DocumentTemplate(
                id="bilan_annuel",
                title="Bilan annuel simplifié",
                vertical=self.VERTICAL_ID,
                category="comptable",
                description="Bilan annuel selon le Code des obligations suisse",
                fields=["actif", "passif", "resultat", "fonds_propres"],
                regulation_ref="CO art. 958-963",
            ),
            DocumentTemplate(
                id="compte_resultat",
                title="Compte de résultat",
                vertical=self.VERTICAL_ID,
                category="comptable",
                description="Compte de résultat selon les normes suisses",
                fields=["produits", "charges", "ebitda", "resultat_net"],
                regulation_ref="CO art. 958a",
            ),
        ]

    def calendar(self, year: int = None) -> list[DeadlineEvent]:
        y = year or date.today().year
        return [
            DeadlineEvent(
                id="tva_q1", title="Déclaration TVA Q1", vertical=self.VERTICAL_ID,
                date=f"{y}-04-30", category="fiscal",
                description="Déclaration TVA pour le 1er trimestre", urgency="urgent",
                action_required="Soumettre la déclaration TVA via le portail de l'AFF",
                regulation_ref="LTVA art. 38",
            ),
            DeadlineEvent(
                id="tva_q2", title="Déclaration TVA Q2", vertical=self.VERTICAL_ID,
                date=f"{y}-07-31", category="fiscal",
                description="Déclaration TVA pour le 2ème trimestre", urgency="urgent",
                action_required="Soumettre la déclaration TVA via le portail de l'AFF",
                regulation_ref="LTVA art. 38",
            ),
            DeadlineEvent(
                id="tva_q3", title="Déclaration TVA Q3", vertical=self.VERTICAL_ID,
                date=f"{y}-10-31", category="fiscal",
                description="Déclaration TVA pour le 3ème trimestre", urgency="urgent",
                action_required="Soumettre la déclaration TVA via le portail de l'AFF",
                regulation_ref="LTVA art. 38",
            ),
            DeadlineEvent(
                id="tva_q4", title="Déclaration TVA Q4 + annuelle", vertical=self.VERTICAL_ID,
                date=f"{y+1}-01-31", category="fiscal",
                description="Déclaration TVA pour le 4ème trimestre + récapitulatif annuel",
                urgency="critical",
                action_required="Soumettre la déclaration TVA et le récapitulatif annuel",
                regulation_ref="LTVA art. 38-42",
            ),
            DeadlineEvent(
                id="bilan", title="Dépôt bilan annuel", vertical=self.VERTICAL_ID,
                date=f"{y}-06-30", category="comptable",
                description="Dépôt du bilan et du compte de résultat au RC",
                urgency="normal",
                action_required="Déposer les comptes annuels au Registre du commerce",
                regulation_ref="CO art. 958",
            ),
        ]


# ═══════════════════════════════════════════════════════════════
# AVOCAT
# ═══════════════════════════════════════════════════════════════

class AvocatVertical(BaseVertical):
    """Connecteur vertical Avocat — Secret professionnel, BAR, droit FR-CH."""

    VERTICAL_ID = "avocat"
    VERTICAL_LABEL = "Avocat / Juriste"
    VERTICAL_ICON = "⚖️"

    def validate(self, action: str, context: dict) -> ValidationResult:
        checks = []
        warnings = []
        blocks = []
        score = 1.0

        # Secret professionnel absolu
        if context.get("data_transfer") or context.get("cross_border"):
            if not context.get("client_consent"):
                blocks.append("Secret professionnel absolu (art. 321 CP) — transfert impossible sans consentement client")
                score -= 0.5
            checks.append({"id": "client_consent", "status": "ok" if context.get("client_consent") else "missing"})

        # Cross-border
        if context.get("cross_border"):
            warnings.append("Transfert cross-border — vérifier la convention de La Haye et le RGPD")
            checks.append({"id": "cross_border", "status": "warning"})

        # IA haute risque (AI Act)
        if action == "IA_high_risk":
            blocks.append("IA haut risque — AI Act art. 6. Conformité obligatoire avant déploiement")
            score -= 0.5

        return ValidationResult(
            valid=len(blocks) == 0,
            vertical=self.VERTICAL_ID,
            checks=checks,
            warnings=warnings,
            blocks=blocks,
            compliance_score=max(0, score),
        )

    def templates(self) -> list[DocumentTemplate]:
        return [
            DocumentTemplate(
                id="mandat_client", title="Mandat client", vertical=self.VERTICAL_ID,
                category="legal", description="Convention d'honoraire et mandat de représentation",
                fields=["client", "affaire", "honoraire", "duree"], regulation_ref="LLCA art. 12",
            ),
            DocumentTemplate(
                id="consentement_rgpd", title="Consentement RGPD", vertical=self.VERTICAL_ID,
                category="privacy", description="Formulaire de consentement au traitement des données personnelles",
                fields=["client", "finalites", "duree", "destinataires"], regulation_ref="RGPD art. 6-7",
            ),
        ]

    def calendar(self, year: int = None) -> list[DeadlineEvent]:
        y = year or date.today().year
        return [
            DeadlineEvent(
                id="cert_bar", title="Certificat BAR", vertical=self.VERTICAL_ID,
                date=f"{y}-12-31", category="professionnel",
                description="Renouvellement du certificat du barreau", urgency="normal",
                action_required="Vérifier les heures de formation continue",
            ),
        ]


# ═══════════════════════════════════════════════════════════════
# SANTÉ
# ═══════════════════════════════════════════════════════════════

class SanteVertical(BaseVertical):
    """Connecteur vertical Santé — H+QR, Lamal, secret médical."""

    VERTICAL_ID = "sante"
    VERTICAL_LABEL = "Santé / Médical"
    VERTICAL_ICON = "🏥"

    # Catégories de données sensibles (RGPD art. 9)
    SENSITIVE_CATEGORIES = [
        "donnees_sante", "genetique", "biometrique",
        "orientation_sexuelle", "addiction", "sante_mentale",
    ]

    def validate(self, action: str, context: dict) -> ValidationResult:
        checks = []
        warnings = []
        blocks = []
        score = 1.0

        # Données sensibles
        data_category = context.get("data_category")
        if data_category in self.SENSITIVE_CATEGORIES:
            warnings.append(f"Données sensibles détectées: {data_category}. Traitement soumis au RGPD art. 9 et à la LPMDS.")
            checks.append({"id": "sensitive_data", "status": "warning", "value": data_category})
            score -= 0.2

            if not context.get("legal_basis"):
                blocks.append("Données de santé sans base légale — traitement interdit (RGPD art. 9.2)")
                score -= 0.5

        # Secret médical
        if context.get("data_transfer"):
            if not context.get("patient_consent"):
                blocks.append("Secret médical (art. 321 CP) — partage impossible sans consentement du patient")
                score -= 0.5

        # H+QR
        if action == "IA_high_risk":
            blocks.append("IA en santé = haut risque selon AI Act. AIPD obligatoire, conformité H+QR requise")
            score -= 0.5

        return ValidationResult(
            valid=len(blocks) == 0,
            vertical=self.VERTICAL_ID,
            checks=checks,
            warnings=warnings,
            blocks=blocks,
            compliance_score=max(0, score),
        )

    def templates(self) -> list[DocumentTemplate]:
        return [
            DocumentTemplate(
                id="consentement_patient", title="Consentement patient", vertical=self.VERTICAL_ID,
                category="medical", description="Formulaire de consentement éclairé du patient",
                fields=["patient", "traitement", "medecin", "date"], regulation_ref="LPMDS art. 7",
            ),
            DocumentTemplate(
                id="aipd", title="AIPD — Analyse d'impact", vertical=self.VERTICAL_ID,
                category="rgpd", description="Analyse d'impact relative à la protection des données",
                fields=["systeme", "donnees", "risques", "mesures"], regulation_ref="RGPD art. 35",
            ),
        ]

    def calendar(self, year: int = None) -> list[DeadlineEvent]:
        y = year or date.today().year
        return [
            DeadlineEvent(
                id="audit_lamal", title="Audit Lamal", vertical=self.VERTICAL_ID,
                date=f"{y}-09-30", category="reglementaire",
                description="Audit annuel des données Lamal", urgency="normal",
            ),
        ]


# ═══════════════════════════════════════════════════════════════
# BANQUE
# ═══════════════════════════════════════════════════════════════

class BanqueVertical(BaseVertical):
    """Connecteur vertical Banque — KYC, AML, CFB, FINMA."""

    VERTICAL_ID = "banque"
    VERTICAL_LABEL = "Banque / Finance"
    VERTICAL_ICON = "🏦"

    def validate(self, action: str, context: dict) -> ValidationResult:
        checks = []
        warnings = []
        blocks = []
        score = 1.0

        montant = context.get("montant", 0)

        # KYC simplifié / renforcé
        if montant and montant >= 15000:
            warnings.append(f"KYC renforcé requis: CHF {montant:,.0f} (seuil FINMA: CHF 15'000)")
            checks.append({"id": "kyc_enhanced", "status": "warning", "value": montant})

        if montant and montant >= 100000:
            blocks.append(f"Montant CHF {montant:,.0f} — due diligence renforcée FINMA. Gel préventif.")
            score -= 0.5

        # AML (Anti-Money Laundering)
        if context.get("cross_border") and montant and montant >= 5000:
            warnings.append("Transfert transfrontalier + montant → vérification AML/GAFI requise")
            checks.append({"id": "aml_cross_border", "status": "warning"})

        # PEP (Personne Politiquement Exposée)
        if context.get("pep"):
            warnings.append("PEP détecté — procédures renforcées obligatoires (FINMA)")
            checks.append({"id": "pep_check", "status": "warning"})

        return ValidationResult(
            valid=len(blocks) == 0,
            vertical=self.VERTICAL_ID,
            checks=checks,
            warnings=warnings,
            blocks=blocks,
            compliance_score=max(0, score),
        )

    def calendar(self, year: int = None) -> list[DeadlineEvent]:
        y = year or date.today().year
        return [
            DeadlineEvent(
                id="kyc_review", title="Revue KYC annuelle", vertical=self.VERTICAL_ID,
                date=f"{y}-03-31", category="conformite",
                description="Revue annuelle des dossiers KYC clients", urgency="urgent",
                action_required="Mettre à jour les profils KYC de tous les clients",
            ),
            DeadlineEvent(
                id="finma_report", title="Rapport FINMA", vertical=self.VERTICAL_ID,
                date=f"{y}-06-30", category="reglementaire",
                description="Rapport annuel à la FINMA", urgency="critical",
            ),
        ]


# ═══════════════════════════════════════════════════════════════
# STARTUP
# ═══════════════════════════════════════════════════════════════

class StartupVertical(BaseVertical):
    """Connecteur vertical Startup — LPMA, base légale, fast-track."""

    VERTICAL_ID = "startup"
    VERTICAL_LABEL = "Startup / Tech"
    VERTICAL_ICON = "🚀"

    def validate(self, action: str, context: dict) -> ValidationResult:
        checks = []
        warnings = []
        blocks = []
        score = 1.0

        # LPMA (Loi sur les placements collectifs)
        if context.get("fundraising") and context.get("montant", 0) >= 1000000:
            warnings.append("Levée de fonds ≥ CHF 1M — vérifier les obligations LPMA et les prospectus")
            checks.append({"id": "lpma_check", "status": "warning"})

        # RGPD startup
        if action == "data_transfer":
            warnings.append("Transfert de données — vérifier le DPA (Data Processing Agreement) avec le sous-traitant")

        return ValidationResult(
            valid=len(blocks) == 0,
            vertical=self.VERTICAL_ID,
            checks=checks,
            warnings=warnings,
            blocks=blocks,
            compliance_score=max(0, score),
        )


# ═══════════════════════════════════════════════════════════════
# RH
# ═══════════════════════════════════════════════════════════════

class RHVertical(BaseVertical):
    """Connecteur vertical RH — LTr, OAR, RGPD employé."""

    VERTICAL_ID = "rh"
    VERTICAL_LABEL = "Ressources Humaines"
    VERTICAL_ICON = "👥"

    def validate(self, action: str, context: dict) -> ValidationResult:
        checks = []
        warnings = []
        blocks = []
        score = 1.0

        # Données employé sensibles
        if context.get("employee_data"):
            if not context.get("legal_basis"):
                warnings.append("Traitement de données employé sans base légale explicite (RGPD art. 6)")
                checks.append({"id": "employee_legal_basis", "status": "warning"})

        # Surveillance employé (AI Act)
        if action == "IA_high_risk":
            blocks.append("IA pour décision RH = haut risque (AI Act art. 6). Conformité obligatoire.")
            score -= 0.5

        return ValidationResult(
            valid=len(blocks) == 0,
            vertical=self.VERTICAL_ID,
            checks=checks,
            warnings=warnings,
            blocks=blocks,
            compliance_score=max(0, score),
        )

    def calendar(self, year: int = None) -> list[DeadlineEvent]:
        y = year or date.today().year
        return [
            DeadlineEvent(
                id="lt_review", title="Revue contrats LTr", vertical=self.VERTICAL_ID,
                date=f"{y}-01-31", category="legal",
                description="Revue annuelle des contrats de travail", urgency="normal",
            ),
        ]


# ═══════════════════════════════════════════════════════════════
# REGISTRY
# ═══════════════════════════════════════════════════════════════

class VerticalRegistry:
    """Registre central des connecteurs verticaux."""

    def __init__(self):
        self._registry: dict[str, BaseVertical] = {}
        self._register_defaults()

    def _register_defaults(self):
        for cls in [ComptableVertical, AvocatVertical, SanteVertical, BanqueVertical, StartupVertical, RHVertical]:
            instance = cls()
            self._registry[instance.VERTICAL_ID] = instance

    def get(self, vertical: str) -> Optional[BaseVertical]:
        return self._registry.get(vertical)

    def list_all(self) -> list[dict]:
        return [
            {"id": v.VERTICAL_ID, "label": v.VERTICAL_LABEL, "icon": v.VERTICAL_ICON}
            for v in self._registry.values()
        ]

    def validate(self, vertical: str, action: str, context: dict) -> ValidationResult:
        connector = self.get(vertical)
        if not connector:
            return ValidationResult(valid=True, vertical=vertical, warnings=[f"Connecteur '{vertical}' non trouvé"])
        return connector.validate(action, context)

    def enrich(self, vertical: str, context: dict) -> dict:
        connector = self.get(vertical)
        if connector:
            return connector.enrich(context)
        return context

    def templates(self, vertical: str = None) -> list[dict]:
        if vertical:
            connector = self.get(vertical)
            return [t.__dict__ for t in (connector.templates() if connector else [])]
        all_templates = []
        for connector in self._registry.values():
            all_templates.extend([t.__dict__ for t in connector.templates()])
        return all_templates

    def calendar(self, vertical: str = None, year: int = None) -> list[dict]:
        if vertical:
            connector = self.get(vertical)
            return [d.__dict__ for d in (connector.calendar(year) if connector else [])]
        all_deadlines = []
        for connector in self._registry.values():
            all_deadlines.extend([d.__dict__ for d in connector.calendar(year)])
        return sorted(all_deadlines, key=lambda d: d.get("date", ""))


vertical_registry = VerticalRegistry()
