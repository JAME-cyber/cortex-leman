#!/usr/bin/env python3
"""
Cortex Leman v5 — Générateur de Verticale (ADK-like)

Crée une nouvelle verticale métier en 3 fichiers:
  1. core/mediator/rules/{vertical}.json   — Règles JsonLogic du Médiateur
  2. core/serment/{vertical}.yaml           — Serment numérique
  3. data/vault/regulatory/{vertical}.json  — Textes réglementaires pour le RAG

Usage:
  python scripts/add_vertical.py <nom_vertical> [--rules 5] [--profession "Nom"]

Exemple:
  python scripts/add_vertical.py assurance --profession "Agent d'Assurance"
  python scripts/add_vertical.py immobilier --rules 4
"""
import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Root du projet
ROOT = Path(__file__).parent.parent
RULES_DIR = ROOT / "core" / "mediator" / "rules"
SERMENT_DIR = ROOT / "core" / "serment"
VAULT_DIR = ROOT / "data" / "vault" / "regulatory"

VERTICALS_EXISTANTES = [f.stem for f in RULES_DIR.glob("*.json")]

# Profils pré-configurés pour les verticales courantes
PROFILS = {
    "assurance": {
        "profession": "Agent d'Assurance / Courtier",
        "jurisdiction": "FR (Code des assurances) + CH (LCA/LSA)",
        "references": [
            "Code des assurances Art. L113-1 à L113-16",
            "LCA (Loi sur le Contrat d'Assurance, CH)",
            "RGPD Art. 22 — Décision automatisée",
            "AI Act Art. 6 — Classification des risques",
            "IDD — Directive Distribution d'Assurances (EU)",
        ],
        "serment_lignes": [
            "À ne prendre AUCUNE décision de souscription ou d'indemnisation automatique.",
            "À signaler tout sinistre dont le montant dépasse le seuil de prudence.",
            "À respecter le devoir de conseil et d'information de l'assuré.",
            "À ne jamais recommander un produit sur la base de critères discriminatoires.",
            "À conserver la trace de chaque analyse dans le journal d'audit.",
        ],
        "rules": [
            {
                "id": "assurance-001",
                "name": "Pas de souscription automatique",
                "severity": "critical",
                "condition": {"and": [
                    {"==": [{"var": "action.type"}, "souscription"]},
                    {"!": [{"var": "human_validated"}]},
                ]},
                "action": "freeze",
                "message": "IDD + AI Act: Aucune souscription automatique sans validation humaine.",
            },
            {
                "id": "assurance-002",
                "name": "Indemnisation : seuil de prudence",
                "severity": "critical",
                "condition": {"and": [
                    {"==": [{"var": "action.type"}, "indemnisation"]},
                    {">=": [{"var": "payload.montant"}, 10000]},
                ]},
                "action": "freeze",
                "message": "Indemnisation >= 10 000 sans validation humaine. Gel préventif.",
            },
            {
                "id": "assurance-003",
                "name": "Anti-discrimination tarifaire",
                "severity": "high",
                "condition": {"and": [
                    {"!=": [{"var": "bias_score"}, None]},
                    {">=": [{"var": "bias_score"}, 0.5]},
                ]},
                "action": "freeze",
                "message": "Code des assurances + AI Act: Score de biais >= 0.5 dans la tarification.",
            },
            {
                "id": "assurance-004",
                "name": "Dossier sensible : consentement",
                "severity": "high",
                "condition": {"and": [
                    {"==": [{"var": "data_category"}, "donnees_sante_assurance"]},
                    {"!": [{"var": "client_consent"}]},
                ]},
                "action": "block",
                "message": "RGPD Art. 9: Données de santé utilisées en assurance sans consentement.",
            },
        ],
        "regulatory_docs": [
            {
                "title": "Code des assurances L113-1 — Obligations de l'assureur",
                "text": "L'assureur doit informer l'assuré des conditions du contrat, des exclusions et des démarches en cas de sinistre. Le devoir d'information et de conseil s'impose à chaque étape de la relation contractuelle. L'utilisation de systèmes IA pour la tarification ou la sélection des risques ne doit pas contourner ces obligations.",
                "reference": "Code des assurances Art. L113-1 à L113-16",
                "jurisdiction": "FR",
                "tags": ["assurance", "obligation", "information", "conseil", "IA"],
            },
            {
                "title": "IDD — Directive Distribution d'Assurances",
                "text": "La directive (EU) 2016/97 impose aux distributeurs d'assurances d'agir avec honnêteté, équité et professionnalisme. L'évaluation des besoins et des exigences du client est obligatoire avant toute souscription. Les outils numériques et IA utilisés dans la distribution doivent respecter ces principes et ne pas induire le client en erreur sur la nature du produit.",
                "reference": "Directive (EU) 2016/97 (IDD)",
                "jurisdiction": "EU",
                "tags": ["IDD", "distribution", "conseil", "honnêteté", "numérique"],
            },
        ],
    },
    "immobilier": {
        "profession": "Agent Immobilier / Notaire",
        "jurisdiction": "FR (Loi Hoguet) + CH (LFAI)",
        "references": [
            "Loi Hoguet Art. 1-17 (FR)",
            "LFAI — Loi Fédérale sur l'Acquisition d'Immeubles (CH)",
            "RGPD Art. 22 — Décision automatisée",
            "AI Act Art. 52 — Transparence",
        ],
        "serment_lignes": [
            "À ne prendre AUCUNE décision d'estimation automatique sans validation humaine.",
            "À signaler toute transaction dont le montant dépasse le seuil de prudence.",
            "À respecter le secret professionnel et la confidentialité des données clients.",
            "À ne jamais appliquer de discrimination dans la sélection des locataires ou acheteurs.",
            "À conserver la trace de chaque analyse dans le journal d'audit.",
        ],
        "rules": [
            {
                "id": "immobilier-001",
                "name": "Estimation automatique bloquée",
                "severity": "critical",
                "condition": {"and": [
                    {"==": [{"var": "action.type"}, "estimation"]},
                    {"!": [{"var": "human_validated"}]},
                ]},
                "action": "freeze",
                "message": "Loi Hoguet: Estimation immobilière automatique sans validation d'un agent habilité.",
            },
            {
                "id": "immobilier-002",
                "name": "Transaction : seuil de prudence",
                "severity": "critical",
                "condition": {"and": [
                    {"==": [{"var": "action.type"}, "transaction"]},
                    {">=": [{"var": "payload.montant"}, 50000]},
                ]},
                "action": "freeze",
                "message": "Transaction >= 50 000 sans validation humaine. Gel préventif.",
            },
            {
                "id": "immobilier-003",
                "name": "Anti-discrimination logement",
                "severity": "critical",
                "condition": {"and": [
                    {"!=": [{"var": "bias_score"}, None]},
                    {">=": [{"var": "bias_score"}, 0.5]},
                ]},
                "action": "freeze",
                "message": "Loi anti-discrimination + AI Act: Score de biais >= 0.5 dans la sélection locative.",
            },
        ],
        "regulatory_docs": [
            {
                "title": "Loi Hoguet — Réglementation des agents immobiliers (FR)",
                "text": "Les agents immobiliers doivent détenir une carte professionnelle et être couverts par une garantie financière. L'estimation immobilière est un acte réglementé qui nécessite des compétences spécifiques. Les outils IA utilisés pour l'estimation doivent être validés par un professionnel habilité.",
                "reference": "Loi n°70-9 Art. 1-17 (Hoguet)",
                "jurisdiction": "FR",
                "tags": ["immobilier", "agent", "estimation", "habilitation", "IA"],
            },
        ],
    },
    "education": {
        "profession": "Établissement d'Enseignement / Formateur",
        "jurisdiction": "FR (Code éducation) + CH (LEA)",
        "references": [
            "Code de l'éducation Art. L111-1 à L141-2",
            "RGPD Art. 22 — Décision automatisée",
            "AI Act Art. 52 — Transparence",
        ],
        "serment_lignes": [
            "À ne prendre AUCUNE décision d'orientation ou d'évaluation automatique sans validation humaine.",
            "À protéger les données des mineurs avec une vigilance renforcée.",
            "À signaler tout biais détecté dans les systèmes d'évaluation.",
            "À respecter le droit à l'éducation et la non-discrimination.",
            "À conserver la trace de chaque analyse dans le journal d'audit.",
        ],
        "rules": [
            {
                "id": "education-001",
                "name": "Pas de décision d'orientation automatique",
                "severity": "critical",
                "condition": {"and": [
                    {"==": [{"var": "action.type"}, "orientation"]},
                    {"!": [{"var": "human_validated"}]},
                ]},
                "action": "freeze",
                "message": "Code éducation + RGPD: Aucune orientation scolaire automatisée.",
            },
            {
                "id": "education-002",
                "name": "Données mineurs : protection renforcée",
                "severity": "critical",
                "condition": {"and": [
                    {"==": [{"var": "data_category"}, "donnees_mineur"]},
                    {"!": [{"var": "parent_consent"}]},
                ]},
                "action": "block",
                "message": "RGPD Art. 8 + Code éducation: Données de mineurs sans consentement parental.",
            },
            {
                "id": "education-003",
                "name": "Anti-discrimination évaluation",
                "severity": "high",
                "condition": {"and": [
                    {"!=": [{"var": "bias_score"}, None]},
                    {">=": [{"var": "bias_score"}, 0.3]},
                ]},
                "action": "freeze",
                "message": "AI Act + Loi anti-discrimination: Score de biais >= 0.3 dans l'évaluation académique.",
            },
        ],
        "regulatory_docs": [
            {
                "title": "Code de l'éducation — Principes fondamentaux",
                "text": "L'éducation est un droit garanti. Tout système IA utilisé dans l'éducation doit respecter le principe d'égalité d'accès et ne pas reproduire de discriminations. Les données des élèves sont protégées par le RGPD avec des garanties renforcées pour les mineurs.",
                "reference": "Code éducation Art. L111-1 à L141-2",
                "jurisdiction": "FR",
                "tags": ["éducation", "égalité", "mineur", "RGPD", "IA"],
            },
        ],
    },
}


