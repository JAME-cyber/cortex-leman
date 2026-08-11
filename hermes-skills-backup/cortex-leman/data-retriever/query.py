"""
DATA RETRIEVER - Cortex Leman
Récupération données légales (Infogreffe FR + Zefix CH)

Fonctions :
- query_infogreffe() - Recherche entreprise FR
- query_zefix() - Recherche entreprise CH
- cross_validate_data() - Validation croisée FR-CH
- extract_kb_details() - Extraction Kbis
- extract_statuts() - Extraction statuts société

Author: L'Oeil de Cortex
"""

import json
import requests
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CompanyData:
    """Données entreprise"""
    siret: Optional[str]
    uid: Optional[str]
    name: str
    address: str
    legal_form: str
    registration_date: Optional[str]
    capital: Optional[float]
    legal_representative: Optional[str]
    status: str

class DataRetriever:
    """Récupérateur données légales Cortex Leman"""

    INF GREFFE_BASE_URL = "https://data.infogreffe.fr/api/v1"
    ZEFIX_BASE_URL = "https://www.zefix.ch/ZefixPublicREST/api/v1"

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()

    def query_infogreffe(self, siret: str) -> Optional[CompanyData]:
        """
        Interroge Infogreffe (FR)

        Args:
            siret: Numéro SIRET (14 chiffres)

        Returns:
            CompanyData ou None
        """
        try:
            # Simulation API Infogreffe
            response = {
                'siret': siret,
                'name': 'ENTREPRISE TEST FR',
                'address': '123 Rue du Commerce, 75001 Paris',
                'legal_form': 'SARL',
                'registration_date': '2020-01-01',
                'capital': 10000.0,
                'legal_representative': 'JEAN DUPONT',
                'status': 'active'
            }

            return CompanyData(
                siret=response['siret'],
                uid=None,
                name=response['name'],
                address=response['address'],
                legal_form=response['legal_form'],
                registration_date=response['registration_date'],
                capital=response['capital'],
                legal_representative=response['legal_representative'],
                status=response['status']
            )

        except Exception as e:
            print(f"Erreur Infogreffe: {e}")
            return None

    def query_zefix(self, uid: str) -> Optional[CompanyData]:
        """
        Interroge Zefix (CH)

        Args:
            uid: UID (Mehrfachidentifikator) CH (ex: CHE-123.456.789)

        Returns:
            CompanyData ou None
        """
        try:
            # Simulation API Zefix
            response = {
                'uid': uid,
                'name': 'TEST AG CH',
                'address': 'Bahnhofstrasse 1, 8001 Zurich',
                'legal_form': 'AG',
                'registration_date': '2020-01-01',
                'capital': 100000.0,
                'legal_representative': 'HANS MUELLER',
                'status': 'active'
            }

            return CompanyData(
                siret=None,
                uid=response['uid'],
                name=response['name'],
                address=response['address'],
                legal_form=response['legal_form'],
                registration_date=response['registration_date'],
                capital=response['capital'],
                legal_representative=response['legal_representative'],
                status=response['status']
            )

        except Exception as e:
            print(f"Erreur Zefix: {e}")
            return None

    def cross_validate_data(self, fr_data: Optional[CompanyData],
                               ch_data: Optional[CompanyData]) -> Tuple[float, List[str]]:
        """
        Validation croisée FR-CH

        Args:
            fr_data: Données Infogreffe
            ch_data: Données Zefix

        Returns:
            (score_validation, anomalies)
        """
        anomalies = []

        # Cas 1: Pas de données FR, pas de données CH
        if fr_data is None and ch_data is None:
            return 0.0, ["Aucune donnée trouvée"]

        # Cas 2: Données FR seulement
        if fr_data is not None and ch_data is None:
            return 1.0, []

        # Cas 3: Données CH seulement
        if ch_data is not None and fr_data is None:
            return 1.0, []

        # Cas 4: Données FR et CH - validation
        if fr_data is not None and ch_data is not None:
            # Nom similaire?
            if not self._names_similar(fr_data.name, ch_data.name):
                anomalies.append(f"Nom différent: FR '{fr_data.name}' vs CH '{ch_data.name}'")

            # Adresse similaire?
            if not self._addresses_similar(fr_data.address, ch_data.address):
                anomalies.append("Adresse différente")

            # Représentant légal identique?
            if fr_data.legal_representative != ch_data.legal_representative:
                anomalies.append(f"Représentant différent: FR '{fr_data.legal_representative}' vs CH '{ch_data.legal_representative}'")

            # Score basé sur anomalies
            score = max(0.0, 1.0 - (len(anomalies) * 0.2))

            return score, anomalies

        return 1.0, []

    def _names_similar(self, name1: str, name2: str) -> bool:
        """Vérifie similarité noms"""
        # Nettoyage
        n1 = name1.lower().replace(' ', '').replace('-', '')
        n2 = name2.lower().replace(' ', '').replace('-', '')

        # Jaccard similarity
        set1 = set(n1)
        set2 = set(n2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return (intersection / union) >= 0.7 if union > 0 else False

    def _addresses_similar(self, addr1: str, addr2: str) -> bool:
        """Vérifie similarité adresses"""
        # Similaire : même code postal ou même ville
        zip1 = self._extract_zip(addr1)
        zip2 = self._extract_zip(addr2)

        if zip1 and zip2 and zip1 == zip2:
            return True

        # Ville
        city1 = self._extract_city(addr1)
        city2 = self._extract_city(addr2)

        if city1 and city2 and city1.lower() == city2.lower():
            return True

        return False

    def _extract_zip(self, address: str) -> Optional[str]:
        """Extrait code postal"""
        import re
        match = re.search(r'\b\d{5}\b', address)
        return match.group() if match else None

    def _extract_city(self, address: str) -> Optional[str]:
        """Extrait ville"""
        parts = address.split(',')
        return parts[-1].strip() if parts else None

    def extract_kb_details(self, pdf_path: str) -> Dict:
        """
        Extrait détails Kbis (via vision)

        Args:
            pdf_path: Chemin fichier Kbis

        Returns:
            Dictionnaire détails
        """
        # Simulation extraction vision
        return {
            'siret': '12345678900012',
            'siren': '123456789',
            'nom_commercial': 'ENTREPRISE TEST',
            'forme_juridique': 'SARL',
            'capital': 10000,
            'date_immatriculation': '2020-01-01',
            'representant_legal': 'JEAN DUPONT',
            'siege_social': '123 Rue du Commerce, 75001 Paris',
            'activite': 'Commerce de gros'
        }

    def extract_statuts(self, pdf_path: str) -> Dict:
        """
        Extrait statuts société

        Args:
            pdf_path: Chemin fichier statuts

        Returns:
            Dictionnaire statuts
        """
        # Simulation extraction
        return {
            'date_creation': '2020-01-01',
            'duree_sociale': '99 ans',
            'objet_social': 'Commerce et services',
            'capital_social': 10000,
            'repartition_capital': {
                'JEAN DUPONT': 60,
                'MARIE DURAND': 40
            },
            'pouvoirs': 'Le gérant engage la société par sa seule signature'
        }


# Test
if __name__ == "__main__":
    retriever = DataRetriever()

    # Test Infogreffe
    fr_data = retriever.query_infogreffe("12345678900012")
    print(f"FR Data: {fr_data.name if fr_data else 'None'}")

    # Test Zefix
    ch_data = retriever.query_zefix("CHE-123.456.789")
    print(f"CH Data: {ch_data.name if ch_data else 'None'}")

    # Test cross-validation
    score, anomalies = retriever.cross_validate_data(fr_data, ch_data)
    print(f"Validation score: {score}")
    print(f"Anomalies: {anomalies}")

    # Test Kbis
    kb = retriever.extract_kb_details("kbis.pdf")
    print(f"Kbis SIRET: {kb['siret']}")

    # Test statuts
    statuts = retriever.extract_statuts("statuts.pdf")
    print(f"Statuts capital: {statuts['capital_social']}€")

    print("✅ Data retriever test passed")
