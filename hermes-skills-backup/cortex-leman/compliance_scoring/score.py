"""
COMPLIANCE SCORING - Cortex Leman
Scoring compliance RGPD-AI (0-1)

Fonctions :
- calculate_score() - Score global 0-1
- weight_criteria() - Pondération critères
- apply_thresholds() - Application seuils
- classify_compliance() - Classification (Vert/Orange/Rouge)
- generate_score_report() - Rapport détaillé

Author: Le Gardien des Normes
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class ComplianceLevel(Enum):
    """Niveau de conformité"""
    NON_CONFORME = 0.0
    PARTIEL = 0.5
    LARGEMENT = 0.8
    PLEINEMENT = 1.0

class ColorCode(Enum):
    """Code couleur"""
    ROUGE = "ROUGE"
    ORANGE = "ORANGE"
    VERT = "VERT"

@dataclass
class CriteriaScore:
    """Score par critère"""
    name: str
    weight: float
    score: float
    weighted_score: float
    violations: List[str]

class ComplianceScorer:
    """Scoreur de compliance Cortex Leman"""

    # 5 domaines d'audit
    CRITERIA = {
        'collecte_donnees': {'weight': 0.2, 'threshold': 0.6},
        'transfert_hors_ue': {'weight': 0.25, 'threshold': 0.7},
        'consentement': {'weight': 0.2, 'threshold': 0.7},
        'stockage_securise': {'weight': 0.2, 'threshold': 0.8},
        'droit_oubli': {'weight': 0.15, 'threshold': 0.7}
    }

    def __init__(self):
        self.criteria_scores: List[CriteriaScore] = []

    def calculate_score(self, criteria_results: Dict[str, Dict]) -> Tuple[float, Dict]:
        """
        Calcule score global compliance

        Args:
            criteria_results: Résultats par critère
                {
                    'collecte_donnees': {'score': 0.8, 'violations': []},
                    'transfert_hors_ue': {'score': 0.3, 'violations': ['No CSC']},
                    ...
                }

        Returns:
            (score_global, details)
        """
        total_weighted = 0.0
        total_weight = 0.0

        for criteria_name, result in criteria_results.items():
            weight = self.CRITERIA[criteria_name]['weight']
            score = result['score']
            violations = result.get('violations', [])

            weighted_score = score * weight

            criteria_score = CriteriaScore(
                name=criteria_name,
                weight=weight,
                score=score,
                weighted_score=weighted_score,
                violations=violations
            )

            self.criteria_scores.append(criteria_score)

            total_weighted += weighted_score
            total_weight += weight

        global_score = total_weighted / total_weight if total_weight > 0 else 0.0

        details = {
            'global_score': global_score,
            'criteria_scores': [
                {
                    'name': cs.name,
                    'weight': cs.weight,
                    'score': cs.score,
                    'weighted_score': cs.weighted_score,
                    'violations': cs.violations
                }
                for cs in self.criteria_scores
            ]
        }

        return global_score, details

    def weight_criteria(self, sector: str) -> Dict[str, float]:
        """
        Ajuste pondération critères selon secteur

        Args:
            sector: Secteur (health, finance, retail, etc.)

        Returns:
            Dictionnaire poids ajustés
        """
        weights = self.CRITERIA.copy()

        # Santé : plus d'importance sur stockage sécurisé
        if sector == 'health':
            weights['stockage_securise']['weight'] = 0.3
            weights['consentement']['weight'] = 0.25

        # Finance : plus d'importance sur transferts
        elif sector == 'finance':
            weights['transfert_hors_ue']['weight'] = 0.3

        # Normalisation pour somme = 1
        total = sum(c['weight'] for c in weights.values())
        for criteria in weights.values():
            criteria['weight'] = criteria['weight'] / total

        return {k: v['weight'] for k, v in weights.items()}

    def apply_thresholds(self, score: float) -> Tuple[ComplianceLevel, ColorCode]:
        """
        Applique seuils classification

        Args:
            score: Score global (0-1)

        Returns:
            (niveau, couleur)
        """
        if score >= 0.8:
            return ComplianceLevel.PLEINEMENT, ColorCode.VERT
        elif score >= 0.5:
            return ComplianceLevel.LARGEMENT, ColorCode.ORANGE
        else:
            return ComplianceLevel.NON_CONFORME, ColorCode.ROUGE

    def classify_compliance(self, global_score: float) -> Dict:
        """
        Classification complète compliance

        Args:
            global_score: Score global

        Returns:
            Dictionnaire classification
        """
        level, color = self.apply_thresholds(global_score)

        return {
            'level': level.value,
            'color': color.value,
            'action_required': level != ComplianceLevel.PLEINEMENT,
            'attestation_eligible': level == ComplianceLevel.PLEINEMENT
        }

    def generate_score_report(self, criteria_results: Dict, sector: str) -> Dict:
        """
        Génère rapport complet scoring

        Args:
            criteria_results: Résultats par critère
            sector: Secteur client

        Returns:
            Rapport complet
        """
        # Ajustement pondération secteur
        weights = self.weight_criteria(sector)

        # Calcul score global
        global_score, details = self.calculate_score(criteria_results)

        # Classification
        classification = self.classify_compliance(global_score)

        # Recommandations
        recommendations = self._generate_recommendations(self.criteria_scores)

        # Violations critiques
        critical_violations = self._extract_critical_violations(self.criteria_scores)

        return {
            'global_score': global_score,
            'classification': classification,
            'sector_weights': weights,
            'criteria_details': details,
            'recommendations': recommendations,
            'critical_violations': critical_violations,
            'attestation_eligible': classification['attestation_eligible']
        }

    def _generate_recommendations(self, criteria_scores: List[CriteriaScore]) -> List[str]:
        """Génère recommandations"""
        recommendations = []

        for cs in criteria_scores:
            if cs.score < 0.5:
                recommendations.append(
                    f"CRITIQUE: {cs.name} - Score {cs.score:.2f} < 0.5. Actions immédiates requises."
                )
            elif cs.score < 0.8:
                recommendations.append(
                    f"AMÉLIORATION: {cs.name} - Score {cs.score:.2f}. Planifier corrections."
                )

        return recommendations

    def _extract_critical_violations(self, criteria_scores: List[CriteriaScore]) -> List[Dict]:
        """Extrait violations critiques"""
        critical = []

        for cs in criteria_scores:
            if cs.score < 0.5:
                for violation in cs.violations:
                    critical.append({
                        'criteria': cs.name,
                        'violation': violation,
                        'severity': 'CRITICAL',
                        'reference': 'RGPD' if 'RGPD' in cs.name else 'AI Act'
                    })

        return critical

    def check_kill_switch_conditions(self, criteria_results: Dict) -> Tuple[bool, str]:
        """
        Vérifie conditions activation Kill Switch

        Args:
            criteria_results: Résultats par critère

        Returns:
            (activate, reason)
        """
        for criteria_name, result in criteria_results.items():
            score = result['score']
            violations = result.get('violations', [])

            # Score critique (< 0.3)
            if score < 0.3:
                return True, f"Score {criteria_name} = {score:.2f} < 0.3"

            # Violations critiques
            for violation in violations:
                if 'critique' in violation.lower() or 'critical' in violation.lower():
                    return True, f"Violation critique détectée: {violation}"

        return False, ""


# Test
if __name__ == "__main__":
    scorer = ComplianceScorer()

    # Test scoring
    criteria_results = {
        'collecte_donnees': {'score': 0.9, 'violations': []},
        'transfert_hors_ue': {'score': 0.3, 'violations': ['Transfert US sans CSC']},
        'consentement': {'score': 0.7, 'violations': []},
        'stockage_securise': {'score': 0.8, 'violations': []},
        'droit_oubli': {'score': 0.5, 'violations': ['Délai > 30 jours']}
    }

    global_score, details = scorer.calculate_score(criteria_results)
    print(f"Global score: {global_score}")

    # Test classification
    classification = scorer.classify_compliance(global_score)
    print(f"Classification: {classification['level']} ({classification['color']})")

    # Test rapport
    report = scorer.generate_score_report(criteria_results, 'health')
    print(f"Attestation eligible: {report['attestation_eligible']}")
    print(f"Critical violations: {len(report['critical_violations'])}")

    # Test Kill Switch
    activate, reason = scorer.check_kill_switch_conditions(criteria_results)
    print(f"Kill switch: {activate} - {reason}")

    print("✅ Compliance scorer test passed")
