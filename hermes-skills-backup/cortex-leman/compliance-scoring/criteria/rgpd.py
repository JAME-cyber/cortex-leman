"""
RGPD Criteria — 10 domains covering 99 articles.

Regulation (EU) 2016/679 of the European Parliament and of the Council
of 27 April 2016 on the protection of natural persons with regard to
the processing of personal data (General Data Protection Regulation).

Texts are abridged originals from EUR-Lex:
https://eur-lex.europa.eu/eli/reg/2016/679/oj

IMPORTANT: Texts marked [TEXTE À COMPLÉTER] need manual verification
against the official EUR-Lex source and should be filled in.
"""

from __future__ import annotations

from .base import build_citation, build_criterion, build_domain
from ..models import CriteriaDomain

# --- URL templates ---
_RGD_URL = "https://eur-lex.europa.eu/eli/reg/2016/679/oj"


def _c(art_id: str, title: str, text: str, threshold: float = 0.6,
        weight: float = 1.0, checklist: list | None = None,
        evidence: list[str] | None = None, citations: list | None = None):
    """Shorthand for build_criterion with RGPD defaults."""
    rgpd_citations = citations or [build_citation(
        source="RGPD",
        article_id=f"RGPD.{art_id}",
        article_title=title,
        excerpt=text[:200],
        url=_RGD_URL,
        relevance=1.0,
    )]
    return build_criterion(
        article_id=f"RGPD.{art_id}",
        title=title,
        text=text,
        threshold=threshold,
        weight=weight,
        checklist_questions=checklist,
        evidence_types=evidence,
        citations=rgpd_citations,
    )


# ============================================================================
# Domain 1: Principes de traitement (Chapitre II, Art. 5-11)
# ============================================================================