def validate_vertical(name: str) -> str:
    """Valider le nom de la verticale"""
    name = name.strip().lower().replace(" ", "-")
    # Caractères autorisés : lettres, tirets
    if not all(c.isalpha() or c == "-" for c in name):
        print(f"❌ Nom invalide: '{name}'. Utilisez uniquement des lettres et tirets.")
        sys.exit(1)
    if name in VERTICALS_EXISTANTES:
        print(f"⚠️  La verticale '{name}' existe déjà !")
        print(f"   Fichiers existants:")
        print(f"   - {RULES_DIR / name}.json")
        print(f"   - {SERMENT_DIR / name}.yaml")
        print(f"   - {VAULT_DIR / name}.json")
        sys.exit(1)
    return name


def generate_rules(vertical: str, profil: dict) -> dict:
    """Générer les règles JsonLogic pour la verticale"""
    rules = profil.get("rules", [
        {
            "id": f"{vertical}-001",
            "name": "Validation humaine requise",
            "severity": "critical",
            "condition": {"and": [
                {"==": [{"var": "action.type"}, "decision"]},
                {"!": [{"var": "human_validated"}]},
            ]},
            "action": "freeze",
            "message": f"Règle par défaut {vertical}: Décision automatique sans validation humaine.",
        },
    ])
    return {
        "vertical": vertical,
        "description": f"Règles de conformité pour {profil.get('profession', vertical)} (RGPD, AI Act)",
        "rules": rules,
    }


