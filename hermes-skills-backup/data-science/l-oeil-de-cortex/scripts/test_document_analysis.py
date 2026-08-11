#!/usr/bin/env python3
"""
Test script pour L'Oeil de Cortex - Lead Data Visionary
Teste l'extraction de données et la détection d'anomalies dans un document administratif (Kbis)
"""

import json
from typing import Dict, List, Optional
from datetime import datetime


class DocumentAnalyzer:
    """
    Classe d'analyse de documents administratifs
    Utilise GLM-5V pour l'extraction et la détection d'anomalies
    """
    
    def __init__(self):
        self.document_types = {
            "kbis": {
                "name": "Kbis",
                "country": "France",
                "required_fields": [
                    "siren", "denomination", "form_juridique", "adresse",
                    "capital", "representant_legal", "date_immatriculation"
                ]
            },
            "statuts": {
                "name": "Statuts",
                "country": "Suisse",
                "required_fields": [
                    "ide", "denomination", "form_juridique", "siege",
                    "capital", "actionnaires", "date_constitution"
                ]
            },
            "identite": {
                "name": "Pièce d'identité",
                "country": "FR/CH",
                "required_fields": [
                    "nom", "prenoms", "date_naissance", "lieu_naissance",
                    "date_expiration", "numero_document", "signature"
                ]
            }
        }
        
        self.official_sources = {
            "infogreffe": "https://www.infogreffe.fr",
            "zefix": "https://www.zefix.ch",
            "rc_france": "https://data.inpi.fr",
            "rc_suisse": "https://register.zh.ch"
        }
    
    def analyze_document(self, document_path: str, document_type: str) -> Dict:
        """
        Analyse un document administratif
        
        Args:
            document_path: Chemin du document
            document_type: Type de document (kbis, statuts, identite)
        
        Returns:
            Résultat d'analyse complet
        """
        
        # Simulation de l'analyse avec GLM-5V
        # En production, ceci utiliserait l'API GLM-5V
        
        analysis_result = {
            "document_type": document_type,
            "document_path": document_path,
            "timestamp": datetime.now().isoformat(),
            "authenticity_score": 1.0,
            "extracted_data": {},
            "anomalies": [],
            "cross_validation": {},
            "proofs": []
        }
        
        # Extraction des données (simulée)
        if document_type == "kbis":
            analysis_result["extracted_data"] = self._extract_kbis()
            analysis_result["cross_validation"] = self._cross_validate_kbis()
            analysis_result["anomalies"] = self._detect_anomalies_kbis(
                analysis_result["extracted_data"],
                analysis_result["cross_validation"]
            )
        elif document_type == "statuts":
            analysis_result["extracted_data"] = self._extract_statuts()
            analysis_result["cross_validation"] = self._cross_validate_statuts()
            analysis_result["anomalies"] = self._detect_anomalies_statuts(
                analysis_result["extracted_data"],
                analysis_result["cross_validation"]
            )
        
        # Calcul du score d'authenticité
        analysis_result["authenticity_score"] = self._calculate_authenticity_score(
            analysis_result["anomalies"]
        )
        
        # Génération des preuves
        analysis_result["proofs"] = self._generate_proofs(document_path, document_type)
        
        return analysis_result
    
    def _extract_kbis(self) -> Dict:
        """Extraction des données d'un Kbis (simulé)"""
        
        return {
            "siren": "12345678900012",
            "denomination": "SARL CORTEX LEMAN",
            "form_juridique": "SARL",
            "adresse": "1 Rue de la République, 74100 Annemasse",
            "capital": "10000 EUR",
            "representant_legal": "Jean DUPONT",
            "date_immatriculation": "2024-01-15",
            "ape_naf": "6201Z",
            "activite": "Programmation informatique",
            "greffe": "Annecy"
        }
    
    def _cross_validate_kbis(self) -> Dict:
        """Cross-validation avec Infogreffe (simulé)"""
        
        return {
            "siren_valid": True,
            "siren_exists": True,
            "infogreffe_match": False,  # ⚠️ Anomalie
            "official_data": {
                "siren": "12345678900012",
                "denomination": "SARL CORTEX LEMAN",
                "adresse": "1 Rue de la République, 74100 Annemasse",
                "capital": "10000 EUR",
                "representant_legal": "Pierre MARTIN",  # ⚠️ Différent !
                "date_immatriculation": "2024-01-15",
                "last_update": "2026-02-28"
            },
            "modification_history": [
                {
                    "date": "2024-01-15",
                    "type": "creation",
                    "details": "Création de la SARL"
                },
                {
                    "date": "2026-03-15",
                    "type": "modification",
                    "details": "Changement de représentant légal : Pierre MARTIN → Jean DUPONT"
                }
            ]
        }
    
    def _detect_anomalies_kbis(self, extracted: Dict, cross_validated: Dict) -> List[Dict]:
        """Détection d'anomalies dans un Kbis"""
        
        anomalies = []
        
        # Anomalie 1 : Incohérence représentant légal
        if extracted["representant_legal"] != cross_validated["official_data"]["representant_legal"]:
            anomalies.append({
                "severity": "majeure",
                "type": "incoherence",
                "field": "representant_legal",
                "description": f"Incohérence entre le document (Jean DUPONT) et Infogreffe (Pierre MARTIN)",
                "location": "page_1_line_18",
                "recommendation": "Vérifier le justificatif de changement de représentant légal",
                "confidence": 0.95
            })
        
        # Anomalie 2 : Faute de frappe dans l'adresse
        if "RÉpublique" in extracted["adresse"]:
            anomalies.append({
                "severity": "mineure",
                "type": "typo",
                "field": "adresse",
                "description": "Faute de frappe : 'RÉpublique' au lieu de 'République'",
                "location": "page_1_line_12",
                "recommendation": "Corriger l'adresse dans les documents officiels",
                "confidence": 0.90
            })
        
        # Anomalie 3 : Modification récente
        recent_modifications = [
            m for m in cross_validated["modification_history"]
            if m["type"] == "modification"
            and datetime.fromisoformat(m["date"]) > datetime.fromisoformat("2026-03-01")
        ]
        
        if recent_modifications:
            for mod in recent_modifications:
                anomalies.append({
                    "severity": "majeure",
                    "type": "modification_recente",
                    "field": "representant_legal",
                    "description": f"Modification récente détectée le {mod['date']} : {mod['details']}",
                    "location": "page_1_line_18",
                    "recommendation": "Demander justification et preuves documentaires",
                    "confidence": 0.88
                })
        
        return anomalies
    
    def _extract_statuts(self) -> Dict:
        """Extraction des données de statuts (simulé)"""
        
        return {
            "ide": "CHE-123.456.789",
            "denomination": "CORTEX LEMAN SA",
            "form_juridique": "SA",
            "siege": "Route de Chêne 1, 1208 Genève",
            "capital": "100000 CHF",
            "actionnaires": [
                {"nom": "Jean DUPONT", "parts": "60%"},
                {"nom": "Pierre MARTIN", "parts": "40%"}
            ],
            "date_constitution": "2024-03-01",
            "but_social": "Développement de solutions d'intelligence artificielle"
        }
    
    def _cross_validate_statuts(self) -> Dict:
        """Cross-validation avec Zefix (simulé)"""
        
        return {
            "ide_valid": True,
            "ide_exists": True,
            "zefix_match": True,
            "official_data": {
                "ide": "CHE-123.456.789",
                "denomination": "CORTEX LEMAN SA",
                "siege": "Route de Chêne 1, 1208 Genève",
                "capital": "100000 CHF",
                "form_juridique": "SA",
                "actionnaires": [
                    {"nom": "Jean DUPONT", "parts": "60%"},
                    {"nom": "Pierre MARTIN", "parts": "40%"}
                ],
                "date_constitution": "2024-03-01",
                "last_update": "2026-01-15"
            }
        }
    
    def _detect_anomalies_statuts(self, extracted: Dict, cross_validated: Dict) -> List[Dict]:
        """Détection d'anomalies dans des statuts"""
        
        anomalies = []
        
        # Pas d'anomalies dans ce cas (document conforme)
        return anomalies
    
    def _calculate_authenticity_score(self, anomalies: List[Dict]) -> float:
        """
        Calcule le score d'authenticité (0-1)
        
        Args:
            anomalies: Liste des anomalies détectées
        
        Returns:
            Score d'authenticité
        """
        
        if not anomalies:
            return 1.0
        
        # Pénalités selon la gravité
        penalty_map = {
            "critique": 0.5,
            "majeure": 0.2,
            "mineure": 0.05
        }
        
        total_penalty = 0.0
        for anomaly in anomalies:
            penalty = penalty_map.get(anomaly["severity"], 0.1)
            total_penalty += penalty * anomaly["confidence"]
        
        # Calculer le score (minimum 0)
        score = max(0.0, 1.0 - total_penalty)
        
        return round(score, 2)
    
    def _generate_proofs(self, document_path: str, document_type: str) -> List[Dict]:
        """Génère les preuves documentaires"""
        
        proofs = []
        
        # Preuve 1 : Screenshot du document
        proofs.append({
            "type": "screenshot",
            "path": f"{document_path}_page1.png",
            "description": "Capture de la page 1 du document",
            "timestamp": datetime.now().isoformat()
        })
        
        # Preuve 2 : Cross-validation
        if document_type == "kbis":
            proofs.append({
                "type": "infogreffe_record",
                "path": f"/tmp/infogreffe_{document_type}_record.json",
                "description": "Données officielles Infogreffe",
                "timestamp": datetime.now().isoformat()
            })
        elif document_type == "statuts":
            proofs.append({
                "type": "zefix_record",
                "path": f"/tmp/zefix_{document_type}_record.json",
                "description": "Données officielles Zefix",
                "timestamp": datetime.now().isoformat()
            })
        
        return proofs
    
    def check_kill_switch(self, analysis_result: Dict) -> Dict:
        """
        Vérifie si le Kill Switch doit être activé
        
        Args:
            analysis_result: Résultat d'analyse
        
        Returns:
            Décision Kill Switch
        """
        
        critical_anomalies = [
            a for a in analysis_result["anomalies"]
            if a["severity"] == "critique"
        ]
        
        kill_switch = {
            "activated": len(critical_anomalies) > 0,
            "critical_anomalies_count": len(critical_anomalies),
            "critical_anomalies": critical_anomalies,
            "reason": None,
            "action": None
        }
        
        if kill_switch["activated"]:
            kill_switch["reason"] = f"{len(critical_anomalies)} anomalie(s) critique(s) détectée(s)"
            kill_switch["action"] = "Alerte immédiate au Gardien des Normes"
        
        return kill_switch
    
    def format_for_gardien_des_normes(self, analysis_result: Dict) -> Dict:
        """
        Formate les résultats pour Le Gardien des Normes
        
        Args:
            analysis_result: Résultat d'analyse
        
        Returns:
            Format standardisé pour Le Gardien des Normes
        """
        
        return {
            "source": "l-oeil-de-cortex",
            "document_type": analysis_result["document_type"],
            "document_id": f"{analysis_result['document_type']}_2026_001",
            "authenticity_score": analysis_result["authenticity_score"],
            "extracted_data": analysis_result["extracted_data"],
            "anomalies": analysis_result["anomalies"],
            "cross_validation": analysis_result["cross_validation"],
            "proofs": analysis_result["proofs"],
            "timestamp": analysis_result["timestamp"]
        }


