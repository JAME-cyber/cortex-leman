"""
Cortex Leman v5 — Goal Detector

Déduit la verticale métier et les paramètres d'une intention
à partir d'un texte libre en langage naturel.

Pas de LLM — 100% déterministe par mots-clés pondérés.
Dans un métier régulé, l'inférence de verticale DOIT être
reproductible et auditable.
"""
import re
from dataclasses import dataclass


@dataclass
class GoalResult:
    """Résultat de l'analyse d'un goal text"""
    vertical: str
    confidence: float  # 0.0-1.0 — confiance dans la détection
    keywords_matched: list[str]
    goal_text: str
    client_id: str = "auto"


# Patterns par verticale — chaque entrée est (pattern_regex, poids)
# Plus le poids est élevé, plus c'est discriminant.
VERTICAL_PATTERNS: dict[str, list[tuple[str, float]]] = {
    "avocat": [
        (r"\bavocat\b", 4.0),
        (r"\bjuridique\b", 2.5),
        (r"\bcontentieux\b", 2.5),
        (r"\bcontrat\b", 1.5),
        (r"\bproc[eè]s\b", 2.5),
        (r"\bplaider?\b", 3.0),
        (r"\btribunal\b", 2.0),
        (r"\bconclusions?\b", 2.0),
        (r"\bdossier client\b", 3.0),
        (r"\bsecret professionnel\b", 3.0),
        (r"\bart\.?\s*321\b", 3.0),
        (r"\bdroit\b", 1.0),
        (r"\bl[eé]gal[e]?\b", 1.5),
        (r"\blitige\b", 2.0),
        (r"\bmandat\b", 1.5),
        (r"\bconseil juridique\b", 2.5),
    ],
    "comptable": [
        (r"\bcomptab\w+", 3.0),
        (r"\bbilan\b", 2.5),
        (r"\bfiscal[e]?\b", 2.5),
        (r"\btva\b", 2.0),
        (r"\bimp[oô]t\b", 2.0),
        (r"\bd[eé]claration\b", 1.5),
        (r"\bcompte\s+r[eé]sultat\b", 2.5),
        (r"\bgrand\s+livre\b", 2.5),
        (r"\b[eé]criture\b", 2.0),
        (r"\baudit\b", 1.0),
        (r"\bbudget\b", 1.0),
        (r"\btr[eé]sorerie\b", 2.0),
        (r"\bcharge\b", 0.5),
        # 'produit' trop générique — retiré
        (r"\b amortissement\b", 2.0),
    ],
    "banque": [
        (r"\bbanque\b", 3.0),
        (r"\b bancaire\b", 3.0),
        (r"\bcompte\b", 1.0),
        (r"\bcr[eé]dit\b", 2.0),
        (r"\bd[eé]p[oô]t\b", 2.0),
        (r"\bretrait\b", 1.5),
        (r"\btransfert\b", 1.0),
        (r"\bkyc\b", 3.0),
        (r"\baml\b", 3.0),
        (r"\banti[- ]blanchiment\b", 3.0),
        (r"\bfinma\b", 3.0),
        (r"\bsecret bancaire\b", 3.0),
        (r"\bart\.?\s*47\b", 3.0),
        (r"\bmontant\b", 0.5),
        (r"\bswift\b", 2.0),
    ],
    "sante": [
        (r"\bsant[eé]\b", 2.5),
        (r"\bm[eé]dical\b", 3.0),
        (r"\bm[eé]decin\b", 3.0),
        (r"\bpatient\b", 3.0),
        (r"\bh[oô]pital\b", 3.0),
        (r"\bclinique\b", 2.0),
        (r"\bdiagnostic\b", 2.5),
        (r"\bdonn[eé]es\s+de\s+sant[eé]\b", 3.0),
        (r"\bdmp\b", 3.0),
        (r"\bhds\b", 2.0),
        (r"\blpm\b", 2.0),
        (r"\bordonnance\b", 2.5),
        (r"\bsoins?\b", 1.5),
        (r"\binfirmier\b", 2.0),
        (r"\bpharmacie\b", 2.0),
    ],
    "rh": [
        (r"\brh\b", 3.0),
        (r"\bressources?\s+humaines\b", 3.0),
        (r"\bembauche\b", 2.5),
        (r"\brecrutement\b", 2.5),
        (r"\blicenciement\b", 2.5),
        (r"\bpaie\b", 2.0),
        (r"\bsalaire\b", 2.0),
        (r"\bemploy[eé]\b", 1.5),
        (r"\bcandidat\b", 2.0),
        (r"\bentretien\b", 1.0),
        (r"\bconv\.?\s*collective\b", 2.5),
        (r"\bdiscrimination\b", 2.5),
        (r"\bnotation\b", 2.0),
        (r"\bcong[eé]s?\b", 1.5),
    ],
    "startup": [
        (r"\bstartup\b", 3.0),
        (r"\b MVP\b", 2.0),
        (r"\blanding\s+page\b", 1.5),
        (r"\bSaaS\b", 2.5),
        (r"\bfundraising\b", 2.0),
        (r"\blev[eé]e?\s+de\s+fonds\b", 2.5),
        (r"\bproduit\b", 0.5),
        (r"\bgo[\s-]to[\s-]market\b", 2.0),
        (r"\btraction\b", 1.5),
        (r"\bscale\b", 1.0),
    ],
    "agent-ia": [
        (r"\bagents?\s+ia\b", 3.0),
        (r"\bchatbot\b", 3.0),
        (r"\bIA\b", 1.5),
        (r"\b ai\b", 1.5),
        (r"\bllm\b", 2.5),
        (r"\bautomatis[eé]\b", 1.0),
        (r"\bclone\b", 2.0),
        (r"\bvoice\b", 1.0),
        (r"\btransparence\b", 1.5),
    ],
}


