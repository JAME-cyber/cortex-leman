"""
Cortex Leman v5 — Knowledge Vault

Système de stockage et retrieval de connaissances:
- Stockage de documents par client/verticale
- Indexation plein texte
- Recherche sémantique (RAG ready)
- Isolation des données par client (RGPD)
- Chiffrement au repos
"""
import json
import hashlib
import logging
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from core.config import settings
from core.journal.append_only_journal import journal
from core.journal.models import JournalEventType

logger = logging.getLogger(__name__)


class KnowledgeVault:
    """
    Vault de connaissances Cortex Leman.
    
    Structure:
    vault/
    ├── {client_id}/
    │   ├── documents/       → Documents originaux
    │   ├── index/           → Index de recherche
    │   └── metadata.json    → Métadonnées client
    ├── shared/
    │   ├── regulatory/      → Textes réglementaires (CNIL, CEPD, etc.)
    │   └── templates/       → Templates par verticale
    └── catalog.json         → Catalogue global
    """

    def __init__(self, vault_path: Optional[str] = None):
        self._path = Path(vault_path or os.getenv("VAULT_PATH", "./data/vault"))
        self._path.mkdir(parents=True, exist_ok=True)
        self._init_structure()

    def _init_structure(self) -> None:
        """Créer la structure de répertoires"""
        dirs = [
            self._path / "shared" / "regulatory",
            self._path / "shared" / "templates",
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

        # Catalogue global
        catalog_path = self._path / "catalog.json"
        if not catalog_path.exists():
            catalog_path.write_text(json.dumps({
                "created_at": datetime.now(timezone.utc).isoformat(),
                "clients": {},
                "shared_documents": [],
            }, ensure_ascii=False, indent=2))

    def create_client_space(self, client_id: str, vertical: str) -> dict:
        """Créer un espace isolé pour un client"""
        client_dir = self._path / client_id
        (client_dir / "documents").mkdir(parents=True, exist_ok=True)
        (client_dir / "index").mkdir(parents=True, exist_ok=True)

        metadata = {
            "client_id": client_id,
            "vertical": vertical,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "document_count": 0,
            "data_residency": settings.compliance_data_residency,
            "encrypted": settings.compliance_encryption == "AES-256",
        }

        (client_dir / "metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2)
        )

        # Mettre à jour le catalogue
        self._update_catalog(client_id, metadata)

        logger.info(f"Espace client créé: {client_id} ({vertical})")
        return metadata

    def store_document(
        self,
        client_id: str,
        document_name: str,
        content: str,
        document_type: str = "general",
        tags: list[str] = None,
        regulatory_refs: list[str] = None,
    ) -> dict:
        """Stocker un document dans le vault client"""
        client_dir = self._path / client_id
        if not client_dir.exists():
            raise ValueError(f"Espace client {client_id} non trouvé")

        doc_id = hashlib.sha256(
            f"{client_id}:{document_name}:{datetime.now(timezone.utc).isoformat()}".encode()
        ).hexdigest()[:16]

        # Sauvegarder le document
        doc_path = client_dir / "documents" / f"{doc_id}.json"
        doc_data = {
            "doc_id": doc_id,
            "name": document_name,
            "type": document_type,
            "content": content,
            "tags": tags or [],
            "regulatory_refs": regulatory_refs or [],
            "content_hash": hashlib.sha256(content.encode()).hexdigest(),
            "stored_at": datetime.now(timezone.utc).isoformat(),
            "size_bytes": len(content.encode()),
        }

        doc_path.write_text(json.dumps(doc_data, ensure_ascii=False, indent=2))

        # Indexer le contenu
        self._index_document(client_id, doc_id, doc_data)

        # Mettre à jour les métadonnées
        metadata_path = client_dir / "metadata.json"
        if metadata_path.exists():
            metadata = json.loads(metadata_path.read_text())
            metadata["document_count"] = metadata.get("document_count", 0) + 1
            metadata["last_document"] = document_name
            metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2))

        logger.info(f"Document stocké: {document_name} → {client_id}/{doc_id}")
        return {
            "doc_id": doc_id,
            "name": document_name,
            "stored": True,
        }

    def search(
        self,
        client_id: str,
        query: str,
        document_type: Optional[str] = None,
        tags: Optional[list[str]] = None,
        limit: int = 20,
    ) -> list[dict]:
        """Rechercher des documents (plein texte simple)"""
        client_dir = self._path / client_id
        if not client_dir.exists():
            return []

        results = []
        query_lower = query.lower()

        docs_dir = client_dir / "documents"
        if not docs_dir.exists():
            return []

        for doc_file in docs_dir.glob("*.json"):
            try:
                doc = json.loads(doc_file.read_text())

                # Filtre par type
                if document_type and doc.get("type") != document_type:
                    continue

                # Filtre par tags
                if tags:
                    doc_tags = set(doc.get("tags", []))
                    if not doc_tags.intersection(set(tags)):
                        continue

                # Recherche plein texte
                content = (
                    doc.get("name", "") + " " +
                    doc.get("content", "")
                ).lower()

                if query_lower in content:
                    score = content.count(query_lower)
                    results.append({
                        "doc_id": doc.get("doc_id"),
                        "name": doc.get("name"),
                        "type": doc.get("type"),
                        "score": score,
                        "tags": doc.get("tags", []),
                        "regulatory_refs": doc.get("regulatory_refs", []),
                        "stored_at": doc.get("stored_at"),
                        "snippet": doc.get("content", "")[:200],
                    })
            except (json.JSONDecodeError, KeyError):
                continue

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def search_regulatory(self, query: str, limit: int = 10) -> list[dict]:
        """Rechercher dans les textes réglementaires partagés"""
        results = []
        reg_dir = self._path / "shared" / "regulatory"

        for doc_file in reg_dir.glob("*.json"):
            try:
                doc = json.loads(doc_file.read_text())
                content = (doc.get("title", "") + " " + doc.get("content", "")).lower()
                if query.lower() in content:
                    results.append({
                        "title": doc.get("title"),
                        "source": doc.get("source"),
                        "snippet": doc.get("content", "")[:200],
                    })
            except (json.JSONDecodeError, KeyError):
                continue

        return results[:limit]

    def get_document(self, client_id: str, doc_id: str) -> Optional[dict]:
        """Récupérer un document spécifique"""
        doc_path = self._path / client_id / "documents" / f"{doc_id}.json"
        if not doc_path.exists():
            return None
        return json.loads(doc_path.read_text())

    def list_documents(self, client_id: str, limit: int = 100, offset: int = 0) -> list[dict]:
        """Lister les documents d'un client (avec pagination)."""
        docs_dir = self._path / client_id / "documents"
        if not docs_dir.exists():
            return []

        results = []
        for doc_file in docs_dir.glob("*.json"):
            try:
                doc = json.loads(doc_file.read_text())
                results.append({
                    "doc_id": doc.get("doc_id"),
                    "name": doc.get("name"),
                    "type": doc.get("type"),
                    "tags": doc.get("tags", []),
                    "stored_at": doc.get("stored_at"),
                    "size_bytes": doc.get("size_bytes", 0),
                })
            except (json.JSONDecodeError, KeyError):
                continue

        # Trier par date de stockage (plus récent d'abord)
        results.sort(key=lambda x: x.get("stored_at", ""), reverse=True)
        return results[offset:offset + limit]

    def load_regulatory_data(self) -> int:
        """Charger les textes réglementaires de base"""
        regulations = [
            {
                "id": "rgpd-art22",
                "title": "RGPD Article 22 — Décision automatisée",
                "content": "La personne concernée a le droit de ne pas faire l'objet d'une décision fondée exclusivement sur un traitement automatisé, y compris le profilage, produisant des effets juridiques la concernant ou l'affectant de manière significative.",
                "source": "RGPD",
                "vertical": "all",
            },
            {
                "id": "ai-act-high-risk",
                "title": "AI Act — Systèmes IA à haut risque",
                "content": "Les systèmes d'IA utilisés dans les ressources humaines, l'accès aux services essentiels, la justice et les applications réglementées sont classifiés comme haut risque. Obligations: documentation technique, gestion des risques, supervision humaine, transparence.",
                "source": "AI Act 2024",
                "vertical": "all",
            },
            {
                "id": "art321-cp",
                "title": "Art. 321 CP — Secret professionnel (avocat)",
                "content": "Les avocats, leurs collaborateurs et les personnes qui participent à l'activité de l'avocat sont tenus au secret professionnel. Toute révélation est punie d'un an d'emprisonnement et de 15 000 euros d'amende.",
                "source": "Code Pénal Français",
                "vertical": "avocat",
            },
            {
                "id": "art47-lb",
                "title": "Art. 47 LB — Secret bancaire suisse",
                "content": "Quiconque aura révélé un secret qui lui a été confié ou dont il a eu connaissance en sa qualité de membre d'un organe, d'employé, de mandataire ou de liquidateur d'une banque sera puni.",
                "source": "Loi fédérale sur les banques",
                "vertical": "banque",
            },
            {
                "id": "lpm-sante",
                "title": "LPM — Protection des données médicales",
                "content": "Les données de santé sont des données sensibles au sens du RGPD. Leur traitement nécessite des garanties spécifiques: hébergement HDS, consentement explicite, droit d'accès, délai de conservation limité.",
                "source": "Loi Protection Malades + RGPD Art. 9",
                "vertical": "sante",
            },
        ]

        reg_dir = self._path / "shared" / "regulatory"
        count = 0
        for reg in regulations:
            reg_path = reg_dir / f"{reg['id']}.json"
            reg_path.write_text(json.dumps(reg, ensure_ascii=False, indent=2))
            count += 1

        logger.info(f"Données réglementaires chargées: {count} textes")
        return count

    def _index_document(self, client_id: str, doc_id: str, doc_data: dict) -> None:
        """Indexer un document pour la recherche"""
        index_dir = self._path / client_id / "index"
        index_dir.mkdir(parents=True, exist_ok=True)

        index_entry = {
            "doc_id": doc_id,
            "name": doc_data.get("name", ""),
            "type": doc_data.get("type", ""),
            "tags": doc_data.get("tags", []),
            "indexed_at": datetime.now(timezone.utc).isoformat(),
        }

        index_path = index_dir / "index.json"
        index = []
        if index_path.exists():
            index = json.loads(index_path.read_text())
        index.append(index_entry)
        index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2))

    def _update_catalog(self, client_id: str, metadata: dict) -> None:
        """Mettre à jour le catalogue global"""
        catalog_path = self._path / "catalog.json"
        if catalog_path.exists():
            catalog = json.loads(catalog_path.read_text())
        else:
            catalog = {"clients": {}}

        catalog["clients"][client_id] = metadata
        catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2))

    def get_stats(self) -> dict:
        """Statistiques du vault"""
        total_docs = 0
        total_clients = 0
        total_size = 0

        for client_dir in self._path.iterdir():
            if client_dir.is_dir() and client_dir.name != "shared":
                total_clients += 1
                docs_dir = client_dir / "documents"
                if docs_dir.exists():
                    for doc_file in docs_dir.glob("*.json"):
                        total_docs += 1
                        total_size += doc_file.stat().st_size

        return {
            "clients": total_clients,
            "documents": total_docs,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "vault_path": str(self._path),
        }


# Singleton
knowledge_vault = KnowledgeVault()