def test_kbis_analysis():
    """Test l'analyse d'un Kbis"""
    
    print("=" * 80)
    print("TEST L'OEIL DE CORTEX - Analyse Kbis")
    print("=" * 80)
    print()
    
    # Initialiser l'analyseur
    analyzer = DocumentAnalyzer()
    
    # Analyser le document
    document_path = "/tmp/kbis_sarl_cortex_leman.pdf"
    analysis_result = analyzer.analyze_document(document_path, "kbis")
    
    # Afficher les résultats
    print(f"DOCUMENT : {analysis_result['document_type'].upper()}")
    print(f"Timestamp : {analysis_result['timestamp']}")
    print()
    
    print("=" * 80)
    print("DONNÉES EXTRAITES")
    print("=" * 80)
    for key, value in analysis_result["extracted_data"].items():
        print(f"{key}: {value}")
    print()
    
    print("=" * 80)
    print("CROSS-VALIDATION")
    print("=" * 80)
    print(f"SIREN valide : {analysis_result['cross_validation']['siren_valid']}")
    print(f"Match Infogreffe : {analysis_result['cross_validation']['infogreffe_match']}")
    print()
    
    print("Données officielles Infogreffe :")
    official_data = analysis_result["cross_validation"]["official_data"]
    print(f"  SIREN : {official_data['siren']}")
    print(f"  Dénomination : {official_data['denomination']}")
    print(f"  Représentant légal : {official_data['representant_legal']}")
    print(f"  Dernière mise à jour : {official_data['last_update']}")
    print()
    
    print("Historique des modifications :")
    for mod in analysis_result["cross_validation"]["modification_history"]:
        print(f"  - {mod['date']}: {mod['type']} - {mod['details']}")
    print()
    
    print("=" * 80)
    print("ANOMALIES DÉTECTÉES")
    print("=" * 80)
    print(f"Total : {len(analysis_result['anomalies'])}")
    for i, anomaly in enumerate(analysis_result["anomalies"], 1):
        print(f"\n{i}. {anomaly['severity'].upper()} - {anomaly['type']}")
        print(f"   Description : {anomaly['description']}")
        print(f"   Location : {anomaly['location']}")
        print(f"   Recommandation : {anomaly['recommendation']}")
        print(f"   Confidence : {anomaly['confidence']:.0%}")
    print()
    
    print("=" * 80)
    print("SCORE D'AUTHENTICITÉ")
    print("=" * 80)
    score = analysis_result["authenticity_score"]
    print(f"Score : {score}/1")
    print()
    
    if score >= 0.8:
        print("COULEUR : 🟢 VERT (Document authentifié avec certitude)")
    elif score >= 0.5:
        print("COULEUR : 🟠 ORANGE (Doute modéré)")
    else:
        print("COULEUR : 🔴 ROUGE (Probablement falsifié)")
    print()
    
    # Vérifier Kill Switch
    kill_switch = analyzer.check_kill_switch(analysis_result)
    
    print("=" * 80)
    print("KILL SWITCH")
    print("=" * 80)
    if kill_switch["activated"]:
        print("STATUS : ⚠️  KILL SWITCH ACTIVÉ")
        print(f"Raison : {kill_switch['reason']}")
        print(f"Action : {kill_switch['action']}")
    else:
        print("STATUS : ✅ KILL SWITCH NON ACTIVÉ")
        print("Aucune anomalie critique détectée")
    print()
    
    # Formater pour Le Gardien des Normes
    formatted_result = analyzer.format_for_gardien_des_normes(analysis_result)
    
    print("=" * 80)
    print("FORMAT POUR LE GARDIEN DES NORMES")
    print("=" * 80)
    print(json.dumps(formatted_result, indent=2, ensure_ascii=False))
    print()
    
    # Sauvegarder le rapport
    report = {
        "document_analysis": formatted_result,
        "kill_switch": kill_switch
    }
    
    with open("/tmp/analyse_document_kbis.json", "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("Rapport sauvegardé : /tmp/analyse_document_kbis.json")
    print()
    
    return report


if __name__ == "__main__":
    test_kbis_analysis()
