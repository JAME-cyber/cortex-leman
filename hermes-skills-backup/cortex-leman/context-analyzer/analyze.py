"""
CONTEXT ANALYZER - Cortex Leman
Analyse profil client + flux de données

Fonctions :
- analyze_client_profile() - Profil secteur/taille/risque
- detect_data_flows() - Identification flux collecte→stockage→transfert→suppression
- identify_risk_factors() - Facteurs de risque spécifiques
- classify_sensitivity() - Classification sensibilité données
- estimate_compliance_effort() - Effort mise en conformité

Author: L'Architecte Lémanique
"""

import json
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class Sector(Enum):
    """Secteurs d'activité"""
    HEALTH = "health"
    FINANCE = "finance"
    RETAIL = "retail"
    TECH = "tech"
    PUBLIC = "public"
    MANUFACTURING = "manufacturing"

class Size(Enum):
    """Taille entreprise"""
    MICRO = "micro"      # 1-9 salariés
    SMALL = "small"      # 10-49 salariés
    MEDIUM = "medium"    # 50-249 salariés
    LARGE = "large"      # 250+ salariés

class DataSensitivity(Enum):
    """Sensibilité des données"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ClientProfile:
    """Profil client"""
    name: str
    sector: Sector
    size: Size
    location: str
    has_health_data: bool
    has_financial_data: bool
    has_minors_data: bool
    estimated_volume: int

@dataclass
class DataFlow:
    """Flux de données"""
    step: str
    data_types: List[str]
    location: str
    has_consent: bool
    is_encrypted: bool

class ContextAnalyzer:
    """Analyseur de contexte Cortex Leman"""

    SECTOR_RISK_MULTIPLIER = {
        Sector.HEALTH: 1.5,
        Sector.FINANCE: 1.3,
        Sector.PUBLIC: 1.2,
        Sector.TECH: 1.1,
        Sector.RETAIL: 1.0,
        Sector.MANUFACTURING: 0.9
    }

    SIZE_COMPLIANCE_BASE = {
        Size.MICRO: 40,      # heures
        Size.SMALL: 60,
        Size.MEDIUM: 100,
        Size.LARGE: 200
    }

    def analyze_client_profile(self, client_data: Dict) -> ClientProfile:
        """Analyse profil client"""
        return ClientProfile(
            name=client_data['name'],
            sector=Sector(client_data['sector']),
            size=Size(client_data['size']),
            location=client_data['location'],
            has_health_data=client_data.get('health_data', False),
            has_financial_data=client_data.get('financial_data', False),
            has_minors_data=client_data.get('minors_data', False),
            estimated_volume=client_data.get('data_volume', 0)
        )

    def detect_data_flows(self, system_description: Dict) -> List[DataFlow]:
        """Détecte flux de données"""
        flows = []

        # Collecte
        flows.append(DataFlow(
            step="collect",
            data_types=system_description.get('collect_types', []),
            location=system_description.get('collect_location', 'EU'),
            has_consent=system_description.get('consent_mechanism', False),
            is_encrypted=system_description.get('collect_encrypted', False)
        ))

        # Stockage
        flows.append(DataFlow(
            step="store",
            data_types=system_description.get('store_types', []),
            location=system_description.get('store_location', 'EU'),
            has_consent=False,
            is_encrypted=system_description.get('store_encrypted', False)
        ))

        # Transfert
        flows.append(DataFlow(
            step="transfer",
            data_types=system_description.get('transfer_types', []),
            location=system_description.get('transfer_location', 'EU'),
            has_consent=False,
            is_encrypted=system_description.get('transfer_encrypted', True)
        ))

        # Suppression
        flows.append(DataFlow(
            step="delete",
            data_types=system_description.get('delete_types', []),
            location="local",
            has_consent=False,
            is_encrypted=False
        ))

        return flows

    def identify_risk_factors(self, profile: ClientProfile, flows: List[DataFlow]) -> List[str]:
        """Identifie facteurs de risque"""
        risks = []

        # Données sensibles
        if profile.has_health_data:
            risks.append("Données de santé (Art. 9 RGPD)")

        if profile.has_financial_data:
            risks.append("Données financières")

        if profile.has_minors_data:
            risks.append("Données mineurs (protection renforcée)")

        # Transferts hors UE
        for flow in flows:
            if flow.step == "transfer" and flow.location != "EU":
                risks.append(f"Transfert vers {flow.location} sans adequacy")

        # Chiffrement
        for flow in flows:
            if flow.step in ["store", "transfer"] and not flow.is_encrypted:
                risks.append(f"Non-chiffré {flow.step}")

        # Consentement
        for flow in flows:
            if flow.step == "collect" and not flow.has_consent:
                risks.append("Absence consentement explicite")

        return risks

    def classify_sensitivity(self, data_types: List[str]) -> DataSensitivity:
        """Classifie sensibilité des données"""
        critical_types = ['health', 'biometric', 'criminal', 'political']
        high_types = ['financial', 'location', 'identification']

        if any(d in critical_types for d in data_types):
            return DataSensitivity.CRITICAL

        if any(d in high_types for d in data_types):
            return DataSensitivity.HIGH

        if len(data_types) > 5:
            return DataSensitivity.MEDIUM

        return DataSensitivity.LOW

    def estimate_compliance_effort(self, profile: ClientProfile, risk_count: int) -> Tuple[int, str]:
        """
        Estime effort mise en conformité

        Returns:
            (heures_estimees, niveau_complexite)
        """
        base_hours = self.SIZE_COMPLIANCE_BASE[profile.size]

        # Multiplicateur secteur
        sector_multiplier = self.SECTOR_RISK_MULTIPLIER[profile.sector]

        # Multiplicateur risques
        risk_multiplier = 1.0 + (risk_count * 0.1)

        total_hours = int(base_hours * sector_multiplier * risk_multiplier)

        # Classification complexité
        if total_hours < 50:
            complexity = "FAIBLE"
        elif total_hours < 100:
            complexity = "MOYENNE"
        elif total_hours < 200:
            complexity = "ÉLEVÉE"
        else:
            complexity = "CRITIQUE"

        return total_hours, complexity


# Test
if __name__ == "__main__":
    analyzer = ContextAnalyzer()

    # Test profil
    client = {
        'name': 'PME Test',
        'sector': 'health',
        'size': 'medium',
        'location': 'FR',
        'health_data': True,
        'financial_data': False,
        'minors_data': False,
        'data_volume': 5000
    }

    profile = analyzer.analyze_client_profile(client)
    print(f"Client: {profile.name}, Sector: {profile.sector.value}")

    # Test flux
    system = {
        'collect_types': ['name', 'email', 'health'],
        'collect_location': 'EU',
        'consent_mechanism': True,
        'collect_encrypted': True,
        'store_types': ['name', 'email', 'health'],
        'store_location': 'EU',
        'store_encrypted': True,
        'transfer_types': [],
        'transfer_location': 'EU',
        'transfer_encrypted': True
    }

    flows = analyzer.detect_data_flows(system)
    print(f"Flows detected: {len(flows)}")

    # Test risques
    risks = analyzer.identify_risk_factors(profile, flows)
    print(f"Risks: {risks}")

    # Test effort
    hours, complexity = analyzer.estimate_compliance_effort(profile, len(risks))
    print(f"Effort: {hours}h ({complexity})")

    print("✅ Context analyzer test passed")
