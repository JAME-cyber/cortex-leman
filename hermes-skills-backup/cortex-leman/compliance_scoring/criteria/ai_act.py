"""
AI Act Criteria — 6 domains covering key articles of Regulation (EU) 2024/1689.

EU Artificial Intelligence Act, entered into force 1 August 2024, with phased application: prohibited practices (Feb 2025), high-risk (Aug 2026), general (Aug 2027).
Phased application: risk management (Aug 2025), high-risk (Aug 2026), general (Aug 2027).

Texts from EUR-Lex: https://eur-lex.europa.eu/eli/reg/2024/1689/oj
"""

from __future__ import annotations

from .base import build_citation, build_criterion, build_domain
from ..models import CriteriaDomain

_AI_ACT_URL = "https://eur-lex.europa.eu/eli/reg/2024/1689/oj"


def _c(art_id: str, title: str, text: str, threshold: float = 0.6,
        weight: float = 1.0, checklist: list | None = None,
        evidence: list[str] | None = None):
    """Shorthand for AI Act criterion."""
    return build_criterion(
        article_id=f"AI_ACT.{art_id}",
        title=title,
        text=text,
        threshold=threshold,
        weight=weight,
        checklist_questions=checklist,
        evidence_types=evidence or [],
        citations=[build_citation(
            source="AI_ACT",
            article_id=f"AI_ACT.{art_id}",
            article_title=title,
            excerpt=text[:200],
            url=_AI_ACT_URL,
            relevance=1.0,
        )],
    )


# ============================================================================
# Domain 1: Classification des risques (Art. 6-7)
# ============================================================================

_aiact_classification = build_domain(
    domain_id="aiact_classification",
    name="Classification des risques IA",
    regulation="AI_ACT",
    chapter="Art. 6-7",
    default_weight=0.15,
    criteria=[
        _c("6", "Systèmes IA à risque",
           "Un système d'IA est considéré comme à risque élevé s'il est un produit de sécurité au sens de la réglementation "
           "UE (machines, jouets, dispositifs médicaux) ou s'il relève de l'annexe III (biométrie, gestion RH, "
           "justice, immigration, services publics essentiels).",
           threshold=0.7,
           weight=1.5,
           checklist=[
               {"question": "Tous les systèmes IA utilisés ont-ils été inventoriés ?", "severity": "critical"},
               {"question": "Chaque système IA a-t-il été classé selon le risque (inacceptable, élevé, limité, minime) ?", "severity": "critical"},
               {"question": "Les systèmes de l'annexe III (biométrie, RH, éducation, justice) ont-ils été identifiés comme à risque élevé ?", "severity": "critical"},
           ],
           evidence=["document", "registre"]),

        _c("5.1.a", "Systèmes de notation sociale par les autorités publiques",
           "Interdiction des systèmes d'IA destinés à la notation sociale des personnes par les autorités publiques "
           "sur une période indéterminée ou de manière généralisée.",
           threshold=0.9,
           weight=1.3,
           checklist=[
               {"question": "Aucun système de notation sociale à usage généralisé par une autorité publique n'est-il utilisé ?", "severity": "critical"},
           ],
           evidence=["document", "declaration"]),

        _c("5.1.b", "Manipulation subliminale et exploitation de vulnérabilités",
           "Interdiction des systèmes manipulant le comportement pour contourner le libre arbitre de manière non "
           "raisonnablement prévisible, et ceux exploitant les vulnérabilités de groupes spécifiques.",
           threshold=0.9,
           weight=1.2,
           checklist=[
               {"question": "Aucun système d'IA manipulant le comportement par des techniques subliminales n'est-il déployé ?", "severity": "critical"},
               {"question": "Aucun système exploitant les vulnérabilités de personnes vulnérables n'est-il déployé ?", "severity": "critical"},
           ],
           evidence=["document", "declaration"]),
    ],
)

# ============================================================================
# Domain 2: Systèmes IA à risque — Obligations (Art. 8-15)
# ============================================================================

