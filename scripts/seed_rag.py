#!/usr/bin/env python3
"""
Cortex Leman v5 — Seed RAG ChromaDB

Vectorise les textes réglementaires du vault dans ChromaDB.
Usage: python scripts/seed_rag.py
"""
import json
import sys
import os

# Ajouter le root au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from core.integrations.rag import RAGService


def seed_rag():
    vault_dir = Path("./data/vault/regulatory")

    if not vault_dir.exists():
        print(f"❌ Vault non trouvé: {vault_dir}")
        sys.exit(1)

    rag = RAGService()
    total_chunks = 0
    total_docs = 0

    for reg_file in sorted(vault_dir.glob("*.json")):
        vertical = reg_file.stem
        data = json.loads(reg_file.read_text(encoding="utf-8"))
        docs = data.get("documents", [])

        regulations = []
        for doc in docs:
            regulations.append({
                "id": doc["doc_id"],
                "title": doc["title"],
                "content": doc["text"],
                "source": doc.get("reference", ""),
                "vertical": vertical,
            })

        if regulations:
            count = rag.index_regulatory(regulations)
            total_chunks += count
            total_docs += len(regulations)
            print(f"  ✅ {vertical}: {len(regulations)} docs → {count} chunks")

    # Stats finales
    stats = rag.get_stats()
    print()
    print(f"═══ RAG Seed Complet ═══")
    print(f"  Documents: {total_docs}")
    print(f"  Chunks vectorisés: {total_chunks}")
    print(f"  Collections: {len(stats.get('collections', []))}")

    # Test rapide
    print()
    print("═══ Test recherche ═══")
    results = rag.search("déduction TVA seuil chiffre d'affaires", vertical="comptable", n_results=3)
    if results:
        for r in results:
            print(f"  [{r.get('relevance', 0):.0%}] {r.get('title', r.get('content', '')[:60])}")
    else:
        print("  ⚠️ Aucun résultat — vérifier les embeddings")

    return total_chunks


if __name__ == "__main__":
    print("🌱 Seeding RAG ChromaDB...")
    count = seed_rag()
    if count > 0:
        print(f"\n✅ {count} chunks vectorisés avec succès")
    else:
        print("\n❌ Aucun chunk vectorisé")
        sys.exit(1)
