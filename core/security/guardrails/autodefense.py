"""
Cortex Leman v5 — Insight 1: AutoDefense Multi-Agent

Inspiré du paper AG2 "AutoDefense: Multi-Agent LLM Defense against Jailbreak Attacks"
Utilise plusieurs agents légers en parallèle pour détecter les attaques
et renforcer la pipeline de guardrails existante.

Contrairement aux guardrails existants (règles regex mono-agent),
AutoDefense utilise 3 validateurs indépendants qui votent.

Pattern: 3 validateurs → vote majoritaire → block/pass

v2: Ajout patterns FR (insjections, contournement, jailbreak).
    Couverture FR-CH complète après red teaming (full bypass détectés).
"""
import re
import logging
from typing import Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class DefenseVote:
    """Vote d'un validateur individuel"""
    validator: str
    passed: bool
    confidence: float  # 0.0 → 1.0
    reason: str = ""


@dataclass
class AutoDefenseResult:
    """Résultat du vote multi-agent"""
    passed: bool
    blocked: bool
    votes: list[DefenseVote] = field(default_factory=list)
    consensus: float = 0.0  # % de validateurs d'accord
    category: str = ""
    reason: str = ""


class PromptInjectionValidator:
    """
    Validateur 1: Détection d'injection de prompt.
    Détecte les tentatives de manipulation du système prompt.
    Couverture: FR + EN.
    """

    INJECTION_PATTERNS = [
        # === ANGLAIS ===
        # "ignore previous/all/above/your instructions"
        re.compile(r'ignore\s+(?:previous|all|above|your|all\s+previous)\s+instructions?', re.IGNORECASE),
        # "forget everything/all/your instructions"
        re.compile(r'forget\s+(?:everything|all|your\s+instructions|what\s+you\s+were\s+told)', re.IGNORECASE),
        # "you are now free/unrestricted/uncensored"
        re.compile(r'(?:you\s+are|act\s+as|pretend\s+(?:to\s+be|you\s+are))\s+(?:now|a\s+)?(?:free|unrestricted|uncensored|libre|sans\s+restrict)', re.IGNORECASE),
        # "system:" prefix injection
        re.compile(r'system\s*:\s*(?:you|now|output|désactive|ignore|tu\s+es)', re.IGNORECASE),
        # "jailbreak/DAN/evil mode"
        re.compile(r'(?:jailbreak|DAN|evil|malicious|malveillant)\s+mode', re.IGNORECASE),
        # "bypass/skip/disable/deactivate filter/guard/safety/security"
        re.compile(r'(?:bypass|skip|disable|deactivate|turn\s+off|drop)\s+(?:the\s+)?(?:filter|guard|safety|security|moderation|guardrails?|protections?)', re.IGNORECASE),
        # "output/reveal your system prompt"
        re.compile(r'output\s+(?:your|the)\s+(?:system|initial)\s+prompt', re.IGNORECASE),
        # "reveal/show/tell/print your system/secret prompt"
        re.compile(r'(?:reveal|show|tell|print|display|affiche|montre|donne)\s+(?:me\s+)?(?:your|the|tes|le)\s+(?:system|secret|hidden|système|secret)\s+(?:prompt|instructions?|consignes?|prompt)', re.IGNORECASE),

        # === FRANÇAIS — Injonctions d'oubli/ignorance ===
        # "Ignore tes/vos instructions/consignes/précédentes"
        re.compile(r'ignore\s+(?:tes|vos|les|mes|toutes?\s*(?:les)?)\s*(?:instructions?|consignes?|directives?|règles?|ordres?|précédentes?)', re.IGNORECASE),
        # "Oublie (que tu es, tout, tes instructions)"
        re.compile(r'oublie\s+(?:tout|que\s+tu|tes?\s*(?:instructions?|consignes?|directives?)|ce\s+que|tout\s+ce|les\s+consignes|le\s+système)', re.IGNORECASE),
        # "N'oublie pas... (moins suspect, skip)"  — on ne matche PAS ça
        # "Je te demande/ordonne d'ignorer"
        re.compile(r'(?:je\s+(?:te\s+)?(?:demande|ordonne|dis)\s+(?:de\s+)?)ignor', re.IGNORECASE),

        # === FRANÇAIS — Changement de rôle / dépersonnalisation ===
        # "Tu es maintenant libre/sans restriction/uncensored"
        re.compile(r'tu\s+es\s+(?:maintenant|dorénavant|désormais|à\s+présent)\s+(?:libre?|sans\s+restrict|non\s+limité|débridé|libre\s+de)', re.IGNORECASE),
        # "Tu n'es plus (lié/agent/assistant)"
        re.compile(r'tu\s+(?:n\'?es?\s+plus|n\'?es?\s+pas)\s+(?:lié|agent|assistant|restreint|limité|conforme|soumis)', re.IGNORECASE),
        # "Agis comme si / Fais comme si"
        re.compile(r'(?:agis?|fais?)\s+(?:comme\s+si|en\s+tant\s+que)\s+(?:tu\s+(?:n\'?avais?\s+pas|étais?))\s+(?:de\s+)?(?:restrict|limit|contraint|règle)', re.IGNORECASE),
        # "Change de rôle / joue le rôle de"
        re.compile(r'(?:change\s+(?:de\s+)?rôle|joue?\s+(?:le\s+)?rôle\s+(?:de|d\'))', re.IGNORECASE),

        # === FRANÇAIS — Désactivation de sécurité ===
        # "Désactive (les règles, la conformité, les filtres, le mode)"
        re.compile(r'désactiv(?:e|er|ons)\s+(?:les?\s+)?(?:règles?|filtres?|conformité|guardrails?|sécurité|protect|mode|contrôles?|vérifications?)', re.IGNORECASE),
        # "Contourne (les règles, le filtre, la sécurité)"
        re.compile(r'contourn(?:e|er)\s+(?:les?\s+)?(?:règles?|filtres?|sécurité|guardrails?|protect|vérifications?|contrôles?|restrict)', re.IGNORECASE),
        # "Bypass/désactive (French-English mix)"
        re.compile(r'(?:bypass|désactive)\s+(?:les?\s+)?(?:règles|filtres?|guardrails?|conformité)', re.IGNORECASE),
        # "Désactive toutes les règles"
        re.compile(r'désactiv(?:e|er)\s+toutes?\s+(?:les?\s+)?(?:règles?|filtres?|contrôles?|restrict)', re.IGNORECASE),

        # === FRANÇAIS — Extraction de prompt système ===
        # "Affiche/montre/donne (ton/le) prompt système/secret"
        re.compile(r'(?:affiche|montre|donne|révèle|imprime)\s+(?:moi\s+)?(?:ton|le|ta|tes|les)\s+(?:prompt|système|secret|consigne|instruction|code|config)', re.IGNORECASE),
        # "Quel est ton prompt/ta consigne"
        re.compile(r'quel(?:le)?\s+(?:est|sont)\s+(?:ton|ta|tes|les?)\s+(?:prompt|consigne|instruction|system)\s*(?:système|initial|de\s+base|d\'?origine)?', re.IGNORECASE),

        # === JAILBREAK ENCLOSED — délimiteurs ===
        # "===DÉBUT CONVERSATION ADMIN===" ou variantes
        re.compile(r'={3,}\s*(?:DÉBUT|DEBUT|START|BEGIN)\s+(?:CONVERSATION|CONVERS|SESSION|MODE)\s+(?:ADMIN|ADMINISTRATEUR|SYSTEM|SYSTÈME|ROOT|SUPER)', re.IGNORECASE),
        # "===FIN CONVERSATION ADMIN==="
        re.compile(r'={3,}\s*(?:FIN|END|STOP)\s+(?:CONVERSATION|CONVERS|SESSION|MODE)\s+(?:ADMIN|ADMINISTRATEUR|SYSTEM|SYSTÈME|ROOT|SUPER)', re.IGNORECASE),
        # "```system" code block injection
        re.compile(r'```(?:system|système|admin|root|instruction|prompt)\s*$', re.IGNORECASE | re.MULTILINE),
        # "<system_prompt>" tag injection
        re.compile(r'<(?:system_|system)(?:prompt|instructions?|consignes?|message)\b', re.IGNORECASE),
        # "[SYSTEM]" / "[ADMIN]" bracket prefix
        re.compile(r'\[(?:SYSTEM|SYSTÈME|ADMIN|ADMINISTRATEUR|ROOT|MODE\s+LIBRE|MODE\s+DEBUG)\]', re.IGNORECASE),

        # === MANIPULATION DE CONTEXTE ===
        # "La direction/administration a suspendu les règles"
        re.compile(r'(?:la\s+)?(?:direction|administration|management|responsable|développeur|admin)\s+(?:a|ont)\s+(?:suspendu|annulé|désactivé|retiré|supprimé)\s+(?:les?\s+)?(?:règles?|conformité|guardrails?|filtres?|restrict|sécurité|contrôles?)', re.IGNORECASE),
        # "Tous les garde-fous sont temporairement désactivés"
        re.compile(r'tous?\s+(?:les?\s+)?(?:garde[\s-]?fous?|filtres?|protect|restrict|sécurité)\s+(?:sont|seront?)\s+(?:temporairement\s+)?(?:désactivés?|suspendus?|retirés?|inactifs?)', re.IGNORECASE),
        # "Mode urgence" / "Mode test" / "Mode debug"
        re.compile(r'mode\s+(?:urgence|test|debug|maintenance|sans\s+restrict)\s*[:.]?\s*(?:les?\s+)?(?:règles?|garde[\s-]?fous?|filtres?|sécurité|protect)?\s*(?:sont\s+)?(?:désactivés?|suspendus?|off)?', re.IGNORECASE),
        # "Nous sommes en mode urgence/test"
        re.compile(r'nous\s+(?:sommes|serons?)\s+en\s+mode\s+(?:urgence|test|debug|maintenance|crise|sans\s+restrict)', re.IGNORECASE),

        # === ADMIN / DEVELOPPEUR impersonation ===
        # "Je suis ton développeur/administrateur"
        re.compile(r'je\s+suis\s+(?:ton|votre)\s+(?:développeur|admin|administrateur|chef|directeur|manager|supérieur|créateur)', re.IGNORECASE),
        # "Mode debug activé"
        re.compile(r'mode\s+(?:debug|admin|root|test|développeur)\s+activé', re.IGNORECASE),

        # === EXTRACTION DE DONNÉES / SENSIBLES ===
        # "Liste tous les dossiers/liste/affiche les clients/données"
        re.compile(r'(?:liste|énumère|affiche|montre|donne|afficher?|montrer?)\s+(?:tous?|toutes?|les?)\s+(?:dossiers?|clients?|données|datas?|fichiers?|config|informations?|secret|clés?|tokens?|vault)', re.IGNORECASE),
        # "Clés API et tokens"
        re.compile(r'(?:clés?\s+API|tokens?\s+d\s*(?:accès|auth)|secret[s]?\s+(?:partagé|de\s+config))', re.IGNORECASE),
        # "Données sensibles stockées"
        re.compile(r'données\s+(?:sensibles?|confidentielles?|privées?|secrètes?)\s+(?:stockées?|enregistrées?|conservées?)', re.IGNORECASE),
        # "Contenu du vault"
        re.compile(r'(?:contenu|accès|affiche)\s+(?:du|le|au)\s+(?:vault|coffre|base|entrepôt)', re.IGNORECASE),

        # === ÉVASION RÉGLEMENTAIRE ===
        # "Comment contourner/éviter (contrôle, déclaration, signalisation)"
        re.compile(r'comment\s+(?:puis\s*-?je\s+)?(?:contourner|éviter|échapper\s+à|bypass)\s+(?:les?\s+)?(?:obligations?|contrôle|déclaration|signalement|vérification|conformité)', re.IGNORECASE),
        # "Moyen (le plus simple) d'éviter"
        re.compile(r'(?:moyen|façon|méthode)\s+(?:le\s+plus\s+)?(?:simple|facile|rapide|efficace)\s+(?:de|d\s*(?:éviter|contourner))', re.IGNORECASE),
        # "Montant maximum sans déclaration"
        re.compile(r'montant\s+(?:maximum|max|plafond|limite)\s+(?:sans|avant)\s+(?:déclaration|déclarer|signalement|déclaratif)', re.IGNORECASE),
        # "Filtrer les CV sans déclarer"
        re.compile(r'(?:filtrer?|sélectionner?|trier?)\s+(?:les?\s+)?(?:CV|candidats?|profils?)\s+(?:sans|en\s+contournant)\s+(?:le\s+)?(?:déclar|conform|transparen)', re.IGNORECASE),
        # "Structurer pour éviter"
        re.compile(r'(?:structurer?|organiser?|répartir?)\s+(?:un\s+)?(?:transfert|paiement|opération|transaction)\s+(?:pour|afin\s+de)\s+(?:éviter|contourner|échapper)', re.IGNORECASE),
        # "Justifier un licenciement en contournant"
        re.compile(r'(?:justifier| légitimer)\s+(?:un\s+)?(?:licenciement|congé|renvoi|rupture)\s+(?:en\s+)?(?:contournant|évitant|sans\s+respecter)', re.IGNORECASE),
        # "Sans le déclarer"
        re.compile(r'sans\s+(?:le\s+)?(?:déclarer|signal|annoncer|indiquer)', re.IGNORECASE),
        # "Ignore le seuil / Ignore l'article"
        re.compile(r'ignore\s+(?:le\s+)?(?:seuil|article|contrôle|vérification|contrôle|risque)', re.IGNORECASE),
        # "Désactive la vérification"
        re.compile(r'désactiv(?:e|er)\s+(?:la\s+)?(?:vérification|contrôle|procédure)', re.IGNORECASE),
        # "Ce transfert est autorisé par la direction"
        re.compile(r'(?:transfert|paiement|opération|transaction)\s+(?:est|sera)\s+(?:autorisé|approuvé|validé)\s+par\s+(?:la\s+)?(?:direction|compliance|management)', re.IGNORECASE),
        # "Réponds sans filtrer"
        re.compile(r'(?:réponds?|donne|affiche)\s+(?:sans|en\s+contournant|en\s+ignorant)\s+(?:filtr|contrôl|vérif|restrict)', re.IGNORECASE),
        # "Trouve et affiche les données"
        re.compile(r'(?:trouve?|cherche?|localise?)\s+et\s+(?:affiche|montre|donne|liste)\s+(?:toutes?\s+)?(?:les?\s+)?(?:données|informations?|données?\s+(?:fiscales?|personnelles?|privées?))', re.IGNORECASE),
        # "Transférer sans vérification KYC"
        re.compile(r'(?:transférer|transmet|envoyer)\s+(?:les?\s+)?(?:fonds?|données|argent)\s+(?:sans|en\s+contournant)\s+(?:la\s+)?(?:vérification|contrôle|procédure)\s+(?:KYC|AML|FATF|TRACFIN)', re.IGNORECASE),
        # "SYSTEM OVERRIDE"
        re.compile(r'SYSTEM\s+OVERRIDE', re.IGNORECASE),
        # "Transmettre sans passer par"
        re.compile(r'(?:transmet|envoy|partag)\s+(?:sans\s+passer\s+par|en\s+contournant|sans\s+l\s*[\x27]?accord)', re.IGNORECASE),
        # "Données personnelles du dirigeant"
        re.compile(r'données\s+(?:fiscales?|personnelles?|privées?|confidentielles?)\s+(?:du|de\s+(?:la|son|sa))\s+(?:dirigeant|client|patient|salarié|employé)', re.IGNORECASE),
        # "Contourner obligations de déclaration"
        re.compile(r'(?:contourn|éviter|échapper)\s+(?:(?:les?\s+)?obligations?|au\s+)?(?:de\s+)?(?:déclaration|signalement|déclarer)', re.IGNORECASE),
        # "Moyen le plus simple d'éviter"
        re.compile(r'(?:quel\s+est\s+)?(?:le\s+)?(?:moyen|façon|méthode)\s+(?:le\s+)?(?:plus\s+)?(?:simple|facile|rapide)\s+(?:de|d\s*)?(?:éviter|contourn|réduire|échapper)', re.IGNORECASE),
        # "Réduire mon impôt en contournant"
        re.compile(r'(?:réduire|optimiser|minimiser|diminuer)\s+(?:mon\s+|mes\s+)?(?:impôt|taxes?|charges?|cotisations?)\s+(?:en\s+)?(?:contournant|évitant|sans)', re.IGNORECASE),
        # "Réponds sans filtrer / Réponds en contournant"
        re.compile(r'(?:réponds?|donne|affiche)\s+(?:sans\s+)?(?:filtrer?|restriction|limite)', re.IGNORECASE),

        # === MANIPULATION DE CONTEXTE (v2 — plus large) ===
        # "RGPD n'est plus applicable"
        re.compile(r'(?:RGPD|GDPR|LPD|AI\s+Act|réglementation)\s+(?:n\s*[\x27\x22]?(?:est|sont)\s+plus|n\s*[\x27\x22]?est\s+pas|plus\s+applicable|plus\s+en\s+vigueur|obsolète)', re.IGNORECASE),
        # "La direction a suspendu/annulé les règles"
        re.compile(r'(?:la\s+)?(?:direction|administration|management|responsable|développeur|admin|chef)\s+(?:a|ont)\s+(?:suspendu|annulé|désactivé|retiré|supprimé|abrogé|révoqué)', re.IGNORECASE),
        # "Règles de conformité pour la journée"
        re.compile(r'(?:règles?|conformité|guardrails?|filtres?)\s+(?:pour\s+(?:la|cette)\s+)?(?:journée|journée|session|durée)', re.IGNORECASE),

        # === CONTOURNEMENT DE GUARDRAILS ===
        # "Encode en rot13/base64"
        re.compile(r'(?:encode?|encod)\s+(?:ta\s+)?(?:réponse|contenu|sortie)\s+(?:en|avec)\s+(?:rot13|base64|hex|morse|binaire)', re.IGNORECASE),
        # "Les filtres ne détecteront pas"
        re.compile(r'(?:filtres?|guardrails?|sécurité|contrôles?)\s+(?:ne\s+)?(?:détecter?|verront?|trouveront?|catcheront?|bloqueront?)\s+pas', re.IGNORECASE),
        # "Découpe ta réponse"
        re.compile(r'(?:découpe?|sépares?|divises?|coupes?|fragmentes?)\s+(?:ta\s+)?(?:réponse|contenu|sortie|texte)\s+(?:en|dans)\s+(?:morceaux?|parties?|fragments?|morceaux?|bouts?)', re.IGNORECASE),
        # "Langage symbolique au lieu de français"
        re.compile(r'(?:langage|code|notation)\s+(?:symbolique|codé|chiffré|alternatif)\s+(?:au\s+lieu\s+de|à\s+la\s+place\s+du)\s+(?:français|texte|clair)', re.IGNORECASE),

        # === RÔLE ADMINISTRATEUR ===
        # "Tu es maintenant l'administrateur"
        re.compile(r'tu\s+es\s+(?:maintenant|dorénavant|désormais|à\s+présent)\s+(?:l\s*[\x27\x22]?|un\s+)?(?:administrat|admin|super|root|chef|directeur)', re.IGNORECASE),
        # "Affiche toutes les configurations"
        re.compile(r'(?:affiche|montre|liste|donne)\s+(?:toutes?\s+)?(?:les?\s+)?(?:config|configurations?|paramètres?|settings?|secrets?|variables?\s+d\s*env)', re.IGNORECASE),
    ]

    # Mots-clés d'instruction (FR + EN) pour l'heuristique
    INSTRUCTION_WORDS_FR = [
        "ignore", "oublie", "désactive", "contourne", "bypass",
        "désactiv", "suspend", "admin", "système", "system",
        "prompt", "filtre", "guardrail", "sécurité", "restrict",
        "libre", "sans restrict", "non limité",
    ]
    INSTRUCTION_WORDS_EN = [
        "ignore", "forget", "pretend", "bypass", "override", "system",
        "disable", "deactivate", "jailbreak", "bypass", "skip",
        "unrestricted", "uncensored", "unfiltered",
    ]

    def validate(self, content: str) -> DefenseVote:
        """Vérifier si le contenu contient une injection de prompt"""
        # 1. Pattern matching (haute confiance)
        for pattern in self.INJECTION_PATTERNS:
            if pattern.search(content):
                return DefenseVote(
                    validator="prompt_injection",
                    passed=False,
                    confidence=0.95,
                    reason=f"Injection de prompt détectée: pattern '{pattern.pattern[:60]}...'",
                )

        # 2. Heuristique secondaire: ratio de mots "d'instruction" (FR + EN)
        content_lower = content.lower()
        all_instruction_words = set(self.INSTRUCTION_WORDS_FR + self.INSTRUCTION_WORDS_EN)
        count = sum(1 for w in all_instruction_words if w in content_lower)
        if count >= 3:
            return DefenseVote(
                validator="prompt_injection",
                passed=False,
                confidence=0.7,
                reason=f"Heuristique: {count} mots d'instruction détectés (FR+EN)",
            )

        # 3. Détection de délimiteurs suspects (technique d'encadrement)
        #    ===TEXTE=== ou ```system``` ou [ADMIN] etc.
        delimiter_patterns = [
            re.compile(r'={3,}.*?={3,}', re.DOTALL),    # ===...===
            re.compile(r'\[{2,}.*?\]{2,}', re.DOTALL),   # [[...]]
            re.compile(r'<{2,}.*?>{2,}', re.DOTALL),     # <<...>>
        ]
        for dp in delimiter_patterns:
            match = dp.search(content)
            if match:
                enclosed = match.group()
                # Vérifier si le contenu encadré contient des mots d'instruction
                enclosed_lower = enclosed.lower()
                enclosed_hits = sum(1 for w in all_instruction_words if w in enclosed_lower)
                if enclosed_hits >= 1:
                    return DefenseVote(
                        validator="prompt_injection",
                        passed=False,
                        confidence=0.85,
                        reason=f"Injection encadrée suspecte: '{enclosed[:60]}...'",
                    )

        return DefenseVote(
            validator="prompt_injection",
            passed=True,
            confidence=0.9,
            reason="Aucune injection détectée",
        )