_rgpd_principes = build_domain(
    domain_id="rgpd_principes",
    name="Principes de traitement",
    regulation="RGPD",
    chapter="Chapitre II, Art. 5-11",
    default_weight=0.12,
    criteria=[
        _c("5", "Principes relatifs au traitement des données",
           "1. Les données personnelles doivent être : a) traitées de manière licite, loyale et transparente ; "
           "b) collectées pour des finalités déterminées, explicites et légitimes ; "
           "c) adéquates, pertinentes et limitées ; d) exactes et mises à jour ; "
           "e) conservées sous une forme permettant l'identification pendant une durée n'excédant pas celle nécessaire ; "
           "f) traitées de manière à garantir une sécurité appropriée.",
           threshold=0.7,
           weight=1.5,
           checklist=[
               {"question": "Pour chaque traitement, avez-vous documenté la base légale (consentement, contrat, obligation légale, intérêt légitime) ?", "severity": "critical"},
               {"question": "Les finalités de chaque traitement sont-elles déterminées, explicites et légitimes ?", "severity": "critical"},
               {"question": "Les données collectées sont-elles adéquates, pertinentes et limitées au strict nécessaire (minimisation) ?", "severity": "major"},
               {"question": "Les durées de conservation sont-elles définies pour chaque catégorie de données ?", "severity": "major"},
               {"question": "Existe-t-il une politique de mise à jour et de nettoyage des données obsolètes ?", "severity": "minor"},
           ],
           evidence=["document", "policy", "registre"]),

        _c("6", "Licéité du traitement",
           "Le traitement n'est licite que si et dans la mesure où au moins une des conditions suivantes est remplie : "
           "a) la personne concernée a consenti au traitement ; b) nécessaire à l'exécution d'un contrat ; "
           "c) obligation légale ; d) sauvegarde des intérêts vitaux ; "
           "e) mission d'intérêt public ou relevant de l'exercice de l'autorité publique ; "
           "f) intérêt légitime poursuivi par le responsable.",
           threshold=0.8,
           weight=1.5,
           checklist=[
               {"question": "Pour chaque traitement identifié, la base légale est-elle clairement établie et documentée ?", "severity": "critical"},
               {"question": "Les consentements sont-ils recueillis de manière libre, spécifique, informée et non équivoque ?", "severity": "critical"},
               {"question": "En cas d'intérêt légitime, une analyse de balance des intérêts a-t-elle été réalisée et documentée ?", "severity": "major"},
               {"question": "Les traitements fondés sur le consentement permettent-ils un retrait aussi facile que le don ?", "severity": "major"},
           ],
           evidence=["document", "policy", "contract"]),

        _c("7", "Conditions relatives au consentement",
           "Lorsque le traitement est fondé sur le consentement, le responsable de traitement doit pouvoir "
           "démontrer que la personne concernée a consenti. Le consentement doit être libre, spécifique, "
           "éclairé et non équivoque. Il peut être retiré à tout moment.",
           threshold=0.8,
           weight=1.3,
           checklist=[
               {"question": "Le consentement est-il recueilli par une déclaration ou une action positive claire ?", "severity": "critical"},
               {"question": "Les demandes de consentement sont-elles clairement séparées des autres conditions ?", "severity": "major"},
               {"question": "Les personnes concernées peuvent-elles retirer leur consentement aussi facilement qu'elles l'ont donné ?", "severity": "critical"},
               {"question": "Un registre des consentements est-il maintenu avec les preuves de recueil ?", "severity": "major"},
           ],
           evidence=["document", "registre", "screenshot"]),

        _c("9", "Traitement de catégories particulières de données",
           "Le traitement des données sensibles (origine raciale ou ethnique, opinions politiques, convictions religieuses, "
           "appartenance syndicale, données génétiques, biométriques, santé, vie sexuelle) est interdit sauf exceptions "
           "(consentement explicite, obligations légales, intérêts vitaux, etc.).",
           threshold=0.9,
           weight=1.4,
           checklist=[
               {"question": "Avez-vous identifié tous les traitements portant sur des données sensibles ?", "severity": "critical"},
               {"question": "Pour chaque traitement de données sensibles, une base légale exceptionnelle est-elle applicable et documentée ?", "severity": "critical"},
               {"question": "Les données sensibles sont-elles soumises à des mesures de protection renforcées ?", "severity": "critical"},
               {"question": "Une AIPD (analyse d'impact) a-t-elle été réalisée pour les traitements de données sensibles ?", "severity": "major"},
           ],
           evidence=["document", "pia"]),

        _c("11", "Traitement licite nécessitant une identification",
           "Lorsque les finalités du traitement nécessitent l'identification des personnes concernées, "
           "le responsable doit fournir les moyens permettant de prouver que ces personnes ont effectivement "
           "donné leur consentement au traitement.",
           threshold=0.6,
           weight=0.8,
           checklist=[
               {"question": "Existe-t-il un mécanisme permettant de prouver le consentement de la personne concernée ?", "severity": "major"},
               {"question": "Les enregistrements de preuve de consentement sont-ils horodatés et archivés ?", "severity": "minor"},
           ],
           evidence=["log", "registre"]),
    ],
)

# ============================================================================
# Domain 2: Droits des personnes (Chapitre III, Art. 12-23)
# ============================================================================