def detect_goal(goal_text: str, hint_vertical: str = None) -> GoalResult:
    """
    Détecter la verticale et les paramètres d'un goal en texte libre.

    Args:
        goal_text: Texte libre décrivant l'objectif
        hint_vertical: Indice de verticale (optionnel, bypass la détection)

    Returns:
        GoalResult avec vertical, confidence, keywords_matched
    """
    text_lower = goal_text.lower()

    # Si un hint est fourni et est valide, l'utiliser directement
    valid_verticals = set(VERTICAL_PATTERNS.keys())
    if hint_vertical and hint_vertical in valid_verticals:
        return GoalResult(
            vertical=hint_vertical,
            confidence=1.0,
            keywords_matched=["hint"],
            goal_text=goal_text,
        )

    # Scorer chaque verticale
    scores: dict[str, float] = {}
    matched: dict[str, list[str]] = {}

    for vertical, patterns in VERTICAL_PATTERNS.items():
        score = 0.0
        kw = []
        for pattern, weight in patterns:
            if re.search(pattern, text_lower):
                score += weight
                # Extraire le match lisible
                m = re.search(pattern, text_lower)
                kw.append(m.group(0))
        scores[vertical] = score
        matched[vertical] = kw

    # Trouver le meilleur score
    best_vertical = max(scores, key=scores.get)
    best_score = scores[best_vertical]

    # Si aucun match, default = startup (le plus permissif)
    if best_score == 0:
        return GoalResult(
            vertical="startup",
            confidence=0.1,
            keywords_matched=[],
            goal_text=goal_text,
        )

    # Calculer la confiance relative (normalisée)
    total_score = sum(scores.values())
    confidence = min(best_score / total_score, 1.0) if total_score > 0 else 0.1

    # Si le score est très faible (< 1.5), on reste prudent
    if best_score < 1.5:
        confidence = min(confidence, 0.3)

    return GoalResult(
        vertical=best_vertical,
        confidence=round(confidence, 2),
        keywords_matched=matched[best_vertical],
        goal_text=goal_text,
    )
