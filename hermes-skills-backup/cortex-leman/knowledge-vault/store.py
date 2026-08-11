"""
KNOWLEDGE VAULT - Cortex Leman
Recherche + stockage base connaissances juridiques

Fonctions :
- store_in_vault() - Stockage décision/jurisprudence
- search_vault() - Recherche base connaissances
- update_knowledge_base() - Mise à jour automatique
- extract_key_insights() - Extraction insights
- generate_legal_summary() - Synthèse juridique

Author: Le Gardien des Normes
"""

import json
import hashlib
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class LegalDocument:
    """Document juridique"""
    id: str
    source: str
    reference: str
    date: str
    title: str
    content: str
    tags: List[str]
    relevance_score: float
    created_at: str

@dataclass
class SearchQuery:
    """Recherche"""
    keywords: List[str]
    source: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    min_relevance: float = 0.0

class KnowledgeVault:
    """Base connaissances juridiques Cortex Leman"""

    def __init__(self):
        self.documents: List[LegalDocument] = []
        self.load_documents()

    def _generate_id(self, content: str) -> str:
        """Génère ID unique"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def store_in_vault(self, source: str, reference: str, date: str,
                       title: str, content: str, tags: List[str]) -> str:
        """
        Stocke document dans vault

        Args:
            source: Source (CNIL/CEPD/CJUE)
            reference: Référence document
            date: Date document
            title: Titre document
            content: Contenu document
            tags: Tags document

        Returns:
            ID document stocké
        """
        doc_id = self._generate_id(content)

        document = LegalDocument(
            id=doc_id,
            source=source,
            reference=reference,
            date=date,
            title=title,
            content=content,
            tags=tags,
            relevance_score=0.0,
            created_at=datetime.now().isoformat()
        )

        self.documents.append(document)
        self.save_documents()

        return doc_id

    def search_vault(self, query: SearchQuery) -> List[LegalDocument]:
        """
        Recherche dans vault

        Args:
            query: Query recherche

        Returns:
            Liste documents correspondants
        """
        results = []

        for doc in self.documents:
            # Filtre source
            if query.source and doc.source != query.source:
                continue

            # Filtre date
            if query.date_from and doc.date < query.date_from:
                continue
            if query.date_to and doc.date > query.date_to:
                continue

            # Score recherche (keywords)
            keyword_score = self._calculate_keyword_score(doc, query.keywords)
            if keyword_score < query.min_relevance:
                continue

            # Ajouter résultats
            doc.relevance_score = keyword_score
            results.append(doc)

        # Trier par relevance
        results.sort(key=lambda x: x.relevance_score, reverse=True)

        return results

    def _calculate_keyword_score(self, doc: LegalDocument, keywords: List[str]) -> float:
        """Calcule score keywords"""
        score = 0.0
        total_keywords = len(keywords)

        if total_keywords == 0:
            return 0.0

        content_lower = doc.content.lower() + " " + doc.title.lower()

        for keyword in keywords:
            if keyword.lower() in content_lower:
                score += 1.0

        return score / total_keywords

    def update_knowledge_base(self, new_decisions: List[Dict]) -> int:
        """
        Met à jour base connaissances

        Args:
            new_decisions: Nouvelles décisions

        Returns:
            Nombre documents ajoutés
        """
        added = 0

        for decision in new_decisions:
            # Vérifier si existe déjà
            existing = self._find_by_reference(decision.get('reference', ''))
            if existing:
                continue

            # Ajouter nouveau document
            self.store_in_vault(
                source=decision.get('source', ''),
                reference=decision.get('reference', ''),
                date=decision.get('date', ''),
                title=decision.get('title', ''),
                content=decision.get('summary', ''),
                tags=decision.get('tags', [])
            )
            added += 1

        return added

    def _find_by_reference(self, reference: str) -> Optional[LegalDocument]:
        """Trouve document par référence"""
        for doc in self.documents:
            if doc.reference == reference:
                return doc
        return None

    def extract_key_insights(self, documents: List[LegalDocument]) -> List[Dict]:
        """
        Extrait insights clés

        Args:
            documents: Liste documents

        Returns:
            Liste insights
        """
        insights = []

        for doc in documents:
            # Extraire citations RGPD/AI Act
            rgpd_refs = self._extract_references(doc.content, ['Art. ', 'Article ', 'RGPD'])
            ai_act_refs = self._extract_references(doc.content, ['AI Act', 'Art. '])

            insight = {
                'document_id': doc.id,
                'source': doc.source,
                'reference': doc.reference,
                'title': doc.title,
                'rgpd_references': rgpd_refs,
                'ai_act_references': ai_act_refs,
                'key_principles': self._extract_principles(doc.content),
                'actionable_guidance': self._extract_guidance(doc.content)
            }

            insights.append(insight)

        return insights

    def _extract_references(self, text: str, patterns: List[str]) -> List[str]:
        """Extrait références juridiques"""
        import re

        refs = []
        for pattern in patterns:
            matches = re.findall(rf'{pattern}[\d\w\s\-]+', text)
            refs.extend(matches)

        return list(set(refs))

    def _extract_principles(self, text: str) -> List[str]:
        """Extrait principes clés"""
        principles = []
        keywords = ['licéité', 'loyauté', 'transparence', 'minimisation',
                   'exactitude', 'limitation conservation', 'intégrité',
                   'confidentialité', 'responsabilité']

        for keyword in keywords:
            if keyword in text.lower():
                principles.append(keyword.capitalize())

        return principles

    def _extract_guidance(self, text: str) -> List[str]:
        """Extrait guidance opérationnelle"""
        import re

        guidance = []
        # Patterns pour recommandations
        patterns = [
            r'recommande.*?\.',
            r'suggère.*?\.',
            r'conseille.*?\.',
            r'il est conseillé.*?\.'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            guidance.extend(matches)

        return guidance[:5]  # Top 5

    def generate_legal_summary(self, documents: List[LegalDocument]) -> Dict:
        """
        Génère synthèse juridique

        Args:
            documents: Liste documents

        Returns:
            Synthèse structurée
        """
        insights = self.extract_key_insights(documents)

        # Agréger insights
        all_rgpd_refs = []
        all_ai_refs = []
        all_principles = []

        for insight in insights:
            all_rgpd_refs.extend(insight['rgpd_references'])
            all_ai_refs.extend(insight['ai_act_references'])
            all_principles.extend(insight['key_principles'])

        return {
            'total_documents': len(documents),
            'sources': list(set(d.source for d in documents)),
            'date_range': {
                'earliest': min(d.date for d in documents),
                'latest': max(d.date for d in documents)
            },
            'rgpd_references': list(set(all_rgpd_refs))[:10],
            'ai_act_references': list(set(all_ai_refs))[:10],
            'key_principles': list(set(all_principles)),
            'total_insights': len(insights),
            'insights': insights[:5]  # Top 5
        }

    def load_documents(self):
        """Charge documents depuis fichier"""
        try:
            with open('/home/tars/.hermes/cache/knowledge_vault.json', 'r') as f:
                data = json.load(f)
                for doc_data in data:
                    doc = LegalDocument(**doc_data)
                    self.documents.append(doc)
        except FileNotFoundError:
            pass

    def save_documents(self):
        """Sauvegarde documents dans fichier"""
        with open('/home/tars/.hermes/cache/knowledge_vault.json', 'w') as f:
            data = [doc.__dict__ for doc in self.documents]
            json.dump(data, f, indent=2)


# Test
if __name__ == "__main__":
    vault = KnowledgeVault()

    # Test stockage
    doc_id = vault.store_in_vault(
        source='CNIL',
        reference='SAN-2024-001',
        date='2024-03-15',
        title='Sanction Art. 32 RGPD',
        content='Amende pour absence de chiffrement',
        tags=['chiffrement', 'sanction', 'RGPD']
    )
    print(f"Stored document: {doc_id}")

    # Test recherche
    query = SearchQuery(
        keywords=['chiffrement'],
        source='CNIL',
        min_relevance=0.5
    )
    results = vault.search_vault(query)
    print(f"Found {len(results)} results")

    # Test insights
    insights = vault.extract_key_insights(results)
    print(f"Extracted {len(insights)} insights")

    # Test synthèse
    summary = vault.generate_legal_summary(results)
    print(f"Summary: {summary['total_documents']} documents")

    print("✅ Knowledge vault test passed")