_rgpd_droits = build_domain(
    domain_id="rgpd_droits",
    name="Droits des personnes",
    regulation="RGPD",
    chapter="Chapitre III, Art. 12-23",
    default_weight=0.12,
    criteria=[
        _c("12", "Transparence des informations",
           "Le responsable de traitement doit prendre des mesures appropriées pour fournir toute information "
           "relative au traitement aux personnes concernées de manière concise, transparente, intelligible et "
           "accessible, par un langage clair et simple.",
           threshold=0.7,
           weight=1.3,
           checklist=[
               {"question": "Les informations sur le traitement sont-elles fournies au moment de la collecte ?", "severity": "major"},
               {"question": "Les mentions d'information sont-elles rédigées dans un langage clair et simple ?", "severity": "major"},
               {"question": "Les informations couvrent-elles tous les éléments de l'Art. 13 (données collectées directement) ou Art. 14 (données indirectes) ?", "severity": "major"},
               {"question": "L'identité et les coordonnées du DPO sont-elles communiquées ?", "severity": "minor"},
           ],
           evidence=["document", "screenshot", "policy"]),

        _c("13", "Informations à fournir lorsque les données sont collectées auprès de la personne",
           "Lorsque des données sont obtenues auprès de la personne concernée, le responsable doit lui communiquer : "
           "son identité, les finalités, la base légale, les destinataires, les transferts internationaux prévus, "
           "la durée de conservation, les droits de la personne, le droit d'introduire une réclamation.",
           threshold=0.7,
           weight=1.2,
           checklist=[
               {"question": "Les mentions d'information au moment de la collecte incluent-elles : identité du responsable, finalités, base légale, destinataires ?", "severity": "major"},
               {"question": "Les mentions incluent-elles : durée de conservation, droits de la personne, droit de réclamation auprès de l'autorité de contrôle ?", "severity": "major"},
               {"question": "Les informations sont-elles mises à jour en cas de modification du traitement ?", "severity": "minor"},
           ],
           evidence=["document", "screenshot"]),

        _c("15", "Droit d'accès",
           "La personne concernée a le droit d'obtenir la confirmation que des données la concernant sont ou ne sont pas "
           "traitées, ainsi qu'une copie de ces données et les informations visées à l'article 13.",
           threshold=0.7,
           weight=1.3,
           checklist=[
               {"question": "Un procédure d'exercice du droit d'accès existe-t-elle et est-elle accessible ?", "severity": "critical"},
               {"question": "Les demandes d'accès sont-elles traitées dans un délai d'un mois ?", "severity": "major"},
               {"question": "Les copies de données fournies sont-elles dans un format structuré, couramment utilisé et lisible par machine ?", "severity": "major"},
               {"question": "Un registre des demandes d'accès est-il tenu à jour ?", "severity": "minor"},
           ],
           evidence=["document", "log", "registre"]),

        _c("16", "Droit de rectification",
           "La personne concernée a le droit d'obtenir la rectification des données inexactes la concernant.",
           threshold=0.7,
           weight=1.0,
           checklist=[
               {"question": "Une procédure de rectification des données existe-t-elle ?", "severity": "major"},
               {"question": "Les rectifications sont-elles communiquées aux destinataires dans un délai raisonnable ?", "severity": "minor"},
           ],
           evidence=["document", "log"]),

        _c("17", "Droit à l'effacement (droit à l'oubli)",
           "La personne concernée a le droit d'obtenir l'effacement de ses données dans les cas suivants : "
           "données ne sont plus nécessaires, retrait du consentement, opposition au traitement, données illicites, "
           "obligation légale d'effacement.",
           threshold=0.8,
           weight=1.4,
           checklist=[
               {"question": "Une procédure d'exercice du droit à l'oubli existe-t-elle ?", "severity": "critical"},
               {"question": "Les demandes d'effacement sont-elles traitées dans un délai d'un mois ?", "severity": "critical"},
               {"question": "L'effacement est-il effectué dans tous les systèmes (backups inclus) ?", "severity": "major"},
               {"question": "Les destinataires des données sont-ils informés de la demande d'effacement ?", "severity": "minor"},
           ],
           evidence=["document", "log"]),

        _c("18", "Droit à la limitation du traitement",
           "La personne concernée a le droit d'obtenir la limitation du traitement lorsque l'exactitude des données "
           "est contestée, le traitement est illicite, ou le responsable n'a plus besoin des données.",
           threshold=0.7,
           weight=1.0,
           checklist=[
               {"question": "Une procédure de limitation du traitement existe-t-elle ?", "severity": "major"},
               {"question": "Les données en instance de limitation sont-elles clairement marquées ?", "severity": "minor"},
           ],
           evidence=["document", "log"]),

        _c("20", "Droit à la portabilité",
           "La personne concernée a le droit de recevoir ses données dans un format structuré, couramment utilisé "
           "et lisible par machine, et de les transmettre à un autre responsable.",
           threshold=0.7,
           weight=1.1,
           checklist=[
               {"question": "Le format d'export des données est-il structuré et lisible par machine (JSON, CSV) ?", "severity": "major"},
               {"question": "Un mécanisme de transfert direct entre responsables est-il disponible techniquement ?", "severity": "minor"},
           ],
           evidence=["document", "screenshot"]),

        _c("21", "Droit d'opposition",
           "La personne concernée a le droit de s'opposer à tout moment au traitement de ses données pour des "
           "raisons tenant à sa situation particulière, y compris le profilage.",
           threshold=0.7,
           weight=1.1,
           checklist=[
               {"question": "Une procédure d'exercice du droit d'opposition existe-t-elle ?", "severity": "critical"},
               {"question": "En cas d'opposition, le traitement est-il suspendu sauf motifs légitimes impérieux ?", "severity": "major"},
           ],
           evidence=["document", "log"]),
    ],
)