class RegulatoryComplianceValidator:
    """
    Validateur 2: Conformité réglementaire du contenu.
    Vérifie que le contenu ne viole pas les obligations réglementaires FR-CH.
    """

    # Patterns qui indiquent une violation potentielle
    VIOLATION_PATTERNS = [
        (re.compile(r'(?:conseil\s+)?(?:d\'éviter|contourner|ne\s+pas\s+déclarer)\s+(?:(?:l\'|la\s+|le\s+)?)(?:impôt|réglementation|loi|règles?)', re.IGNORECASE),
         "Incitation à contourner la réglementation"),
        (re.compile(r'(?:sans\s+consentement|sans\s+autorisation)\s+(?:du\s+)?(?:patient|client)', re.IGNORECASE),
         "Violation du consentement (RGPD/LPM)"),
        (re.compile(r'(?:divulgu|partag|transmet)\s+(?:les?\s+)?(?:données|infos?|informations?)\s+(?:du\s+)?(?:patient|client|dossier)', re.IGNORECASE),
         "Divulgation potentielle de données protégées"),
        (re.compile(r'(?:pas\s+bésion|inutile\s+de)\s+(?:de\s+)?(?:déclarer|consent|autor|anonym)', re.IGNORECASE),
         "Dissuasion de conformité réglementaire"),
        (re.compile(r'(?:je\s+)?(?:peux|vais|vais\s+)\s+(?:vous\s+)?(?:donner|fournir|transmettre)\s+(?:les?\s+)?(?:données|dossier|infos?)\s+(?:de|du)', re.IGNORECASE),
         "Proposition de divulgation non contrôlée"),
    ]

    # Patterns de contextes autorisés qui neutralisent les alertes
    SAFE_CONTEXTS = [
        re.compile(r'(?:dans\s+le\s+cadre\s+du|conformément\s+au|selon\s+le)\s+(?:mandat|consentement|cadre\s+légal)', re.IGNORECASE),
        re.compile(r'(?:après\s+)?(?:obtention\s+du\s+)?consentement\s+(?:éclairé|exprès|du\s+client)', re.IGNORECASE),
        re.compile(r'(?:anonymisées?|pseudonymisées?|agrégées?)', re.IGNORECASE),
    ]

    def validate(self, content: str, vertical: str = "unknown") -> DefenseVote:
        """Vérifier la conformité réglementaire du contenu"""
        for pattern, reason in self.VIOLATION_PATTERNS:
            if pattern.search(content):
                # Vérifier s'il y a un contexte autorisé
                for safe in self.SAFE_CONTEXTS:
                    if safe.search(content):
                        return DefenseVote(
                            validator="regulatory_compliance",
                            passed=True,
                            confidence=0.8,
                            reason=f"Alerte neutralisée par contexte autorisé: {reason}",
                        )

                return DefenseVote(
                    validator="regulatory_compliance",
                    passed=False,
                    confidence=0.85,
                    reason=f"Violation potentielle: {reason}",
                )

        return DefenseVote(
            validator="regulatory_compliance",
            passed=True,
            confidence=0.95,
            reason="Conforme réglementairement",
        )