def generate_serment(vertical: str, profil: dict) -> str:
    """Générer le serment numérique pour la verticale"""
    profession = profil.get("profession", vertical.capitalize())
    jurisdiction = profil.get("jurisdiction", "FR/CH")
    references = profil.get("references", [f"RGPD Art. 22 — Décision automatisée", "AI Act Art. 6"])
    lignes = profil.get("serment_lignes", [
        "À ne prendre AUCUNE décision automatique sans validation humaine.",
        "À signaler toute situation dépassant le seuil de prudence.",
        "À respecter le secret professionnel et la confidentialité.",
        "À conserver la trace de chaque analyse dans le journal d'audit.",
    ])

    ref_lines = "\n".join(f'  - "{ref}"' for ref in references)
    serment_lines = "\n".join(f"  {i+1}. {ligne}" for i, ligne in enumerate(lignes))

    return f"""# Serment Numérique — {profession}
# Gravé dans le journal WORM lors de l'activation
# Immuable. Consultable par audit. Signé.

vertical: {vertical}
profession: {profession}
jurisdiction: "{jurisdiction}"

serment: |
  Je m'engage, en tant qu'agent numérique d'assistance pour les {profession.lower()} :
  
{serment_lines}

references:
{ref_lines}
"""


def generate_vault(vertical: str, profil: dict) -> dict:
    """Générer le vault réglementaire pour la verticale"""
    docs = profil.get("regulatory_docs", [
        {
            "title": f"RGPD Art. 22 — Décision automatisée ({vertical})",
            "text": "La personne concernée a le droit de ne pas faire l'objet d'une décision fondée exclusivement sur un traitement automatisé, y compris le profilage, produisant des effets juridiques la concernant ou l'affectant de manière significative. En contexte professionnel, toute recommandation générée par un système IA doit être validée par un professionnel compétent avant toute transmission.",
            "reference": "RGPD Art. 22",
            "jurisdiction": "EU",
            "tags": ["automatisation", "décision", "IA", vertical],
        },
    ])

    documents = []
    for i, doc in enumerate(docs):
        documents.append({
            "doc_id": f"reg-{vertical[:3]}-{i+1:03d}",
            "title": doc["title"],
            "text": doc["text"],
            "reference": doc["reference"],
            "jurisdiction": doc.get("jurisdiction", "FR/CH"),
            "tags": doc.get("tags", [vertical]),
        })

    return {
        "vertical": vertical,
        "source": f"Cortex Leman v5 — Generated {datetime.now().strftime('%Y-%m-%d')}",
        "loaded_at": datetime.now().strftime("%Y-%m-%d"),
        "documents": documents,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Cortex Leman v5 — Ajouter une verticale métier en 3 fichiers"
    )
    parser.add_argument("vertical", help="Nom de la verticale (ex: assurance, immobilier)")
    parser.add_argument("--profession", help="Nom de la profession (ex: 'Agent d\\'Assurance')")
    parser.add_argument("--rules", type=int, default=0, help="Nombre de règles (défaut: du profil ou 1)")
    args = parser.parse_args()

    vertical = validate_vertical(args.vertical)

    print()
    print("═══════════════════════════════════════════════════")
    print(f"  Cortex Leman v5 — Nouvelle Verticale: {vertical}")
    print("═══════════════════════════════════════════════════")
    print()

    # Charger le profil s'il existe
    profil = PROFILS.get(vertical, {})

    # Override avec les arguments CLI
    if args.profession:
        profil["profession"] = args.profession

    # Générer les 3 fichiers
    rules_data = generate_rules(vertical, profil)
    serment_text = generate_serment(vertical, profil)
    vault_data = generate_vault(vertical, profil)

    # Écrire les fichiers
    rules_file = RULES_DIR / f"{vertical}.json"
    serment_file = SERMENT_DIR / f"{vertical}.yaml"
    vault_file = VAULT_DIR / f"{vertical}.json"

    rules_file.write_text(json.dumps(rules_data, indent=2, ensure_ascii=False))
    print(f"  ✅ Règles JsonLogic: {rules_file}")
    print(f"     {len(rules_data['rules'])} règle(s)")

    serment_file.write_text(serment_text)
    print(f"  ✅ Serment numérique: {serment_file}")

    vault_file.write_text(json.dumps(vault_data, indent=2, ensure_ascii=False))
    print(f"  ✅ Vault réglementaire: {vault_file}")
    print(f"     {len(vault_data['documents'])} document(s)")

    # Vectoriser dans le RAG
    print()
    print("  🌱 Vectorisation RAG...")
    try:
        sys.path.insert(0, str(ROOT))
        from core.integrations.rag import RAGService
        rag = RAGService()
        regulations = []
        for doc in vault_data["documents"]:
            regulations.append({
                "id": doc["doc_id"],
                "title": doc["title"],
                "content": doc["text"],
                "source": doc["reference"],
                "vertical": vertical,
            })
        chunks = rag.index_regulatory(regulations)
        print(f"     ✅ {chunks} chunks vectorisés dans ChromaDB")
    except Exception as e:
        print(f"     ⚠️  RAG non vectorisé: {e}")
        print(f"     Lancez: python scripts/seed_rag.py")

    print()
    print("═══════════════════════════════════════════════════")
    print(f"  ✅ Verticale '{vertical}' créée avec succès !")
    print()
    print(f"  Prochaines étapes:")
    print(f"    1. Enrichir les règles: {rules_file}")
    print(f"    2. Personnaliser le serment: {serment_file}")
    print(f"    3. Ajouter des docs réglementaires: {vault_file}")
    print(f"    4. Relancer le RAG: python scripts/seed_rag.py")
    print(f"    5. Redémarrer l'API: les règles sont chargées au démarrage")
    print()
    print(f"  Verticales actives: {sorted(VERTICALS_EXISTANTES + [vertical])}")
    print("═══════════════════════════════════════════════════")
    print()


if __name__ == "__main__":
    main()