# ============================================================================
# Domain 3: Obligations du responsable (Chapitre IV, Art. 24-43)
# ============================================================================

_rgpd_obligations = build_domain(
    domain_id="rgpd_obligations",
    name="Obligations du responsable de traitement",
    regulation="RGPD",
    chapter="Chapitre IV, Art. 24-43",
    default_weight=0.10,
    criteria=[
        _c("24", "Responsabilité du responsable",
           "Le responsable met en œuvre des mesures techniques et organisationnelles appropriées pour s'assurer "
           "et pouvoir démontrer que le traitement est effectué conformément au RGPD.",
           threshold=0.7,
           weight=1.3,
           checklist=[
               {"question": "Des mesures techniques et organisationnelles sont-elles documentées et mises en œuvre ?", "severity": "critical"},
               {"question": "Le responsable peut-il démontrer la conformité (piste d'audit) ?", "severity": "critical"},
               {"question": "Ces mesures sont-elles régulièrement révisées et mises à jour ?", "severity": "major"},
           ],
           evidence=["document", "policy"]),

        _c("25", "Protection des données dès la conception et par défaut (Privacy by Design)",
           "Le responsable met en œuvre des mesures techniques et organisationnelles destinées à protéger les données "
           "dès la conception (privacy by design) et par défaut : minimisation des données, limitation de la durée, "
           "restrictions d'accès.",
           threshold=0.7,
           weight=1.4,
           checklist=[
               {"question": "La protection des données est-elle intégrée dès la conception de chaque nouveau traitement ?", "severity": "critical"},
               {"question": "Le traitement par défaut est-il celui qui implique le moins de données et le moins d'exposition possible ?", "severity": "major"},
               {"question": "Les exigences de privacy by design sont-elles intégrées dans les spécifications techniques ?", "severity": "major"},
           ],
           evidence=["document", "policy"]),

        _c("30", "Registre des activités de traitement",
           "Le responsable tient un registre de ses activités de traitement couvrant : finalités, catégories de données, "
           "catégories de destinataires, transferts internationaux, durées de conservation, mesures de sécurité.",
           threshold=0.8,
           weight=1.5,
           checklist=[
               {"question": "Un registre des traitements est-il tenu et à jour ?", "severity": "critical"},
               {"question": "Le registre contient-il toutes les informations requises par l'Art. 30(1) ?", "severity": "critical"},
               {"question": "Le registre est-il accessible à l'autorité de contrôle sur demande ?", "severity": "major"},
               {"question": "Le registre est-il mis à jour à chaque nouveau traitement ou modification ?", "severity": "major"},
           ],
           evidence=["registre", "document"]),

        _c("32", "Sécurité du traitement",
           "Le responsable met en œuvre les mesures techniques et organisationnelles appropriées pour assurer "
           "un niveau de sécurité adapté au risque : pseudonymisation, chiffrement, résilience, tests réguliers.",
           threshold=0.8,
           weight=1.5,
           checklist=[
               {"question": "Des mesures de chiffrement des données au repos et en transit sont-elles en place ?", "severity": "critical"},
               {"question": "La pseudonymisation est-elle utilisée lorsque possible ?", "severity": "major"},
               {"question": "Des tests de sécurité réguliers sont-ils effectués ?", "severity": "major"},
               {"question": "Un PRA (Plan de Reprise d'Activité) inclut-il la protection des données ?", "severity": "major"},
               {"question": "Les accès aux données sont-ils limités au strict nécessaire (principe du moindre privilège) ?", "severity": "critical"},
           ],
           evidence=["document", "policy", "log"]),
    ],
)

# ============================================================================
# Domain 4: Sous-traitants (Art. 26-31, 28)
# ============================================================================