_aiact_risk_obligations = build_domain(
    domain_id="aiact_risk_obligations",
    name="Obligations des systèmes IA à risque",
    regulation="AI_ACT",
    chapter="Art. 8-15",
    default_weight=0.20,
    criteria=[
        _c("9", "Système de gestion des risques",
           "Un système de gestion des risques doit être établi, maintenu et mis à jour continuellement pour les "
           "systèmes IA à risque. Il comprend l'identification, l'analyse et le traitement des risques connus et "
           "raisonnablement prévisibles.",
           threshold=0.7,
           weight=1.5,
           checklist=[
               {"question": "Un système de gestion des risques est-il documenté et opérationnel pour chaque système IA à risque ?", "severity": "critical"},
               {"question": "Les risques identifiés sont-ils évalués, traités et documentés ?", "severity": "critical"},
               {"question": "Le système de gestion des risques est-il mis à jour en cas de modification du système IA ?", "severity": "major"},
           ],
           evidence=["document", "policy"]),

        _c("10", "Gouvernance des données",
           "Les systèmes IA à risque doivent être développés sur la base de jeux de données de formation, validation "
           "et test qui respectent des pratiques de gouvernance des données adaptées au contexte.",
           threshold=0.7,
           weight=1.4,
           checklist=[
               {"question": "Les jeux de données de formation, validation et test sont-ils documentés ?", "severity": "major"},
               {"question": "La qualité des données (pertinence, biais, représentativité) a-t-elle été évaluée ?", "severity": "critical"},
               {"question": "Des mesures de correction des biais sont-elles en place ?", "severity": "major"},
           ],
           evidence=["document"]),

        _c("11", "Documentation technique",
           "La documentation technique doit être tenue avant la mise sur le marché et mise à jour tout au long "
           "de la vie du système. Elle inclut : description générale, limitations, capacités, conformité, conception, "
           "méthodes de développement, test et validation.",
           threshold=0.7,
           weight=1.3,
           checklist=[
               {"question": "La documentation technique couvre-t-elle les exigences de l'Art. 11 et de l'Annexe IV ?", "severity": "critical"},
               {"question": "La documentation est-elle disponible pour les autorités de surveillance du marché sur demande ?", "severity": "major"},
               {"question": "La documentation est-elle mise à jour à chaque modification significative ?", "severity": "major"},
           ],
           evidence=["document"]),

        _c("14", "Surveillance humaine",
           "Les systèmes IA à risque doivent être conçus de manière à permettre une surveillance humaine efficace "
           "pendant la durée de vie du système.",
           threshold=0.7,
           weight=1.3,
           checklist=[
               {"question": "Un humain supervise-t-il les décisions critiques du système IA ?", "severity": "critical"},
               {"question": "Les outils de surveillance permettent-ils une intervention humaine en temps réel ?", "severity": "major"},
               {"question": "Les opérateurs humains sont-ils formés à l'interprétation des sorties du système ?", "severity": "major"},
           ],
           evidence=["document", "policy"]),

        _c("15", "Exactitude, robustesse et cyber-sécurité",
           "Les systèmes IA à risque doivent atteindre un niveau approprié d'exactitude, de robustesse et de sécurité "
           "tout au long de leur cycle de vie, avec des mesures de résilience.",
           threshold=0.7,
           weight=1.4,
           checklist=[
               {"question": "Les métriques d'exactitude sont-elles mesurées et documentées ?", "severity": "major"},
               {"question": "Des tests de robustesse (adversarial, edge cases) ont-ils été effectués ?", "severity": "major"},
               {"question": "Des mesures de cyber-sécurité spécifiques au système IA sont-elles en place ?", "severity": "critical"},
           ],
           evidence=["document", "log"]),
    ],
)

# ============================================================================
# Domain 3: Transparence (Art. 50-52)
# ============================================================================

_aiact_transparence = build_domain(
    domain_id="aiact_transparence",
    name="Obligations de transparence",
    regulation="AI_ACT",
    chapter="Art. 50-52",
    default_weight=0.15,
    criteria=[
        _c("50", "Obligation de transparence pour les systèmes IA",
           "Les systèmes IA qui interagissent avec les personnes, génèrent ou manipulent du contenu (image, audio, vidéo, "
           "texte), ou classifient les personnes, doivent divulguer qu'ils sont des systèmes IA.",
           threshold=0.7,
           weight=1.5,
           checklist=[
               {"question": "Les utilisateurs sont-ils informés lorsqu'ils interagissent avec un système IA ?", "severity": "critical"},
               {"question": "Le contenu généré par IA (deepfakes, synthèse vocale, texte) est-il étiqueté comme tel ?", "severity": "critical"},
               {"question": "Les systèmes de classification ou de notation informent-ils les personnes classées ?", "severity": "major"},
           ],
           evidence=["screenshot", "document", "policy"]),

        _c("52", "Transparence des systèmes à risque spécifiques",
           "Les déployeurs de systèmes IA à risque spécifique (émotions, catégories sensibles, profiling biométrique) "
           "doivent informer les personnes concernées.",
           threshold=0.7,
           weight=1.2,
           checklist=[
               {"question": "Les personnes sont-elles informées de l'utilisation de systèmes d'IA d'inférence d'émotions ou de traits de personnalité ?", "severity": "major"},
           ],
           evidence=["document", "screenshot"]),
    ],
)

# ============================================================================
# Domain 4: Gouvernance IA (Art. 16-27)
# ============================================================================

