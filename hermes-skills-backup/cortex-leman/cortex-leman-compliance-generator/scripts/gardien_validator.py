#!/usr/bin/env python3
"""
Le Gardien des Normes - Validateur de Conformité
Valide les contenus générés pour assurer la conformité RGPD et juridique
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

# Configuration
logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Sévérité des problèmes de conformité"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Résultat de validation"""
    is_valid: bool
    issues: List[Dict]
    corrected_text: Optional[str] = None
    confidence: float = 0.0


@dataclass
class ComplianceRule:
    """Règle de conformité"""
    name: str
    description: str
    severity: ValidationSeverity
    check_function: callable


class GardienValidator:
    """Validateur de conformité pour Cortex Leman"""
    
    def __init__(self):
        self.rules = self._init_rules()
        self.glossary_rgpd = {
            "rgpd": "Règlement Général sur la Protection des Données",
            "gdpr": "Règlement Général sur la Protection des Données",
            "dpo": "Délégué à la Protection des Données",
            "dpd": "Délégué à la Protection des Données",
            "dpia": "Data Protection Impact Assessment",
            "eipd": "Évaluation d'Impact sur la Protection des Données",
            "traitement": "Traitement de données à caractère personnel",
            "consentement": "Consentement explicite et informé",
            "finalité": "Finalité du traitement",
            "minimisation": "Minimisation des données"
        }
    
    def _init_rules(self) -> List[ComplianceRule]:
        """Initialise les règles de conformité"""
        return [
            ComplianceRule(
                name="exactitude_terminologique",
                description="Vérifie l'exactitude des termes RGPD",
                severity=ValidationSeverity.ERROR,
                check_function=self._check_terminology
            ),
            ComplianceRule(
                name="absence_proprio_industrie",
                description="Évite le langage 'propriétaire industriel' opaque",
                severity=ValidationSeverity.WARNING,
                check_function=self._check_proprio_language
            ),
            ComplianceRule(
                name="coherence_juridique",
                description="Vérifie la cohérence juridique des affirmations",
                severity=ValidationSeverity.ERROR,
                check_function=self._check_legal_coherence
            ),
            ComplianceRule(
                name="mentions_legales_obligatoires",
                description="Vérifie les mentions légales obligatoires",
                severity=ValidationSeverity.CRITICAL,
                check_function=self._check_required_mentions
            ),
            ComplianceRule(
                name="absence_promesses_irrealistes",
                description="Évite les promesses irréalistes de conformité",
                severity=ValidationSeverity.ERROR,
                check_function=self._check_realistic_claims
            ),
            ComplianceRule(
                name="adaptation_pme",
                description="Le contenu doit être adapté aux PME FR-CH",
                severity=ValidationSeverity.INFO,
                check_function=self._check_pme_adaptation
            )
        ]
    
    def validate_post(self, text: str, platform: str) -> ValidationResult:
        """
        Valide un post de réseau social
        
        Args:
            text: Texte du post à valider
            platform: Platforme (linkedin, twitter)
        
        Returns:
            ValidationResult avec issues et corrections potentielles
        """
        issues = []
        corrected_text = text
        total_confidence = 0.0
        valid_rules = 0
        
        logger.info(f"🔍 Validation post {platform} ({len(text)} caractères)")
        
        for rule in self.rules:
            try:
                result = rule.check_function(text, platform)
                
                if result.get("has_issue", False):
                    issues.append({
                        "rule": rule.name,
                        "severity": rule.severity.value,
                        "description": rule.description,
                        "issue": result["issue"],
                        "correction": result.get("correction"),
                        "position": result.get("position")
                    })
                    
                    # Appliquer la correction si disponible
                    if result.get("correction"):
                        corrected_text = corrected_text.replace(
                            result.get("original", result["issue"]),
                            result["correction"]
                        )
                    
                    logger.warning(f"⚠️ {rule.name}: {result['issue']}")
                else:
                    valid_rules += 1
                    total_confidence += result.get("confidence", 1.0)
                    logger.info(f"✅ {rule.name}: OK")
                    
            except Exception as e:
                logger.error(f"❌ Erreur règle {rule.name}: {e}")
                issues.append({
                    "rule": rule.name,
                    "severity": ValidationSeverity.ERROR.value,
                    "description": f"Erreur lors de la validation: {e}"
                })
        
        # Calcul de la confiance globale
        confidence = total_confidence / len(self.rules) if self.rules else 0.0
        
        # Déterminer si le texte est valide
        critical_issues = [i for i in issues if i["severity"] == ValidationSeverity.CRITICAL.value]
        error_issues = [i for i in issues if i["severity"] == ValidationSeverity.ERROR.value]
        
        is_valid = len(critical_issues) == 0
        
        logger.info(f"📊 Validation terminée: {len(issues)} issues, confiance: {confidence:.2f}")
        
        return ValidationResult(
            is_valid=is_valid,
            issues=issues,
            corrected_text=corrected_text if issues else None,
            confidence=confidence
        )
    
    def _check_terminology(self, text: str, platform: str) -> Dict:
        """Vérifie l'exactitude des termes RGPD"""
        issues = []
        
        # Vérifier l'utilisation correcte des abréviations
        incorrect_abbreviations = {
            "GDPR": "RGPD",
            "PII": "Données personnelles",
            "GDPR": "RGPD"
        }
        
        text_lower = text.lower()
        
        # Vérifier que les termes RGPD sont correctement utilisés
        if "gdpr" in text_lower and "rgpd" not in text_lower:
            return {
                "has_issue": True,
                "issue": "Utilisation de 'GDPR' au lieu de 'RGPD' pour le contexte FR-CH",
                "correction": "RGPD",
                "confidence": 1.0
            }
        
        # Vérifier que les termes techniques sont corrects
        if "dpo" in text_lower and "délégué" not in text_lower:
            return {
                "has_issue": True,
                "issue": "Utilisation de l'abréviation 'DPO' sans l'expliciter",
                "correction": "DPO (Délégué à la Protection des Données)",
                "confidence": 0.8
            }
        
        return {"has_issue": False, "confidence": 1.0}
    
    def _check_proprio_language(self, text: str, platform: str) -> Dict:
        """Évite le langage 'propriétaire industriel' opaque"""
        # Termes à éviter ou à expliciter
        proprio_terms = [
            "best practice",
            "best practices",
            "framework propriétaire",
            "méthodologie exclusive",
            "solution unique"
        ]
        
        text_lower = text.lower()
        
        for term in proprio_terms:
            if term in text_lower:
                return {
                    "has_issue": True,
                    "issue": f"Utilisation de terme opaque '{term}'",
                    "correction": "recommandations standards" if "best" in term else "standards reconnus",
                    "confidence": 0.7
                }
        
        return {"has_issue": False, "confidence": 1.0}
    
    def _check_legal_coherence(self, text: str, platform: str) -> Dict:
        """Vérifie la cohérence juridique des affirmations"""
        # Affirmations potentiellement problématiques
        problematic_claims = [
            "100% conforme",
            "totalement conforme",
            "conformité garantie",
            "sans risque",
            "zéro risque"
        ]
        
        text_lower = text.lower()
        
        for claim in problematic_claims:
            if claim in text_lower:
                return {
                    "has_issue": True,
                    "issue": f"Affirmation irréaliste: '{claim}'",
                    "correction": "conforme aux exigences actuelles" if "conforme" in claim else "réduit les risques",
                    "confidence": 0.9
                }
        
        return {"has_issue": False, "confidence": 1.0}
    
    def _check_required_mentions(self, text: str, platform: str) -> Dict:
        """Vérifie les mentions légales obligatoires"""
        required_mentions = []
        
        if platform == "linkedin":
            # Pour LinkedIn, vérifier la présence de mentions pertinentes
            if "rgpd" not in text.lower():
                required_mentions.append("RGPD")
        elif platform == "twitter":
            # Pour Twitter, plus concis
            pass
        
        if required_mentions:
            return {
                "has_issue": True,
                "issue": f"Mentions manquantes: {', '.join(required_mentions)}",
                "correction": None,
                "confidence": 0.8
            }
        
        return {"has_issue": False, "confidence": 1.0}
    
    def _check_realistic_claims(self, text: str, platform: str) -> Dict:
        """Évite les promesses irréalistes de conformité"""
        # Promesses irréalistes
        unrealistic_promises = [
            "en 24h",
            "en 1 jour",
            "instantanément",
            "immédiatement",
            "sans effort"
        ]
        
        text_lower = text.lower()
        
        for promise in unrealistic_promises:
            if promise in text_lower:
                return {
                    "has_issue": True,
                    "issue": f"Promesse irréaliste: '{promise}'",
                    "correction": "rapidement" if "instantanément" in promise else "en quelques jours",
                    "confidence": 0.85
                }
        
        return {"has_issue": False, "confidence": 1.0}
    
    def _check_pme_adaptation(self, text: str, platform: str) -> Dict:
        """Vérifie que le contenu est adapté aux PME FR-CH"""
        # Indicateurs d'adaptation PME
        pme_indicators = [
            "pme",
            "petite entreprise",
            "entreprise de taille moyenne",
            "tpe",
            "très petite entreprise"
        ]
        
        text_lower = text.lower()
        
        # Si aucun indicateur PME n'est présent, ce n'est pas critique mais c'est un info
        has_pme_context = any(indicator in text_lower for indicator in pme_indicators)
        
        if not has_pme_context:
            return {
                "has_issue": True,
                "issue": "Contenu non explicitement adapté aux PME",
                "correction": None,
                "confidence": 0.6
            }
        
        return {"has_issue": False, "confidence": 1.0}
    
    def validate_all_posts(self, posts: Dict[str, str]) -> Dict[str, ValidationResult]:
        """
        Valide tous les posts
        
        Args:
            posts: Dictionnaire {platforme: texte}
        
        Returns:
            Dictionnaire {platforme: ValidationResult}
        """
        results = {}
        
        for platform, text in posts.items():
            results[platform] = self.validate_post(text, platform)
        
        return results


