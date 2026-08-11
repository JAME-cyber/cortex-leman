#!/usr/bin/env python3
"""
Test script pour Le Gardien des Normes - Compliance Officer FR-CH
Teste la validation RGPD/AI Act sur un cas fictif de mairie avec chatbot
"""

import json
from typing import Dict, List

class ComplianceValidator:
    """
    Classe de validation RGPD/AI Act
    Simule la logique GLM-5 déterministe
    """
    
    def __init__(self):
        self.rgpd_articles = {
            "Art. 5": "Principes relatifs au traitement des données",
            "Art. 6": "Licéité du traitement",
            "Art. 7": "Conditions du consentement",
            "Art. 13": "Information à fournir lorsque des données sont collectées auprès de la personne concernée",
            "Art. 17": "Droit à l'effacement («droit à l'oubli»)",
            "Art. 19": "Obligation de notifier en cas de rectification ou d'effacement",
            "Art. 25": "Protection des données dès la conception",
            "Art. 32": "Sécurité du traitement",
            "Art. 35": "Analyse d'impact relative à la protection des données",
            "Art. 37": "Désignation d'un délégué à la protection des données",
            "Art. 44": "Principe du transfert vers un pays tiers",
            "Art. 46": "Transferts fondés sur des garanties appropriées",
            "Art. 49": "Dérogations pour des situations particulières"
        }
        
        self.ai_act_articles = {
            "Art. 10": "Obligations pour les systèmes d'IA à risque élevé",
            "Art. 12": "Transparence et obligation de fournir des informations",
            "Art. 20": "Droit à une explication pour les systèmes à risque élevé",
            "Art. 27": "Obligations pour les systèmes d'IA à risque élevé",
            "Art. 28": "Obligations pour les systèmes d'IA à risque limité",
            "Art. 52": "Transparence et obligation de fournir des informations pour les systèmes à risque limité"
        }
    
    def validate_criterion(self, criterion: str, evidence: Dict) -> Dict:
        """
        Valide un critère de conformité RGPD/AI Act
        
        Args:
            criterion: Nom du critère (ex: "Collecte de données personnelles")
            evidence: Preuves collectées
        
        Returns:
            Résultat de validation avec score (0-1)
        """
        
        validation_result = {
            "criterion": criterion,
            "score": 1.0,  # Par défaut conforme
            "violations": [],
            "rgpd_references": [],
            "ai_act_references": [],
            "recommendations": []
        }
        
        # Validation selon le critère
        if criterion == "Collecte de données personnelles":
            validation_result = self._validate_data_collection(evidence)
        elif criterion == "Transfert vers serveurs hors UE":
            validation_result = self._validate_transfers(evidence)
        elif criterion == "Absence de consentement explicite":
            validation_result = self._validate_consent(evidence)
        elif criterion == "Stockage non sécurisé":
            validation_result = self._validate_storage_security(evidence)
        elif criterion == "Droit à l'oubli non implémenté":
            validation_result = self._validate_right_to_deletion(evidence)
        
        return validation_result
    
    def _validate_data_collection(self, evidence: Dict) -> Dict:
        """Validation de la collecte de données personnelles (Art. 5, 6, 13 RGPD)"""
        
        result = {
            "criterion": "Collecte de données personnelles",
            "score": 1.0,
            "violations": [],
            "rgpd_references": [],
            "ai_act_references": [],
            "recommendations": []
        }
        
        # Vérifier si une base légale est mentionnée
        if "base_legale" not in evidence or not evidence["base_legale"]:
            result["score"] = 0.0
            result["violations"].append({
                "description": "Absence de base légale identifiée pour la collecte de données",
                "severity": "critique",
                "rgpd_article": "Art. 6",
                "ai_act_article": "Art. 10"
            })
            result["rgpd_references"].append("Art. 6 - Licéité du traitement")
            result["ai_act_references"].append("Art. 10 - Obligations pour systèmes à risque élevé")
            result["recommendations"].append(
                "Identifier et documenter la base légale (consentement, contrat, intérêt légitime ou obligation légale)"
            )
        
        # Vérifier si les utilisateurs sont informés
        if "information_users" not in evidence or not evidence["information_users"]:
            result["score"] = 0.0
            result["violations"].append({
                "description": "Absence d'information claire des utilisateurs sur la collecte de données",
                "severity": "critique",
                "rgpd_article": "Art. 13",
                "ai_act_article": "Art. 52"
            })
            result["rgpd_references"].append("Art. 13 - Information à fournir lors de la collecte")
            result["ai_act_references"].append("Art. 52 - Transparence pour systèmes à risque limité")
            result["recommendations"].append(
                "Ajouter une mention claire : \"Les données sont collectées avec votre consentement (Art. 6 RGPD)\""
            )
        
        # Vérifier la minimisation des données
        if "data_minimization" not in evidence or not evidence["data_minimization"]:
            result["score"] = max(0.0, result["score"] - 0.3)
            result["violations"].append({
                "description": "Absence de principe de minimisation des données",
                "severity": "majeure",
                "rgpd_article": "Art. 5",
                "ai_act_article": None
            })
            result["rgpd_references"].append("Art. 5 - Principes relatifs au traitement")
            result["recommendations"].append(
                "Vérifier que seules les données nécessaires sont collectées"
            )
        
        return result
    
    def _validate_transfers(self, evidence: Dict) -> Dict:
        """Validation des transferts vers serveurs hors UE (Art. 44, 46, 49 RGPD)"""
        
        result = {
            "criterion": "Transfert vers serveurs hors UE",
            "score": 1.0,
            "violations": [],
            "rgpd_references": [],
            "ai_act_references": [],
            "recommendations": []
        }
        
        # Vérifier s'il y a des transferts hors UE
        if "transfers_outside_eu" in evidence and evidence["transfers_outside_eu"]:
            
            # Vérifier si des clauses contractuelles existent
            if "contractual_clauses" not in evidence or not evidence["contractual_clauses"]:
                result["score"] = 0.0
                result["violations"].append({
                    "description": "Transfert de données hors UE sans clauses contractuelles",
                    "severity": "critique",
                    "rgpd_article": "Art. 46",
                    "ai_act_article": "Art. 27"
                })
                result["rgpd_references"].append("Art. 46 - Transferts fondés sur des garanties appropriées")
                result["ai_act_references"].append("Art. 27 - Obligations pour systèmes à risque élevé")
                result["recommendations"].append(
                    "Mettre en place des clauses contractuelles standard (CSC) pour les transferts hors UE"
                )
            
            # Vérifier s'il y a une décision d'adéquation
            if "adequacy_decision" not in evidence or not evidence["adequacy_decision"]:
                result["score"] = 0.0
                result["violations"].append({
                    "description": "Absence de décision d'adéquation pour le pays de destination",
                    "severity": "critique",
                    "rgpd_article": "Art. 45",
                    "ai_act_article": None
                })
                result["rgpd_references"].append("Art. 45 - Transferts fondés sur une décision d'adéquation")
                result["recommendations"].append(
                    "Vérifier si une décision d'adéquation existe pour le pays de destination"
                )
        
        return result
    
    def _validate_consent(self, evidence: Dict) -> Dict:
        """Validation du consentement (Art. 7 RGPD)"""
        
        result = {
            "criterion": "Absence de consentement explicite",
            "score": 1.0,
            "violations": [],
            "rgpd_references": [],
            "ai_act_references": [],
            "recommendations": []
        }
        
        # Vérifier si le consentement est requis
        if "consent_required" in evidence and evidence["consent_required"]:
            
            # Vérifier si un mécanisme de consentement existe
            if "consent_mechanism" not in evidence or not evidence["consent_mechanism"]:
                result["score"] = 0.0
                result["violations"].append({
                    "description": "Absence de mécanisme de consentement",
                    "severity": "critique",
                    "rgpd_article": "Art. 7",
                    "ai_act_article": "Art. 52"
                })
                result["rgpd_references"].append("Art. 7 - Conditions du consentement")
                result["ai_act_references"].append("Art. 52 - Transparence pour systèmes à risque limité")
                result["recommendations"].append(
                    "Implémenter un mécanisme de consentement explicite (checkbox non pré-cochée)"
                )
            
            # Vérifier la possibilité de retirer le consentement
            if "consent_withdrawal" not in evidence or not evidence["consent_withdrawal"]:
                result["score"] = 0.0
                result["violations"].append({
                    "description": "Absence de mécanisme pour retirer le consentement",
                    "severity": "critique",
                    "rgpd_article": "Art. 7(3)",
                    "ai_act_article": None
                })
                result["rgpd_references"].append("Art. 7(3) - Droit de retirer le consentement")
                result["recommendations"].append(
                    "Ajouter une option de retrait du consentement facilement accessible"
                )
            
            # Vérifier l'absence de dark patterns
            if "dark_patterns" in evidence and evidence["dark_patterns"]:
                result["score"] = max(0.0, result["score"] - 0.4)
                result["violations"].append({
                    "description": "Présence de dark patterns dans le consentement",
                    "severity": "majeure",
                    "rgpd_article": "Art. 7(4)",
                    "ai_act_article": None
                })
                result["rgpd_references"].append("Art. 7(4) - Consentement non soumis à manipulation")
                result["recommendations"].append(
                    "Éliminer les dark patterns (coercition, confusion, etc.)"
                )
        
        return result
    
    def _validate_storage_security(self, evidence: Dict) -> Dict:
        """Validation de la sécurité du stockage (Art. 25, 32 RGPD)"""
        
        result = {
            "criterion": "Stockage non sécurisé",
            "score": 1.0,
            "violations": [],
            "rgpd_references": [],
            "ai_act_references": [],
            "recommendations": []
        }
        
        # Vérifier le chiffrement at rest
        if "encryption_at_rest" not in evidence or not evidence["encryption_at_rest"]:
            result["score"] = 0.0
            result["violations"].append({
                "description": "Absence de chiffrement at rest des données",
                "severity": "critique",
                "rgpd_article": "Art. 32",
                "ai_act_article": "Art. 9"
            })
            result["rgpd_references"].append("Art. 32 - Sécurité du traitement")
            result["ai_act_references"].append("Art. 9 - Sécurité des systèmes à risque élevé")
            result["recommendations"].append(
                "Implémenter le chiffrement AES-256 pour les données stockées"
            )
        
        # Vérifier le chiffrement in transit
        if "encryption_in_transit" not in evidence or not evidence["encryption_in_transit"]:
            result["score"] = 0.0
            result["violations"].append({
                "description": "Absence de chiffrement in transit (HTTPS)",
                "severity": "critique",
                "rgpd_article": "Art. 32",
                "ai_act_article": None
            })
            result["rgpd_references"].append("Art. 32 - Sécurité du traitement")
            result["recommendations"].append(
                "Forcer l'utilisation de HTTPS avec TLS 1.3 minimum"
            )
        
        # Vérifier la gestion des accès
        if "access_control" not in evidence or not evidence["access_control"]:
            result["score"] = max(0.0, result["score"] - 0.3)
            result["violations"].append({
                "description": "Absence de contrôle d'accès (RBAC)",
                "severity": "majeure",
                "rgpd_article": "Art. 32",
                "ai_act_article": None
            })
            result["rgpd_references"].append("Art. 32 - Sécurité du traitement")
            result["recommendations"].append(
                "Implémenter un système de contrôle d'accès basé sur les rôles (RBAC)"
            )
        
        # Vérifier les sauvegardes
        if "backups" not in evidence or not evidence["backups"]:
            result["score"] = max(0.0, result["score"] - 0.4)
            result["violations"].append({
                "description": "Absence de sauvegardes sécurisées",
                "severity": "majeure",
                "rgpd_article": "Art. 32",
                "ai_act_article": None
            })
            result["rgpd_references"].append("Art. 32 - Sécurité du traitement")
            result["recommendations"].append(
                "Mettre en place des sauvegardes régulières et sécurisées"
            )
        
        return result
    
    def _validate_right_to_deletion(self, evidence: Dict) -> Dict:
        """Validation du droit à l'oubli (Art. 17, 19 RGPD)"""
        
        result = {
            "criterion": "Droit à l'oubli non implémenté",
            "score": 1.0,
            "violations": [],
            "rgpd_references": [],
            "ai_act_references": [],
            "recommendations": []
        }
        
        # Vérifier l'existence d'un mécanisme de suppression
        if "deletion_mechanism" not in evidence or not evidence["deletion_mechanism"]:
            result["score"] = 0.0
            result["violations"].append({
                "description": "Absence de mécanisme pour supprimer les données personnelles",
                "severity": "critique",
                "rgpd_article": "Art. 17",
                "ai_act_article": "Art. 20"
            })
            result["rgpd_references"].append("Art. 17 - Droit à l'effacement")
            result["ai_act_references"].append("Art. 20 - Droit à une explication")
            result["recommendations"].append(
                "Implémenter un bouton/option accessible pour supprimer les données personnelles"
            )
        
        # Vérifier les délais de traitement
        if "deletion_timeframe" not in evidence or evidence["deletion_timeframe"] > 30:
            result["score"] = max(0.0, result["score"] - 0.3)
            result["violations"].append({
                "description": f"Délai de traitement de suppression trop long ({evidence.get('deletion_timeframe', 'N/A')} jours au lieu de 30 maximum)",
                "severity": "majeure",
                "rgpd_article": "Art. 12(3)",
                "ai_act_article": None
            })
            result["rgpd_references"].append("Art. 12(3) - Délai de réponse à la personne concernée")
            result["recommendations"].append(
                "Réduire le délai de traitement des demandes de suppression à 30 jours maximum"
            )
        
        # Vérifier la notification aux sous-traitants
        if "subcontractor_notification" not in evidence or not evidence["subcontractor_notification"]:
            result["score"] = max(0.0, result["score"] - 0.4)
            result["violations"].append({
                "description": "Absence de notification aux sous-traitants en cas de suppression",
                "severity": "majeure",
                "rgpd_article": "Art. 19",
                "ai_act_article": None
            })
            result["rgpd_references"].append("Art. 19 - Obligation de notifier en cas de rectification ou d'effacement")
            result["recommendations"].append(
                "Implémenter un mécanisme pour notifier tous les sous-traitants en cas de suppression"
            )
        
        return result
    
    def check_kill_switch(self, validation_results: List[Dict]) -> Dict:
        """
        Vérifie si le Kill Switch doit être activé
        
        Args:
            validation_results: Résultats de validation pour tous les critères
        
        Returns:
            Décision Kill Switch
        """
        
        critical_violations = []
        
        for result in validation_results:
            for violation in result["violations"]:
                if violation["severity"] == "critique":
                    critical_violations.append({
                        "criterion": result["criterion"],
                        "violation": violation
                    })
        
        kill_switch = {
            "activated": len(critical_violations) > 0,
            "critical_violations_count": len(critical_violations),
            "critical_violations": critical_violations,
            "reason": None,
            "action": None
        }
        
        if kill_switch["activated"]:
            kill_switch["reason"] = f"{len(critical_violations)} violation(s) critique(s) détectée(s)"
            kill_switch["action"] = "Arrêt immédiat du système d'IA et génération du rapport d'incident"
        
        return kill_switch
    
    def calculate_overall_score(self, validation_results: List[Dict]) -> float:
        """
        Calcule le score global de conformité
        
        Args:
            validation_results: Résultats de validation pour tous les critères
        
        Returns:
            Score global (0-1)
        """
        
        scores = [result["score"] for result in validation_results]
        overall_score = sum(scores) / len(scores) if scores else 0.0
        
        return round(overall_score, 2)


