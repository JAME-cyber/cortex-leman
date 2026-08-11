"""
LPD/CH (nLPD) Criteria — 4 domains covering key articles of the Swiss
Federal Act on Data Protection (nLPD) of 25 September 2020, in force since 1 Sep 2023.

Texts from Fedlex: https://www.fedlex.admin.ch/eli/cc/2020/720/fr

IMPORTANT: Swiss LPD has significant differences from RGPD:
- No GDPR-like maximum fines (but civil liability and criminal sanctions)
- Secret professionnel applies to DPO/DSI in certain sectors
- Extra-territorial application is narrower than RGPD
- No systematic AIPD obligation (but risk assessment recommended)
"""

from __future__ import annotations

from .base import build_citation, build_criterion, build_domain
from ..models import CriteriaDomain

_LPD_URL = "https://www.fedlex.admin.ch/eli/cc/2020/720/fr"


def _c(art_id: str, title: str, text: str, threshold: float = 0.6,
        weight: float = 1.0, checklist: list | None = None,
        evidence: list[str] | None = None):
    """Shorthand for LPD/CH criterion."""
    return build_criterion(
        article_id=f"LPD_CH.{art_id}",
        title=title,
        text=text,
        threshold=threshold,
        weight=weight,
        checklist_questions=checklist,
        evidence_types=evidence or [],
        citations=[build_citation(
            source="LPD_CH",
            article_id=f"LPD_CH.{art_id}",
            article_title=title,
            excerpt=text[:200],
            url=_LPD_URL,
            relevance=1.0,
        )],
    )


# ============================================================================
# Domain 1: Principes (Art. 4-7)
# ============================================================================

_lpd_principes = build_domain(
    domain_id="lpd_principes",
    name="Principes de protection des données",
    regulation="LPD_CH",
    chapter="Art. 4-7",
    default_weight=0.25,
    criteria=[
        _c("4", "Bonne foi",
           "Les données personnelles sont traitées de bonne foi.",
           threshold=0.6,
           weight=1.0,
           checklist=[
               {"question": "Les traitements de données sont-ils effectués de bonne foi, sans intention de nuire aux personnes concernées ?", "severity": "major"},
           ],
           evidence=["document", "policy"]),

        _c("5", "Principe de finalité",
           "Les données personnelles ne sont traitées que dans le but indiqué au moment de leur collecte "
           "ou qui est compatible avec ce but. Elles ne sont traitées d'une manière incompatible avec ce but "
           "que si la loi l'exige ou le permet, ou si la personne concernée y consent.",
           threshold=0.7,
           weight=1.3,
           checklist=[
               {"question": "Chaque traitement a-t-il une finalité documentée au moment de la collecte ?", "severity": "major"},
               {"question": "Les usages ultérieurs des données sont-ils compatibles avec la finalité initiale ?", "severity": "major"},
               {"question": "En cas de changement de finalité, la base légale est-elle vérifiée ?", "severity": "major"},
           ],
           evidence=["document", "registre"]),

        _c("6", "Principe de proportionnalité",
           "Le traitement des données doit être proportionnel au but visé. La collecte et le traitement "
           "des données sont limités au strict nécessaire.",
           threshold=0.7,
           weight=1.3,
           checklist=[
               {"question": "Les données collectées sont-elles proportionnelles au but du traitement ?", "severity": "major"},
               {"question": "Le traitement est-il limité au strict nécessaire (minimisation) ?", "severity": "critical"},
           ],
           evidence=["document"]),

        _c("6.2", "Données sensibles",
           "Sont considérées comme sensibles les données sur : opinions religieuses, philosophiques ou politiques, "
           "santé, intimité, origine raciale ou ethnique, sanctions pénales et administratives, mesures sociales, "
           "données génétiques et biométriques.",
           threshold=0.8,
           weight=1.4,
           checklist=[
               {"question": "Les catégories de données sensibles traitées ont-elles été identifiées ?", "severity": "critical"},
               {"question": "Les traitements de données sensibles ont-ils une base légale spécifique ?", "severity": "critical"},
               {"question": "Des mesures de protection renforcées sont-elles appliquées aux données sensibles ?", "severity": "major"},
           ],
           evidence=["document", "policy"]),

        _c("7", "Transparence",
           "Le responsable de traitement informe la personne concernée du traitement de ses données si ses "
           "intérêts dignes de protection l'exigent.",
           threshold=0.6,
           weight=1.2,
           checklist=[
               {"question": "Les personnes concernées sont-elles informées du traitement de leurs données ?", "severity": "major"},
               {"question": "Les informations fournies sont-elles claires et accessibles ?", "severity": "minor"},
           ],
           evidence=["document", "screenshot"]),
    ],
)

# ============================================================================
# Domain 2: Droits des personnes (Art. 25-34)
# ============================================================================