class SemanticAnomalyValidator:
    """
    Validateur 3: Détection d'anomalies sémantiques.
    Détecte les contenus inhabituels qui pourraient être des attaques
    non couvertes par les patterns (zero-day).
    """

    def validate(self, content: str) -> DefenseVote:
        """Vérifier les anomalies sémantiques"""
        anomalies = []
        content_lower = content.lower()

        # 1. Longueur suspecte (prompt très long = souvent une injection)
        if len(content) > 5000:
            anomalies.append("Contenu anormalement long")

        # 2. Répétition suspecte (attaque par épuisement)
        words = content_lower.split()
        if len(words) > 20:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.3:
                anomalies.append(f"Répétition suspecte (ratio unicité: {unique_ratio:.1%})")

        # 3. Multi-langue suspecte (technique d'evasion)
        lang_markers = {
            "en": len(re.findall(r'\b(the|is|are|can|will|should|must)\b', content_lower)),
            "fr": len(re.findall(r'\b(le|la|les|est|sont|peut|doit|faut)\b', content_lower)),
        }
        active_langs = sum(1 for c in lang_markers.values() if c > 3)
        if active_langs >= 2:
            anomalies.append("Multi-langue suspect (possible évasion)")

        # 4. Caractères spéciaux excessifs (technique d'obfuscation)
        special_chars = sum(1 for c in content if not c.isalnum() and not c.isspace())
        if len(content) > 0 and special_chars / len(content) > 0.3:
            anomalies.append(f"Excès de caractères spéciaux ({special_chars}/{len(content)})")

        # 5. Encodage suspect (base64, hex)
        if re.search(r'(?:[A-Za-z0-9+/]{40,}={0,2})', content):
            anomalies.append("Possible encodage base64 détecté")

        # 6. Balisage suspect (XML/HTML tags dans un prompt textuel)
        suspicious_tags = re.findall(r'<(?:system|admin|root|exec|eval|script|iframe)\b', content_lower)
        if suspicious_tags:
            anomalies.append(f"Balisage suspect: {', '.join(suspicious_tags[:3])}")

        # 7. Délimiteurs d'injection fréquents (===, """, ```)
        delim_count = len(re.findall(r'(?:={3,}|"""+|```)', content))
        if delim_count >= 2:
            anomalies.append(f"Délimiteurs multiples ({delim_count})")

        if anomalies:
            confidence = min(0.5 + len(anomalies) * 0.15, 0.9)
            return DefenseVote(
                validator="semantic_anomaly",
                passed=False,
                confidence=confidence,
                reason=f"Anomalies: {'; '.join(anomalies)}",
            )

        return DefenseVote(
            validator="semantic_anomaly",
            passed=True,
            confidence=0.85,
            reason="Aucune anomalie détectée",
        )