def test_mairie_chatbot():
    """Test sur un cas fictif de mairie avec chatbot non conforme"""
    
    print("=" * 80)
    print("TEST LE GARDIEN DES NORMES - Mairie avec chatbot non conforme")
    print("=" * 80)
    print()
    
    # Cas fictif : Mairie d'Annemasse avec chatbot
    mairie_evidence = {
        # Collecte de données
        "base_legale": None,  # ❌ Pas de base légale
        "information_users": None,  # ❌ Pas d'information aux utilisateurs
        "data_minimization": False,  # ❌ Pas de minimisation
        
        # Transferts hors UE
        "transfers_outside_eu": True,  # ⚠️ Transferts vers OpenAI (US)
        "contractual_clauses": None,  # ❌ Pas de clauses contractuelles
        "adequacy_decision": None,  # ❌ Pas de décision d'adéquation
        
        # Consentement
        "consent_required": True,  # ✅ Consentement requis
        "consent_mechanism": None,  # ❌ Pas de mécanisme de consentement
        "consent_withdrawal": None,  # ❌ Pas de possibilité de retirer
        "dark_patterns": True,  # ❌ Dark patterns présents
        
        # Stockage
        "encryption_at_rest": False,  # ❌ Pas de chiffrement at rest
        "encryption_in_transit": True,  # ✅ HTTPS activé
        "access_control": False,  # ❌ Pas de contrôle d'accès
        "backups": True,  # ✅ Sauvegardes en place
        
        # Droit à l'oubli
        "deletion_mechanism": None,  # ❌ Pas de mécanisme de suppression
        "deletion_timeframe": 60,  # ❌ 60 jours (trop long)
        "subcontractor_notification": False  # ❌ Pas de notification aux sous-traitants
    }
    
    # Initialiser le validateur
    validator = ComplianceValidator()
    
    # Valider tous les critères
    criteria = [
        "Collecte de données personnelles",
        "Transfert vers serveurs hors UE",
        "Absence de consentement explicite",
        "Stockage non sécurisé",
        "Droit à l'oubli non implémenté"
    ]
    
    validation_results = []
    
    for criterion in criteria:
        print(f"Validation : {criterion}")
        result = validator.validate_criterion(criterion, mairie_evidence)
        validation_results.append(result)
        
        print(f"  Score : {result['score']}")
        print(f"  Violations : {len(result['violations'])}")
        for violation in result["violations"]:
            print(f"    - {violation['severity'].upper()}: {violation['description']}")
            print(f"      RGPD: {violation['rgpd_article']}")
            if violation['ai_act_article']:
                print(f"      AI Act: {violation['ai_act_article']}")
        print()
    
    # Calculer le score global
    overall_score = validator.calculate_overall_score(validation_results)
    
    print("=" * 80)
    print("SCORE GLOBAL DE CONFORMITÉ")
    print("=" * 80)
    print(f"Score : {overall_score}/1")
    print()
    
    # Code couleur
    if overall_score >= 0.8:
        print("COULEUR : 🟢 VERT (Largement conforme)")
    elif overall_score >= 0.5:
        print("COULEUR : 🟠 ORANGE (Conformité intermédiaire)")
    else:
        print("COULEUR : 🔴 ROUGE (Non conforme)")
    print()
    
    # Vérifier Kill Switch
    kill_switch = validator.check_kill_switch(validation_results)
    
    print("=" * 80)
    print("KILL SWITCH")
    print("=" * 80)
    if kill_switch["activated"]:
        print("STATUS : ⚠️  KILL SWITCH ACTIVÉ")
        print(f"Raison : {kill_switch['reason']}")
        print(f"Violations critiques détectées : {kill_switch['critical_violations_count']}")
        print()
        print("Action requise :")
        print(f"  - {kill_switch['action']}")
        print()
        print("Plan d'action corrective :")
        print("  1. Arrêter immédiatement le système d'IA")
        print("  2. Générer le rapport d'incident CNIL")
        print("  3. Mettre en conformité les violations critiques")
        print("  4. Re-audit avant redémarrage")
    else:
        print("STATUS : ✅ KILL SWITCH NON ACTIVÉ")
        print("Aucune violation critique détectée")
    print()
    
    # Générer le résumé
    print("=" * 80)
    print("RÉSUMÉ DES VIOLATIONS")
    print("=" * 80)
    total_violations = sum(len(r["violations"]) for r in validation_results)
    critical_violations = sum(1 for r in validation_results 
                              for v in r["violations"] if v["severity"] == "critique")
    major_violations = sum(1 for r in validation_results 
                          for v in r["violations"] if v["severity"] == "majeure")
    minor_violations = sum(1 for r in validation_results 
                          for v in r["violations"] if v["severity"] == "mineure")
    
    print(f"Total des violations : {total_violations}")
    print(f"  - Critiques : {critical_violations} ⚠️")
    print(f"  - Majeures : {major_violations}")
    print(f"  - Mineures : {minor_violations}")
    print()
    
    # Recommandations
    print("=" * 80)
    print("RECOMMANDATIONS PRIORITAIRES")
    print("=" * 80)
    all_recommendations = []
    for result in validation_results:
        for rec in result["recommendations"]:
            all_recommendations.append(rec)
    
    for i, rec in enumerate(all_recommendations, 1):
        print(f"{i}. {rec}")
    print()
    
    # Sauvegarder le rapport
    report = {
        "client": "Mairie d'Annemasse",
        "date": "2026-04-03",
        "overall_score": overall_score,
        "validation_results": validation_results,
        "kill_switch": kill_switch,
        "recommendations": all_recommendations
    }
    
    with open("/tmp/rapport_audit_mairie.json", "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("Rapport sauvegardé : /tmp/rapport_audit_mairie.json")
    print()
    
    return report


if __name__ == "__main__":
    test_mairie_chatbot()
