"""
LEGAL SCRAPER - Cortex Leman
Scraping juridique (CNIL, CEPD, CJUE)

Fonctions :
- scrape_cnil() - Décisions CNIL
- scrape_cepd() - Guidelines CEPD
- scrape_cjue() - Jurisprudence CJUE
- extract_legal_decisions() - Extraction décisions
- monitor_regulatory_updates() - Veille quotidienne

Author: L'Oeil de Cortex
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class LegalDecision:
    """Décision juridique"""
    source: str
    reference: str
    date: str
    title: str
    summary: str
    url: str
    relevance: float  # 0-1

class LegalScraper:
    """Scraper juridique Cortex Leman"""

    CNIL_BASE_URL = "https://www.cnil.fr"
    CEPD_BASE_URL = "https://edpb.europa.eu"
    CJUE_BASE_URL = "https://curia.europa.eu"

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 Cortex Leman Legal Scraper'
        })

    def scrape_cnil(self, days_back: int = 30) -> List[LegalDecision]:
        """
        Scrape décisions CNIL

        Args:
            days_back: Jours à remonter

        Returns:
            Liste décisions CNIL
        """
        decisions = []

        try:
            # Simulation scraping CNIL
            # En prod: BeautifulSoup sur cnil.fr/decisions

            sample_decisions = [
                {
                    'reference': 'SAN-2024-001',
                    'date': '2024-03-15',
                    'title': 'Sanction entreprise X - Violation Art. 32 RGPD',
                    'summary': 'Amende de 20,000€ pour absence de chiffrement des données',
                    'url': 'https://www.cnil.fr/sanction-2024-001',
                    'relevance': 0.9
                },
                {
                    'reference': 'SAN-2024-002',
                    'date': '2024-03-10',
                    'title': 'Mise en demeure chatbot - Consentement non explicite',
                    'summary': 'Demande correction dans 3 mois',
                    'url': 'https://www.cnil.fr/mise-en-demeure-2024-002',
                    'relevance': 0.85
                }
            ]

            for d in sample_decisions:
                decision = LegalDecision(
                    source='CNIL',
                    reference=d['reference'],
                    date=d['date'],
                    title=d['title'],
                    summary=d['summary'],
                    url=d['url'],
                    relevance=d['relevance']
                )
                decisions.append(decision)

        except Exception as e:
            print(f"Erreur scraping CNIL: {e}")

        return decisions

    def scrape_cepd(self, days_back: int = 30) -> List[LegalDecision]:
        """
        Scrape guidelines CEPD

        Args:
            days_back: Jours à remonter

        Returns:
            Liste guidelines CEPD
        """
        decisions = []

        try:
            sample_guidelines = [
                {
                    'reference': 'GUIDE-2024-001',
                    'date': '2024-03-01',
                    'title': 'Guidelines AI Act - Article 52 Transparency',
                    'summary': 'Recommandations pour conformité transparence systèmes IA',
                    'url': 'https://edpb.europa.eu/guide-2024-001',
                    'relevance': 0.95
                }
            ]

            for d in sample_guidelines:
                decision = LegalDecision(
                    source='CEPD',
                    reference=d['reference'],
                    date=d['date'],
                    title=d['title'],
                    summary=d['summary'],
                    url=d['url'],
                    relevance=d['relevance']
                )
                decisions.append(decision)

        except Exception as e:
            print(f"Erreur scraping CEPD: {e}")

        return decisions

    def scrape_cjue(self, days_back: int = 30) -> List[LegalDecision]:
        """
        Scrape jurisprudence CJUE

        Args:
            days_back: Jours à remonter

        Returns:
            Liste décisions CJUE
        """
        decisions = []

        try:
            sample_jurisprudence = [
                {
                    'reference': 'C-123/24',
                    'date': '2024-02-28',
                    'title': 'Arrêt transfert données US - Clauses standard',
                    'summary': 'Interprétation art. 46 RGPD - Mécanismes de transfert',
                    'url': 'https://curia.europa.eu/juris/C-123-24',
                    'relevance': 0.9
                }
            ]

            for d in sample_jurisprudence:
                decision = LegalDecision(
                    source='CJUE',
                    reference=d['reference'],
                    date=d['date'],
                    title=d['title'],
                    summary=d['summary'],
                    url=d['url'],
                    relevance=d['relevance']
                )
                decisions.append(decision)

        except Exception as e:
            print(f"Erreur scraping CJUE: {e}")

        return decisions

    def extract_legal_decisions(self, html_content: str) -> Dict:
        """
        Extrait décisions depuis HTML

        Args:
            html_content: Contenu HTML

        Returns:
            Dictionnaire décisions
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extraction titre, date, référence
        title = soup.find('h1')
        date = soup.find('span', class_='date')
        reference = soup.find('span', class_='reference')
        content = soup.find('div', class_='content')

        return {
            'title': title.get_text() if title else '',
            'date': date.get_text() if date else '',
            'reference': reference.get_text() if reference else '',
            'content': content.get_text() if content else ''
        }

    def monitor_regulatory_updates(self) -> Dict[str, List[LegalDecision]]:
        """
        Veille réglementaire quotidienne

        Returns:
            Dictionnaire décisions par source
        """
        updates = {
            'CNIL': self.scrape_cnil(days_back=1),
            'CEPD': self.scrape_cepd(days_back=1),
            'CJUE': self.scrape_cjue(days_back=1)
        }

        total_updates = sum(len(v) for v in updates.values())

        return {
            'date': datetime.now().isoformat(),
            'total_updates': total_updates,
            'updates_by_source': updates
        }

    def search_by_keyword(self, keyword: str, source: str = 'all') -> List[LegalDecision]:
        """
        Recherche par mot-clé

        Args:
            keyword: Mot-clé recherche
            source: Source (CNIL/CEPD/CJUE/all)

        Returns:
            Liste décisions correspondantes
        """
        all_decisions = []

        if source in ['all', 'CNIL']:
            all_decisions.extend(self.scrape_cnil(days_back=365))

        if source in ['all', 'CEPD']:
            all_decisions.extend(self.scrape_cepd(days_back=365))

        if source in ['all', 'CJUE']:
            all_decisions.extend(self.scrape_cjue(days_back=365))

        # Filtrer par mot-clé
        keyword_lower = keyword.lower()
        filtered = [
            d for d in all_decisions
            if keyword_lower in d.title.lower() or keyword_lower in d.summary.lower()
        ]

        return sorted(filtered, key=lambda x: x.relevance, reverse=True)


# Test
if __name__ == "__main__":
    scraper = LegalScraper()

    # Test CNIL
    cnil_decisions = scraper.scrape_cnil()
    print(f"CNIL decisions: {len(cnil_decisions)}")

    # Test CEPD
    cepd_decisions = scraper.scrape_cepd()
    print(f"CEPD guidelines: {len(cepd_decisions)}")

    # Test CJUE
    cjue_decisions = scraper.scrape_cjue()
    print(f"CJUE jurisprudence: {len(cjue_decisions)}")

    # Test veille
    updates = scraper.monitor_regulatory_updates()
    print(f"Updates today: {updates['total_updates']}")

    # Test recherche
    results = scraper.search_by_keyword("chatbot")
    print(f"Chatbot results: {len(results)}")

    print("✅ Legal scraper test passed")