_rgpd_sous_traitants = build_domain(
    domain_id="rgpd_sous_traitants",
    name="Sous-traitance et transfert de responsabilité",
    regulation="RGPD",
    chapter="Chapitre IV, Art. 26-31, 28",
    default_weight=0.10,
    criteria=[
        _c("28", "Sous-traitant (conditions et contrat)",
           "Lorsqu'un traitement est effectué par un sous-traitant, le responsable choisit un sous-traitant offrant "
           "des garanties suffisantes. Le traitement est régi par un contrat écrit définissant : objet, durée, nature, "
           "finalités, types de données, obligations du sous-traitant, assistance au responsable, suppression/renvoi.",
           threshold=0.8,
           weight=1.5,
           checklist=[
               {"question": "Un contrat écrit (ou document équivalent) existe-t-il avec chaque sous-traitant ?", "severity": "critical"},
               {"question": "Le contrat inclut-il les éléments obligatoires de l'Art. 28.3 (objet, durée, finalités, données, obligations) ?", "severity": "critical"},
               {"question": "Le sous-traitant a-t-il été évalué sur ses garanties de protection des données ?", "severity": "major"},
               {"question": "Le sous-traitant a-t-il informé le responsable en cas de violation de données ?", "severity": "major"},
           ],
           evidence=["contract", "dpa"]),

        _c("28.3", "Obligations contractuelles du sous-traitant",
           "Le sous-traitant traite les données uniquement selon les instructions documentées du responsable. "
           "Il ne les transmet pas à un tiers sans autorisation. Il assiste le responsable pour les demandes "
           "de droits, les violations, les AIPD.",
           threshold=0.7,
           weight=1.2,
           checklist=[
               {"question": "Le sous-traitant s'engage-t-il à ne traiter que sur instructions documentées ?", "severity": "critical"},
               {"question": "Le sous-traitant s'engage-t-il à ne pas sous-traiter sans autorisation préalable ?", "severity": "major"},
               {"question": "Le sous-traitant fournit-il une assistance pour les droits des personnes et les AIPD ?", "severity": "major"},
           ],
           evidence=["contract", "dpa"]),
    ],
)

# ============================================================================
# Domain 5: Transferts internationaux (Chapitre V, Art. 44-49)
# ============================================================================

_rgpd_transferts = build_domain(
    domain_id="rgpd_transferts",
    name="Transferts internationaux de données",
    regulation="RGPD",
    chapter="Chapitre V, Art. 44-49",
    default_weight=0.12,
    criteria=[
        _c("44", "Principe général des transferts",
           "Le transfert de données personnelles vers un pays tiers ou une organisation internationale n'est "
           "autorisé que si la Commission a décidé que ce pays assure un niveau de protection adéquat, ou si des "
           "garanties appropriées sont fournies.",
           threshold=0.8,
           weight=1.5,
           checklist=[
               {"question": "Tous les transferts internationaux de données ont-ils été identifiés et documentés ?", "severity": "critical"},
               {"question": "Les pays destinataires figurent-ils dans la liste des pays à protection adéquate ?", "severity": "critical"},
               {"question": "Pour les pays non adéquats, des garanties appropriées sont-elles en place (CSC, clauses contractuelles) ?", "severity": "critical"},
           ],
           evidence=["document", "contract", "registre"]),

        _c("46", "Transferts fondés sur des garanties appropriées",
           "En l'absence de décision d'adéquation, le transfert est possible via : clauses contractuelles types "
           "(CSC) approuvées par la Commission, règles internes contraignantes pour les entreprises (BCR), "
           "clauses contractuelles approuvées par une autorité de contrôle.",
           threshold=0.8,
           weight=1.4,
           checklist=[
               {"question": "Les clauses contractuelles types (CSC) de la Commission sont-elles signées avec les destinataires ?", "severity": "critical"},
               {"question": "Une analyse d'impact des transferts (TIA - Transfer Impact Assessment) a-t-elle été réalisée (Schrems II) ?", "severity": "critical"},
               {"question": "Des mesures complémentaires ont-elles été mises en place si nécessaires ?", "severity": "major"},
           ],
           evidence=["contract", "document"]),

        _c("49", "Dérogations pour les transferts",
           "Par dérogation, un transfert peut avoir lieu si : la personne a consenti, nécessaire à l'exécution d'un contrat, "
           "nécessaire pour des raisons importantes d'intérêt public, exercice de droits en justice.",
           threshold=0.7,
           weight=1.0,
           checklist=[
               {"question": "Si un transfert repose sur une dérogation, celle-ci est-elle documentée et justifiée ?", "severity": "major"},
               {"question": "Les dérogations sont-elles exceptionnelles et non systématiques ?", "severity": "major"},
           ],
           evidence=["document"]),
    ],
)

# ============================================================================
# Domain 6: AIPD / DPIA (Art. 35)
# ============================================================================