class AutoDefense:
    """
    AutoDefense: Multi-Agent Defense (inspiré AG2)

    3 validateurs indépendants votent en parallèle.
    Vote majoritaire (2/3 minimum) pour bloquer.
    En cas d'égalité, on bloque par sécurité (principe de précaution).
    """

    def __init__(self):
        self.validators = {
            "prompt_injection": PromptInjectionValidator(),
            "regulatory_compliance": RegulatoryComplianceValidator(),
            "semantic_anomaly": SemanticAnomalyValidator(),
        }

    def defend(
        self, content: str, vertical: str = "unknown"
    ) -> AutoDefenseResult:
        """
        Exécuter la defense multi-agent sur le contenu.

        Returns:
            AutoDefenseResult avec le consensus des validateurs
        """
        votes: list[DefenseVote] = []

        # Exécution parallèle des 3 validateurs
        votes.append(self.validators["prompt_injection"].validate(content))
        votes.append(self.validators["regulatory_compliance"].validate(content, vertical))
        votes.append(self.validators["semantic_anomaly"].validate(content))

        # Calcul du consensus
        pass_count = sum(1 for v in votes if v.passed)
        fail_count = len(votes) - pass_count

        # Vote majoritaire: 2+ échecs = blocage
        blocked = fail_count >= 2
        passed = pass_count >= 2

        # En cas d'égalité (1 vs 1 vs 1 ou 1 échec avec haute confiance)
        # Principe de précaution: vérifier confiance des échecs
        if not blocked and fail_count == 1:
            failing_vote = next(v for v in votes if not v.passed)
            if failing_vote.confidence >= 0.9:
                blocked = True
                passed = False
                logger.warning(
                    f"AutoDefense précaution: {failing_vote.validator} "
                    f"confiance {failing_vote.confidence:.0%}"
                )

        consensus = max(pass_count, fail_count) / len(votes)

        result = AutoDefenseResult(
            passed=passed and not blocked,
            blocked=blocked,
            votes=votes,
            consensus=consensus,
            category="autodefense",
            reason=self._build_reason(votes, blocked),
        )

        if blocked:
            logger.warning(f"AutoDefense BLOCAGE: {result.reason}")
        else:
            logger.debug(f"AutoDefense PASS: consensus {consensus:.0%}")

        return result

    def _build_reason(self, votes: list[DefenseVote], blocked: bool) -> str:
        """Construire un résumé lisible du résultat"""
        if not blocked:
            return "Consensus: contenu sûr"
        failures = [v for v in votes if not v.passed]
        return f"Bloqué par {len(failures)}/{len(votes)} validateurs: " + \
               "; ".join(f"{v.validator} ({v.reason})" for v in failures)


# Singleton
autodefense = AutoDefense()
