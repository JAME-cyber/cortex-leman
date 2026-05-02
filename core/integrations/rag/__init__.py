"""
Cortex Leman v5 — RAG Vectoriel (ChromaDB)

Retrieval-Augmented Generation pour:
- Recherche sémantique dans les documents clients
- Textes réglementaires vectorisés
- Context injection pour les agents LLM
- Isolation par client (RGPD)
"""
import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from core.config import settings

logger = logging.getLogger(__name__)


class RAGService:
    """
    Service RAG vectoriel Cortex Leman.
    
    Utilise ChromaDB avec embeddings locaux (all-MiniLM-L6-v2 par défaut).
    Mode Haute Protection: tout reste en local.
    """

    def __init__(self, persist_dir: Optional[str] = None):
        self._persist_dir = persist_dir or os.path.join(
            settings.journal_path, "..", "chroma_db"
        )
        os.makedirs(self._persist_dir, exist_ok=True)

        # Client ChromaDB persistant
        self._client = chromadb.PersistentClient(
            path=self._persist_dir,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )

        # Embedding function — ChromaDB default (all-MiniLM-L6-v2)
        self._embedding_fn = chromadb.utils.embedding_functions.DefaultEmbeddingFunction()

        # Collections (créées à la demande)
        self._collections = {}

        logger.info(f"RAG ChromaDB initialisé: {self._persist_dir}")

    def _get_collection(self, client_id: str):
        """Récupère ou crée une collection pour un client"""
        if client_id not in self._collections:
            # Nom de collection sécurisé (pas de caractères spéciaux)
            safe_name = f"cl_{hashlib.md5(client_id.encode()).hexdigest()[:12]}"
            self._collections[client_id] = self._client.get_or_create_collection(
                name=safe_name,
                embedding_function=self._embedding_fn,
                metadata={"client_id": client_id, "hnsw:space": "cosine"},
            )
        return self._collections[client_id]

    def _get_regulatory_collection(self):
        """Collection partagée des textes réglementaires"""
        if "_regulatory" not in self._collections:
            self._collections["_regulatory"] = self._client.get_or_create_collection(
                name="cl_regulatory",
                embedding_function=self._embedding_fn,
                metadata={"type": "regulatory", "hnsw:space": "cosine"},
            )
        return self._collections["_regulatory"]

    def index_document(
        self,
        client_id: str,
        doc_id: str,
        content: str,
        metadata: dict = None,
    ) -> int:
        """
        Indexer un document dans ChromaDB.
        Le contenu est découpé en chunks de ~500 caractères.
        Retourne le nombre de chunks créés.
        """
        collection = self._get_collection(client_id)

        # Chunking simple par paragraphes/phrases
        chunks = self._chunk_text(content, chunk_size=500, overlap=50)

        if not chunks:
            return 0

        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        documents = chunks
        metadatas = [
            {
                **(metadata or {}),
                "doc_id": doc_id,
                "chunk_index": i,
                "chunk_total": len(chunks),
            }
            for i in range(len(chunks))
        ]

        # Upsert (idempotent)
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

        logger.info(f"Document {doc_id} indexé: {len(chunks)} chunks pour {client_id}")
        return len(chunks)

    def index_regulatory(self, regulations: list[dict]) -> int:
        """
        Indexer les textes réglementaires dans la collection partagée.
        """
        collection = self._get_regulatory_collection()

        ids = []
        documents = []
        metadatas = []

        for reg in regulations:
            reg_id = reg.get("id", hashlib.md5(reg.get("title", "").encode()).hexdigest()[:12])
            # Découper en chunks
            chunks = self._chunk_text(reg.get("content", ""), chunk_size=800, overlap=100)
            for i, chunk in enumerate(chunks):
                ids.append(f"reg_{reg_id}_chunk_{i}")
                documents.append(chunk)
                metadatas.append({
                    "reg_id": reg_id,
                    "title": reg.get("title", ""),
                    "source": reg.get("source", ""),
                    "vertical": reg.get("vertical", "all"),
                    "chunk_index": i,
                })

        if ids:
            collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
            )

        logger.info(f"Textes réglementaires indexés: {len(ids)} chunks")
        return len(ids)

    def search(
        self,
        query: str,
        client_id: str = None,
        n_results: int = 5,
        vertical: str = None,
        include_regulatory: bool = True,
    ) -> list[dict]:
        """
        Recherche sémantique RAG.
        
        1. Cherche dans les documents du client (si client_id fourni)
        2. Cherche dans les textes réglementaires (si include_regulatory)
        3. Fusionne et trie par pertinence
        """
        all_results = []

        # Recherche dans les documents client
        if client_id:
            try:
                collection = self._get_collection(client_id)
                if collection.count() > 0:
                    results = collection.query(
                        query_texts=[query],
                        n_results=min(n_results, collection.count()),
                    )
                    for i, doc in enumerate(results["documents"][0]):
                        meta = results["metadatas"][0][i] if results["metadatas"] else {}
                        distance = results["distances"][0][i] if results["distances"] else 0
                        all_results.append({
                            "content": doc,
                            "source": "client_documents",
                            "client_id": client_id,
                            "doc_id": meta.get("doc_id"),
                            "relevance": round(1 - distance, 3),
                            "metadata": meta,
                        })
            except Exception as e:
                logger.warning(f"Recherche client {client_id} échouée: {e}")

        # Recherche dans les textes réglementaires
        if include_regulatory:
            try:
                reg_collection = self._get_regulatory_collection()
                if reg_collection.count() > 0:
                    where_filter = None
                    if vertical and vertical != "all":
                        where_filter = {
                            "$or": [
                                {"vertical": vertical},
                                {"vertical": "all"},
                            ]
                        }

                    results = reg_collection.query(
                        query_texts=[query],
                        n_results=min(n_results, reg_collection.count()),
                        where=where_filter,
                    )
                    for i, doc in enumerate(results["documents"][0]):
                        meta = results["metadatas"][0][i] if results["metadatas"] else {}
                        distance = results["distances"][0][i] if results["distances"] else 0
                        all_results.append({
                            "content": doc,
                            "source": "regulatory",
                            "title": meta.get("title"),
                            "reg_id": meta.get("reg_id"),
                            "vertical": meta.get("vertical"),
                            "relevance": round(1 - distance, 3),
                        })
            except Exception as e:
                logger.warning(f"Recherche réglementaire échouée: {e}")

        # Trier par pertinence
        all_results.sort(key=lambda x: x.get("relevance", 0), reverse=True)
        return all_results[:n_results * 2]

    def build_context_for_agent(
        self,
        query: str,
        agent_name: str,
        vertical: str,
        client_id: str = None,
        n_results: int = 5,
    ) -> str:
        """
        Construire le contexte RAG pour injection dans le prompt LLM.
        
        Retourne un texte structuré avec les passages pertinents.
        """
        results = self.search(
            query=query,
            client_id=client_id,
            n_results=n_results,
            vertical=vertical,
            include_regulatory=True,
        )

        if not results:
            return "Aucun contexte supplémentaire trouvé."

        context_parts = ["CONTEXTE RAG (documents et textes pertinents):"]

        for i, result in enumerate(results, 1):
            source = result.get("source", "unknown")
            relevance = result.get("relevance", 0)

            if source == "regulatory":
                context_parts.append(
                    f"\n--- Référence réglementaire (pertinence: {relevance:.0%}) ---"
                    f"\nTitre: {result.get('title', 'N/A')}"
                    f"\nSource: {result.get('vertical', 'N/A')}"
                    f"\n{result.get('content', '')}"
                )
            else:
                context_parts.append(
                    f"\n--- Document client (pertinence: {relevance:.0%}) ---"
                    f"\nDocument: {result.get('doc_id', 'N/A')}"
                    f"\n{result.get('content', '')}"
                )

        return "\n".join(context_parts)

    def delete_client_data(self, client_id: str) -> bool:
        """
        Supprimer toutes les données d'un client (RGPD — droit à l'oubli).
        """
        try:
            safe_name = f"cl_{hashlib.md5(client_id.encode()).hexdigest()[:12]}"
            self._client.delete_collection(safe_name)
            if client_id in self._collections:
                del self._collections[client_id]
            logger.info(f"Données RAG client {client_id} supprimées (droit à l'oubli)")
            return True
        except Exception as e:
            logger.error(f"Suppression RAG client {client_id} échouée: {e}")
            return False

    def get_stats(self) -> dict:
        """Statistiques RAG"""
        collections = self._client.list_collections()
        stats = {"collections": []}
        total_chunks = 0

        for coll in collections:
            count = coll.count()
            total_chunks += count
            stats["collections"].append({
                "name": coll.name,
                "count": count,
            })

        stats["total_chunks"] = total_chunks
        stats["persist_dir"] = self._persist_dir
        return stats

    def load_regulatory_seed(self) -> int:
        """Charger et vectoriser les textes réglementaires du vault"""
        reg_dir = Path(settings.journal_path) / ".." / "vault" / "regulatory"
        if not reg_dir.exists():
            reg_dir = Path("./data/vault/regulatory")

        regulations = []
        if reg_dir.exists():
            for f in reg_dir.glob("*.json"):
                try:
                    reg = json.loads(f.read_text())
                    regulations.append(reg)
                except (json.JSONDecodeError, KeyError):
                    continue

        if not regulations:
            logger.warning("Aucun texte réglementaire trouvé dans le vault")
            return 0

        return self.index_regulatory(regulations)

    @staticmethod
    def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
        """Découper un texte en chunks avec overlap"""
        if not text or len(text) <= chunk_size:
            return [text] if text else []

        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            # Essayer de couper à une phrase/paragraphe
            if end < len(text):
                # Chercher le dernier point/retour à la ligne
                for sep in ["\n\n", ". ", "\n", "."]:
                    last_sep = chunk.rfind(sep)
                    if last_sep > chunk_size // 2:
                        chunk = text[start:start + last_sep + len(sep)]
                        end = start + last_sep + len(sep)
                        break

            chunks.append(chunk.strip())
            start = end - overlap

        return [c for c in chunks if len(c) > 20]


# Singleton
_rag: Optional[RAGService] = None


def get_rag() -> RAGService:
    """Récupère l'instance RAG"""
    global _rag
    if _rag is None:
        _rag = RAGService()
    return _rag


def init_rag():
    """Initialise le RAG et charge les données réglementaires"""
    global _rag
    _rag = RAGService()
    count = _rag.load_regulatory_seed()
    logger.info(f"RAG initialisé: {count} chunks réglementaires")
    return _rag