_aiact_gouvernance = build_domain(
    domain_id="aiact_gouvernance",
    name="Gouvernance de l'IA",
    regulation="AI_ACT",
    chapter="Art. 16-27",
    default_weight=0.15,
    criteria=[
        _c("16", "Qualité et conformité des systèmes IA",
           "Les fournisseurs de systèmes IA à risque établissent, documentent, mettent en œuvre et maintiennent "
           "un système de gestion de la qualité.",
           threshold=0.6,
           weight=1.3,
           checklist=[
               {"question": "Un système de gestion de la qualité couvre-t-il le cycle de vie complet du système IA ?", "severity": "major"},
               {"question": "Des procédures de contrôle qualité sont-elles documentées pour les phases de conception et développement ?", "severity": "major"},
           ],
           evidence=["document", "policy"]),

        _c("26", "Obligations des déployeurs",
           "Les déployeurs de systèmes IA à risque prennent des mesures techniques et organisationnelles pour "
           "utiliser le système conformément aux instructions du fournisseur, s'assurer que les données d'entrée "
           "sont pertinentes, conserver les logs automatiques pendant une durée appropriée.",
           threshold=0.7,
           weight=1.4,
           checklist=[
               {"question": "Le déployeur s'assure-t-il que le système IA est utilisé conformément aux instructions du fournisseur ?", "severity": "major"},
               {"question": "Les données d'entrée du système sont-elles pertinentes et représentatives ?", "severity": "major"},
               {"question": "Les logs du système IA sont-ils conservés pendant une durée appropriée (min. 6 mois) ?", "severity": "critical"},
               {"question": "Une AIFD (évaluation d'impact fondamentale) a-t-elle été réalisée si nécessaire ?", "severity": "major"},
           ],
           evidence=["document", "log", "policy"]),
    ],
)

# ============================================================================
# Domain 5: Documentation technique (Art. 11, Annexe IV)
# ============================================================================

_aiact_documentation = build_domain(
    domain_id="aiact_documentation",
    name="Documentation technique IA",
    regulation="AI_ACT",
    chapter="Art. 11, Annexe IV",
    default_weight=0.15,
    criteria=[
        _c("11.annexe4", "Contenu de la documentation technique (Annexe IV)",
           "La documentation technique doit inclure : description générale, limitations, capacités, type d'IA, "
           "conformité, conception et spécifications, méthodes de développement, test et validation, "
           "mesures de qualité et sécurité, informations pour les déployeurs.",
           threshold=0.7,
           weight=1.5,
           checklist=[
               {"question": "La documentation contient-elle la description générale du système et ses capacités ?", "severity": "major"},
               {"question": "Les limitations et les risques connus sont-ils documentés ?", "severity": "major"},
               {"question": "Les méthodes de développement, les jeux de données, et les procédures de test sont-ils documentés ?", "severity": "major"},
               {"question": "Les informations nécessaires aux déployeurs pour l'utilisation conforme sont-elles fournies ?", "severity": "major"},
           ],
           evidence=["document"]),
    ],
)

# ============================================================================
# Domain 6: Conformité et CE marking (Art. 43-49)
# ============================================================================

_aiact_conformite = build_domain(
    domain_id="aiact_conformite",
    name="Conformité et marquage CE",
    regulation="AI_ACT",
    chapter="Art. 43-49",
    default_weight=0.20,
    criteria=[
        _c("43", "Évaluation de la conformité",
           "Avant la mise sur le marché, le fournisseur d'un système IA à risque effectue une évaluation de conformité "
           "selon les procédures de l'Art. 43. Les systèmes qui génèrent et manipulent du contenu nécessitent des "
           "garanties adéquates de protection des droits.",
           threshold=0.7,
           weight=1.5,
           checklist=[
               {"question": "Une évaluation de conformité a-t-elle été effectuée pour chaque système IA à risque ?", "severity": "critical"},
               {"question": "Les systèmes à manipulation de contenu disposent-ils de garanties de protection des droits ?", "severity": "critical"},
               {"question": "L'évaluation a-t-elle été réalisée par un organisme notifié ou en auto-évaluation ?", "severity": "major"},
           ],
           evidence=["document"]),

        _c("47", "Déclaration UE de conformité",
           "Le fournisseur établit une déclaration UE de conformité pour les systèmes IA à risque conformes, "
           "indiquant le nom du fournisseur, la description du système, la norme harmonisée, les exigences "
           "satisfaites, et l'identité du notified body le cas échéant.",
           threshold=0.8,
           weight=1.3,
           checklist=[
               {"question": "Une déclaration UE de conformité a-t-elle été établie pour chaque système IA à risque ?", "severity": "critical"},
               {"question": "La déclaration contient-elle tous les éléments requis par l'Art. 47 ?", "severity": "major"},
               {"question": "La déclaration est-elle traduite dans la langue requise par l'État membre ?", "severity": "minor"},
           ],
           evidence=["document"]),

        _c("48", "Marquage CE",
           "Les systèmes IA à risque conformes portent le marquage CE.",
           threshold=0.8,
           weight=1.2,
           checklist=[
               {"question": "Le marquage CE est-il apposé sur le système IA à risque conforme ?", "severity": "critical"},
               {"question": "Le marquage respecte-t-il les conditions de l'Art. 48 ?", "severity": "minor"},
           ],
           evidence=["document", "screenshot"]),
    ],
)


AI_ACT_DOMAINS: list[CriteriaDomain] = [
    _aiact_classification,
    _aiact_risk_obligations,
    _aiact_transparence,
    _aiact_gouvernance,
    _aiact_documentation,
    _aiact_conformite,
]