# Fonction utilitaire
def create_gardien_validator() -> GardienValidator:
    """
    Crée un validateur Le Gardien
    
    Returns:
        Instance de GardienValidator
    """
    return GardienValidator()


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    
    validator = create_gardien_validator()
    
    # Test post valide
    valid_post = """🔒 RGPD & IA: Ce que les PME FR-CH doivent savoir en 2026

L'UE renforce les obligations sur l'IA générative. Pour votre PME: documentation obligatoire, DPIA pour systèmes à haut risque, transparence utilisateurs.

Prêt à évaluer votre conformité ?

#RGPD #Compliance #DataProtection #AI #FranceSuisse"""
    
    print("=== TEST POST VALIDE ===")
    result = validator.validate_post(valid_post, "linkedin")
    print(f"Valid: {result.is_valid}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Issues: {len(result.issues)}")
    
    # Test post avec problèmes
    invalid_post = """🔒 GDPR & AI: 100% conforme en 24h!

Best practice exclusive. Totalement garanti zéro risque.

#GDPR #Compliance"""
    
    print("\n=== TEST POST INVALIDE ===")
    result = validator.validate_post(invalid_post, "linkedin")
    print(f"Valid: {result.is_valid}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Issues: {len(result.issues)}")
    for issue in result.issues:
        print(f"  - {issue['severity']}: {issue['issue']}")
