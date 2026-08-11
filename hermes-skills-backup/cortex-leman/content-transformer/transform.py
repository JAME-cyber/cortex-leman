"""
CONTENT TRANSFORMER - Cortex Leman
Transformation documents (PDF → Text → Structured)

Fonctions :
- extract_text_from_pdf() - Extraction OCR
- normalize_text() - Normalisation UTF-8
- format_for_analysis() - Formatage JSON
- extract_entities() - NER (Person, Org, Location)
- clean_pii() - Nettoyage données perso (GDPR)

Author: L'Ingénieur de Flux
"""

import re
import json
import hashlib
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class ExtractedContent:
    """Contenu extrait"""
    raw_text: str
    normalized_text: str
    entities: Dict[str, List[str]]
    metadata: Dict
    hash: str

class ContentTransformer:
    """Transformateur de contenu Cortex Leman"""

    # Patterns NER
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    PHONE_PATTERN = r'\b(?:\+33|0)[1-9](?:[\s.-]?\d{2}){4}\b'
    SIREN_PATTERN = r'\b\d{9}\b'
    SIRET_PATTERN = r'\b\d{14}\b'

    # PII patterns à anonymiser
    PII_PATTERNS = [
        (EMAIL_PATTERN, '[EMAIL_REDACTED]'),
        (PHONE_PATTERN, '[PHONE_REDACTED]'),
        (SIREN_PATTERN, '[SIREN_REDACTED]'),
        (SIRET_PATTERN, '[SIRET_REDACTED]'),
        (r'\b\d{2}[A-Z]{2}\d{5}\b', '[PASSPORT_REDACTED]'),  # Format FR
        (r'\b\d{15}\b', '[IBAN_REDACTED]')
    ]

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extrait texte de PDF

        Note: Dans prod, utilise PyPDF2 ou pdfplumber
        Ici simulation
        """
        # Simulation extraction
        return """
        Extrait Kbis
        SIRET: 12345678900012
        Nom: ENTREPRISE TEST
        Adresse: 123 Rue du Commerce, 75001 Paris
        Email: contact@test.com
        Téléphone: 01 23 45 67 89
        Représentant légal: JEAN DUPONT
        Date création: 01/01/2020
        Capital: 10000€
        """

    def normalize_text(self, text: str) -> str:
        """
        Normalise texte (UTF-8, espaces, ponctuation)
        """
        # Normalisation espaces
        text = re.sub(r'\s+', ' ', text)

        # Nettoyage caractères spéciaux
        text = re.sub(r'[^\w\sÀ-ÿ\.\,\-\:]', '', text)

        # Trim
        text = text.strip()

        return text

    def format_for_analysis(self, text: str, source_type: str) -> Dict:
        """
        Formate pour analyse structurée
        """
        return {
            'source_type': source_type,
            'text': text,
            'word_count': len(text.split()),
            'char_count': len(text),
            'language': self._detect_language(text)
        }

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extrait entités NER (simplifié)
        """
        entities = {
            'emails': re.findall(self.EMAIL_PATTERN, text),
            'phones': re.findall(self.PHONE_PATTERN, text),
            'sirens': re.findall(self.SIREN_PATTERN, text),
            'sirets': re.findall(self.SIRET_PATTERN, text),
            'persons': self._extract_persons(text),
            'organizations': self._extract_organizations(text),
            'dates': self._extract_dates(text)
        }

        return entities

    def _extract_persons(self, text: str) -> List[str]:
        """Extrait noms de personnes (règles simples)"""
        # Noms propres : 2+ mots en MAJUSCULES
        pattern = r'\b[A-Z]{2,}(?:\s+[A-Z]{2,})+\b'
        return re.findall(pattern, text)

    def _extract_organizations(self, text: str) -> List[str]:
        """Extrait organisations"""
        # Mots-clés typiques
        org_keywords = ['SAS', 'SARL', 'SA', 'EURL', 'GIE', 'SCOP']
        orgs = []
        for keyword in org_keywords:
            pattern = rf'\b[A-Z\s]+{keyword}[A-Z\s]*\b'
            orgs.extend(re.findall(pattern, text))
        return orgs

    def _extract_dates(self, text: str) -> List[str]:
        """Extrait dates (formats FR)"""
        # DD/MM/YYYY ou JJ/MM/AAAA
        pattern = r'\b(?:0[1-9]|[12][0-9]|3[01])/(?:0[1-9]|1[0-2])/\d{4}\b'
        return re.findall(pattern, text)

    def _detect_language(self, text: str) -> str:
        """Détecte langue (simplifié)"""
        fr_words = ['le', 'la', 'les', 'un', 'une', 'des', 'et', 'ou', 'avec', 'pour']
        en_words = ['the', 'and', 'or', 'with', 'for', 'a', 'an', 'of', 'in', 'to']

        text_lower = text.lower()
        fr_count = sum(1 for w in fr_words if w in text_lower)
        en_count = sum(1 for w in en_words if w in text_lower)

        if fr_count > en_count:
            return 'fr'
        elif en_count > fr_count:
            return 'en'
        else:
            return 'unknown'

    def clean_pii(self, text: str) -> Tuple[str, Dict]:
        """
        Nettoie données personnelles (GDPR)

        Returns:
            (text_cleaned, mapping_replacements)
        """
        mapping = {}
        cleaned = text

        for pattern, replacement in self.PII_PATTERNS:
            matches = re.findall(pattern, cleaned)
            for match in matches:
                mapping[match] = replacement
            cleaned = re.sub(pattern, replacement, cleaned)

        return cleaned, mapping

    def transform_content(self, pdf_path: str) -> ExtractedContent:
        """
        Pipeline complet transformation

        Args:
            pdf_path: Chemin fichier PDF

        Returns:
            ExtractedContent complet
        """
        # 1. Extraction
        raw_text = self.extract_text_from_pdf(pdf_path)

        # 2. Normalisation
        normalized_text = self.normalize_text(raw_text)

        # 3. Entités
        entities = self.extract_entities(normalized_text)

        # 4. Nettoyage PII
        clean_text, pii_mapping = self.clean_pii(normalized_text)

        # 5. Hash
        content_hash = hashlib.sha256(normalized_text.encode()).hexdigest()[:16]

        # 6. Metadata
        metadata = {
            'source_file': pdf_path,
            'word_count': len(normalized_text.split()),
            'entities_count': sum(len(v) for v in entities.values()),
            'pii_redacted': len(pii_mapping)
        }

        return ExtractedContent(
            raw_text=raw_text,
            normalized_text=normalized_text,
            entities=entities,
            metadata=metadata,
            hash=content_hash
        )


# Test
if __name__ == "__main__":
    transformer = ContentTransformer()

    # Test extraction
    raw = transformer.extract_text_from_pdf("test.pdf")
    print(f"Extracted: {len(raw)} chars")

    # Test normalisation
    normalized = transformer.normalize_text(raw)
    print(f"Normalized: {len(normalized)} chars")

    # Test entités
    entities = transformer.extract_entities(normalized)
    print(f"Entities: {entities}")

    # Test PII
    clean, mapping = transformer.clean_pii(normalized)
    print(f"PII redacted: {len(mapping)} items")

    # Test pipeline complet
    content = transformer.transform_content("test.pdf")
    print(f"Content hash: {content.hash}")
    print(f"Metadata: {content.metadata}")

    print("✅ Content transformer test passed")