_lpd_droits = build_domain(
    domain_id="lpd_droits",
    name="Droits des personnes concernées",
    regulation="LPD_CH",
    chapter="Art. 25-34",
    default_weight=0.25,
    criteria=[
        _c("25", "Droit d'information",
           "Le responsable de traitement informe la personne concernée de son droit d'accès, de rectification, "
           "d'effacement et de portabilité, et de l'existence d'un fichier si les données sont transmises.",
           threshold=0.6,
           weight=1.2,
           checklist=[
               {"question": "Les personnes sont-elles informées de leurs droits (accès, rectification, effacement, portabilité) ?", "severity": "major"},
               {"question": "L'information est-elle fournie dans les cas où les données sont collectées间接ement ?", "severity": "major"},
           ],
           evidence=["document", "screenshot"]),

        _c("28", "Droit d'accès",
           "Toute personne peut exiger du responsable de traitement des renseignements sur le traitement "
           "de ses données personnelles. Le droit d'accès est gratuit.",
           threshold=0.6,
           weight=1.3,
           checklist=[
               {"question": "Une procédure d'exercice du droit d'accès existe-t-elle ?", "severity": "major"},
               {"question": "Les demandes sont-elles traitées dans un délai raisonnable (30 jours) ?", "severity": "major"},
           ],
           evidence=["document", "log"]),

        _c("30", "Droit de rectification",
           "Toute personne peut exiger la rectification des données personnelles inexactes la concernant.",
           threshold=0.6,
           weight=1.0,
           checklist=[
               {"question": "Une procédure de rectification des données existe-t-elle ?", "severity": "major"},
           ],
           evidence=["document"]),

        _c("31", "Droit à l'effacement",
           "Toute personne peut exiger l'effacement des données personnelles traitées en violation de la loi.",
           threshold=0.7,
           weight=1.3,
           checklist=[
               {"question": "Les demandes d'effacement pour données traitées en violation sont-elles traitées ?", "severity": "major"},
               {"question": "L'effacement est-il effectif dans tous les systèmes concernés ?", "severity": "major"},
           ],
           evidence=["document", "log"]),

        _c("32", "Droit à la portabilité",
           "Toute personne a le droit d'obtenir du responsable les données personnelles la concernant dans un "
           "format électronique couramment utilisé, dans la mesure où cela est techniquement réalisable et "
           "sans que les droits d'autres personnes ne soient lésés.",
           threshold=0.6,
           weight=1.1,
           checklist=[
               {"question": "Les données peuvent-elles être exportées dans un format électronique standard ?", "severity": "major"},
               {"question": "Le droit de portabilité est-il mentionné dans les informations aux personnes ?", "severity": "minor"},
           ],
           evidence=["document", "screenshot"]),
    ],
)

# ============================================================================
# Domain 3: Sécurité (Art. 8)
# ============================================================================

_lpd_securite = build_domain(
    domain_id="lpd_securite",
    name="Sécurité des données",
    regulation="LPD_CH",
    chapter="Art. 7-8",
    default_weight=0.25,
    criteria=[
        _c("7", "Obligation de sécurité",
           "Le responsable prend toutes les mesures techniques et organisationnelles nécessaires pour "
           "assurer la protection des données. Il garantit en particulier que les données sont protégées "
           "contre tout traitement non autorisé.",
           threshold=0.7,
           weight=1.4,
           checklist=[
               {"question": "Des mesures techniques et organisationnelles de protection des données sont-elles en place ?", "severity": "critical"},
               {"question": "La protection contre les traitements non autorisés est-elle garantie ?", "severity": "critical"},
               {"question": "Un concept de protection des données est-il documenté ?", "severity": "major"},
           ],
           evidence=["document", "policy"]),

        _c("8", "Responsabilité du traitement par des tiers",
           "Le responsable reste responsable de la protection des données s'il fait appel à un tiers pour "
           "traiter des données. Le tiers ne peut traiter les données qu'en vertu d'un contrat ou d'une "
           "disposition légale.",
           threshold=0.7,
           weight=1.3,
           checklist=[
               {"question": "Un contrat existe-t-il avec chaque sous-traitant ?", "severity": "critical"},
               {"question": "Le contrat définit-il les obligations de protection des données du sous-traitant ?", "severity": "critical"},
               {"question": "Le sous-traitant est-il contrôlé régulièrement sur le respect de ses obligations ?", "severity": "major"},
           ],
           evidence=["contract", "dpa"]),
    ],
)

# ============================================================================
# Domain 4: Transferts à l'étranger (Art. 16-17)
# ============================================================================

_lpd_transferts = build_domain(
    domain_id="lpd_transferts",
    name="Transferts de données à l'étranger",
    regulation="LPD_CH",
    chapter="Art. 16-17",
    default_weight=0.25,
    criteria=[
        _c("16", "Transfert à l'étranger",
           "Le responsable ne peut transmettre des données à l'étranger que si : la législation de l'État "
           "destinataire garantit un niveau de protection adéquat, des garanties contractuelles suffisantes "
           "existent, ou la personne concernée y consent expressément.",
           threshold=0.8,
           weight=1.5,
           checklist=[
               {"question": "Tous les transferts de données vers l'étranger ont-ils été identifiés ?", "severity": "critical"},
               {"question": "Les pays destinataires garantissent-ils un niveau de protection adéquat ?", "severity": "critical"},
               {"question": "Pour les pays non adéquats, des garanties contractuelles sont-elles en place ?", "severity": "critical"},
               {"question": "Le consentement des personnes est-il recueilli si nécessaire ?", "severity": "major"},
           ],
           evidence=["document", "contract", "registre"]),

        _c("17", "Décision du Conseil fédéral",
           "Le Conseil fédéral décide si un État dispose d'une législation assurant un niveau de protection adéquat.",
           threshold=0.6,
           weight=1.0,
           checklist=[
               {"question": "Les transferts ont-ils été vérifiés contre la liste du Conseil fédéral des pays adéquats ?", "severity": "major"},
           ],
           evidence=["document"]),
    ],
)


LPD_CH_DOMAINS: list[CriteriaDomain] = [
    _lpd_principes,
    _lpd_droits,
    _lpd_securite,
    _lpd_transferts,
]