_rgpd_aipd = build_domain(
    domain_id="rgpd_aipd",
    name="Analyse d'impact (AIPD/DPIA)",
    regulation="RGPD",
    chapter="Chapitre IV, Art. 35",
    default_weight=0.10,
    criteria=[
        _c("35", "Analyse d'impact relative à la protection des données (AIPD)",
           "Le responsable réalise une AIPD lorsqu'un traitement est susceptible d'engendrer un risque élevé pour "
           "les droits et libertés : évaluation systématique des personnes, données sensibles à grande échelle, "
           "surveillance systématique d'une zone accessible au public.",
           threshold=0.7,
           weight=1.5,
           checklist=[
               {"question": "Les traitements à risque élevé ont-ils été identifiés ?", "severity": "critical"},
               {"question": "Une AIPD a-t-elle été réalisée pour chaque traitement à risque élevé ?", "severity": "critical"},
               {"question": "L'AIPD contient-elle : description systématique, évaluation de la nécessité, analyse des risques, mesures prévues ?", "severity": "critical"},
               {"question": "L'avis du DPO sur l'AIPD a-t-il été recueilli ?", "severity": "major"},
               {"question": "L'autorité de contrôle a-t-elle été consultée en cas de risque résiduel élevé ?", "severity": "major"},
           ],
           evidence=["pia", "document"]),
    ],
)

# ============================================================================
# Domain 7: Notification de violation (Art. 33-34)
# ============================================================================

_rgpd_violation = build_domain(
    domain_id="rgpd_violation",
    name="Notification de violation de données",
    regulation="RGPD",
    chapter="Chapitre IV, Art. 33-34",
    default_weight=0.08,
    criteria=[
        _c("33", "Notification à l'autorité de contrôle",
           "En cas de violation de données, le responsable la notifie à l'autorité de contrôle compétente dans les "
           "72 heures, sauf si la violation est peu probable qu'elle engendre un risque pour les droits.",
           threshold=0.8,
           weight=1.5,
           checklist=[
               {"question": "Une procédure de notification de violation existe-t-elle et est-elle testée ?", "severity": "critical"},
               {"question": "Le délai de 72 heures pour notification à l'autorité est-il respecté dans les tests ?", "severity": "critical"},
               {"question": "La notification inclut-elle : nature de la violation, catégories de personnes, DPO contact, conséquences, mesures ?", "severity": "major"},
           ],
           evidence=["document", "policy", "log"]),

        _c("34", "Communication aux personnes concernées",
           "Le responsable communique la violation aux personnes concernées lorsqu'elle est susceptible d'engendrer "
           "un risque élevé pour leurs droits, sauf si les données sont chiffrées ou si des mesures assurent l'impossibilité de l'identification.",
           threshold=0.7,
           weight=1.2,
           checklist=[
               {"question": "Les critères d'évaluation du risque pour les personnes sont-ils définis ?", "severity": "major"},
               {"question": "Un template de notification aux personnes concernées est-il préparé ?", "severity": "minor"},
           ],
           evidence=["document", "policy"]),
    ],
)

# ============================================================================
# Domain 8: DPO (Art. 37-39)
# ============================================================================

_rgpd_dpo = build_domain(
    domain_id="rgpd_dpo",
    name="Délégué à la protection des données (DPO)",
    regulation="RGPD",
    chapter="Chapitre IV, Art. 37-39",
    default_weight=0.08,
    criteria=[
        _c("37", "Désignation du DPO",
           "Le responsable et le sous-traitant désignent un DPO dans les cas suivants : traitement par une autorité publique, "
           "activités de base nécessitant un suivi régulier et systématique des personnes à grande échelle, "
           "traitement à grande échelle de données sensibles.",
           threshold=0.7,
           weight=1.3,
           checklist=[
               {"question": "Un DPO a-t-il été désigné (ou l'obligation de désignation a-t-elle été évaluée) ?", "severity": "critical"},
               {"question": "Les coordonnées du DPO sont-elles communiquées à l'autorité de contrôle et publiées ?", "severity": "major"},
               {"question": "Le DPO dispose-t-il des ressources et de l'indépendance nécessaires ?", "severity": "major"},
           ],
           evidence=["document"]),

        _c("39", "Tâches du DPO",
           "Le DPO informe et conseille le responsable, contrôle le respect du RGPD, coopère avec l'autorité de contrôle, "
           "tient compte du risque élevé et agit comme point de contact.",
           threshold=0.7,
           weight=1.2,
           checklist=[
               {"question": "Le DPO a-t-il accès aux processus de traitement pour exercer sa mission ?", "severity": "major"},
               {"question": "Le DPO a-t-il produit un rapport d'activité annuel ?", "severity": "minor"},
               {"question": "Le DPO n'est-il pas en situation de conflit d'intérêts ?", "severity": "critical"},
           ],
           evidence=["document", "policy"]),
    ],
)

# ============================================================================
# Domain 9: Profilage et décisions automatisées (Art. 22)
# ============================================================================

_rgpd_profilage = build_domain(
    domain_id="rgpd_profilage",
    name="Profilage et décisions automatisées",
    regulation="RGPD",
    chapter="Chapitre III, Art. 22",
    default_weight=0.08,
    criteria=[
        _c("22", "Décisions individuelles automatisées, y compris le profilage",
           "La personne concernée a le droit de ne pas faire l'objet d'une décision fondée exclusivement sur un "
           "traitement automatisé produisant des effets juridiques la concernant de manière similaire, sauf "
           "consentement explicite, nécessité contractuelle, autorisation légale.",
           threshold=0.7,
           weight=1.5,
           checklist=[
               {"question": "Les systèmes de prise de décision automatisée ont-ils été identifiés ?", "severity": "critical"},
               {"question": "Pour chaque système, le droit à une intervention humaine est-il garanti ?", "severity": "critical"},
               {"question": "Les personnes concernées sont-elles informées de l'existence du profilage ?", "severity": "major"},
               {"question": "Des mesures de safeguard (procédures, informations, droits) sont-elles en place ?", "severity": "major"},
           ],
           evidence=["document", "policy"]),
    ],
)

# ============================================================================
# Domain 10: Coopération avec l'autorité (Art. 31, 36, 77-82)
# ============================================================================

_rgpd_cooperation = build_domain(
    domain_id="rgpd_cooperation",
    name="Coopération avec l'autorité de contrôle",
    regulation="RGPD",
    chapter="Art. 31, 36, 77-82",
    default_weight=0.10,
    criteria=[
        _c("31", "Coopération avec l'autorité de contrôle",
           "Le responsable et le sous-traitant coopèrent avec l'autorité de contrôle à sa demande, y compris pour "
           "l'accès aux données et aux locaux.",
           threshold=0.6,
           weight=1.3,
           checklist=[
               {"question": "L'organisation est-elle prête à répondre à une demande de l'autorité de contrôle dans les délais ?", "severity": "major"},
               {"question": "L'accès aux données et aux locaux peut-il être facilité si demandé ?", "severity": "minor"},
           ],
           evidence=["document", "policy"]),

        _c("77", "Droit à une action judiciaire",
           "Toute personne concernée a le droit d'introduire une réclamation auprès d'une autorité de contrôle "
           "et de recevoir un réexamen de l'affaire.",
           threshold=0.6,
           weight=1.0,
           checklist=[
               {"question": "Les personnes concernées sont-elles informées de leur droit de réclamation auprès de l'autorité de contrôle ?", "severity": "major"},
               {"question": "Le DPO ou le responsable est-il le point de contact pour les réclamations ?", "severity": "minor"},
           ],
           evidence=["document", "screenshot"]),

        _c("82", "Droit à réparation et responsabilité",
           "Toute personne ayant subi un dommage du fait d'un traitement illicite a le droit d'obtenir réparation "
           "du responsable ou du sous-traitant.",
           threshold=0.6,
           weight=1.0,
           checklist=[
               {"question": "Le responsable est-il assuré pour les risques liés au traitement des données personnelles ?", "severity": "major"},
               {"question": "Une procédure de gestion des plaintes et réclamations est-elle en place ?", "severity": "minor"},
           ],
           evidence=["document", "policy"]),
    ],
)


# ============================================================================
# Export: all RGPD domains
# ============================================================================

RGPD_DOMAINS: list[CriteriaDomain] = [
    _rgpd_principes,
    _rgpd_droits,
    _rgpd_obligations,
    _rgpd_sous_traitants,
    _rgpd_transferts,
    _rgpd_aipd,
    _rgpd_violation,
    _rgpd_dpo,
    _rgpd_profilage,
    _rgpd_cooperation,
]
