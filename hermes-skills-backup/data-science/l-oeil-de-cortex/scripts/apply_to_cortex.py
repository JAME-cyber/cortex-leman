#!/usr/bin/env python3
"""
L'OEIL DE CORTEX → Cortex Leman Integration

Boucle fermée: papers ArXiv high-relevance → mise à jour Cortex Leman.

Pour chaque paper high-relevance non traité:
  1. L'agent LLM analyse le paper
  2. Génère des règles/compléments compliance au format Cortex Leman
  3. Injecte dans le bon composant:
     - core/mediator/rules/{vertical}.json  → nouvelles règles
     - data/vault/shared/regulatory/         → textes réglementaires
     - data/arxiv_advisories/                → advisories pour les agents
  4. Notifie via Telegram
  5. Journalise dans le journal Cortex Leman
"""

import os
import json
import sqlite3
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Charger .env hermes
_env_file = Path.home() / ".hermes" / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _key, _, _val = _line.partition("=")
            os.environ.setdefault(_key.strip(), _val.strip())

# Paths
DB_PATH = Path.home() / ".hermes" / "data" / "hermes_research.db"
CORTEX_V5 = Path.home() / "cortex-leman-v5"
PROCESSED_LOG = Path.home() / ".hermes" / "data" / "cortex_applied.json"
ADVISORY_DIR = Path.home() / ".hermes" / "data" / "arxiv_advisories"

# API
OPENROUTER_API = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# Telegram
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID") or os.environ.get("TELEGRAM_HOME_CHANNEL")

# Seuil pour appliquer (plus élevé que le simple alerting)
APPLY_THRESHOLD = float(os.environ.get("ARXIV_APPLY_THRESHOLD", "0.75"))


def load_processed():
    if PROCESSED_LOG.exists():
        try:
            return json.loads(PROCESSED_LOG.read_text())
        except:
            return {}
    return {}


def save_processed(data):
    PROCESSED_LOG.parent.mkdir(parents=True, exist_ok=True)
    PROCESSED_LOG.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def get_eligible_papers():
    """Papers high-relevance pas encore appliqués"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT arxiv_id, title, abstract, domain, relevance_score,
               citation_count, published_date, pdf_url
        FROM arxiv_papers
        WHERE relevance_score >= ?
        ORDER BY relevance_score DESC
        LIMIT 5
    ''', (APPLY_THRESHOLD,))
    papers = [dict(zip(
        ["arxiv_id", "title", "abstract", "domain", "relevance_score",
         "citation_count", "published_date", "pdf_url"], row
    )) for row in cursor.fetchall()]
    conn.close()
    return papers


def get_cortex_context():
    """Lit le contexte Cortex Leman actuel pour le donner à l'agent"""
    context = {
        "verticals": [],
        "existing_rules": {},
        "regulatory_docs": [],
    }

    # Verticales disponibles
    rules_dir = CORTEX_V5 / "core" / "mediator" / "rules"
    if rules_dir.exists():
        for rf in rules_dir.glob("*.json"):
            vertical = rf.stem
            context["verticals"].append(vertical)
            try:
                data = json.loads(rf.read_text())
                rules = data.get("rules", [])
                context["existing_rules"][vertical] = [
                    {"id": r.get("id"), "name": r.get("name"), "action": r.get("action")}
                    for r in rules
                ]
            except:
                pass

    # Regulatory docs
    reg_dir = CORTEX_V5 / "data" / "vault" / "shared" / "regulatory"
    if reg_dir.exists():
        for rf in reg_dir.glob("*.json"):
            try:
                doc = json.loads(rf.read_text())
                context["regulatory_docs"].append({
                    "id": doc.get("id"),
                    "title": doc.get("title"),
                    "source": doc.get("source"),
                })
            except:
                pass

    return context


def ask_agent_to_generate_updates(paper, cortex_context):
    """Demande à l'agent de générer des mises à jour concrètes pour Cortex Leman"""

    rules_summary = json.dumps(cortex_context["existing_rules"], indent=2, ensure_ascii=False)
    reg_summary = json.dumps(cortex_context["regulatory_docs"], indent=2, ensure_ascii=False)

    prompt = f"""Tu es L'Architecte Lémanique. Un paper ArXiv pertinent a été détecté pour Cortex Leman.
Ta mission: décider SI et COMMENT mettre à jour le système Cortex Leman.

## PAPER DÉTECTÉ
- Titre: {paper['title']}
- arXiv: {paper['arxiv_id']}
- Domaine: {paper['domain']}
- Score: {paper['relevance_score']}/1.0
- PDF: {paper['pdf_url']}

## ABSTRACT
{paper['abstract']}

## CONTEXTE CORTEX LEMAN ACTUEL
Verticales: {', '.join(cortex_context['verticals'])}

Règles existantes:
{rules_summary}

Textes réglementaires:
{reg_summary}

## TA RÉPONSE (JSON STRICT)

Réponds UNIQUEMENT en JSON valide avec cette structure:

```json
{{
  "should_update": true/false,
  "reason": "Pourquoi on met à jour (ou pas)",
  "actions": [
    {{
      "type": "add_rule",
      "vertical": "comptable",
      "rule": {{
        "id": "comptable-XXX",
        "name": "Nom de la règle",
        "severity": "medium",
        "condition": {{ "==" : [{{"var": "action.type"}}, "quelque_chose"] }},
        "action": "warn",
        "message": "Message explicatif"
      }}
    }},
    {{
      "type": "add_regulatory",
      "doc": {{
        "id": "arXiv-XXXX-XXXX",
        "title": "Titre du papier",
        "content": "Résumé des exigences pertinentes pour Cortex Leman",
        "source": "arXiv: {paper['arxiv_id']}",
        "vertical": "all"
      }}
    }}
  ]
}}
```

Types d'actions possibles:
- `add_rule`: Ajouter une règle dans core/mediator/rules/{{vertical}}.json
- `add_regulatory`: Ajouter un texte dans le Knowledge Vault
- `add_advisory`: Générer un advisory pour les agents

Sois CONSERVATEUR. Ne propose des mises à jour QUE si le paper apporte réellement quelque chose de nouveau par rapport aux règles existantes. Si le paper n'est pas assez concret, mets should_update à false."""

    if not OPENROUTER_KEY:
        return {"should_update": False, "reason": "Pas de clé API disponible", "actions": []}

    try:
        response = requests.post(
            OPENROUTER_API,
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 2000
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENROUTER_KEY}"
            },
            timeout=60
        )
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            # Extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            return json.loads(content.strip())
        else:
            return {"should_update": False, "reason": f"HTTP {response.status_code}", "actions": []}
    except json.JSONDecodeError as e:
        return {"should_update": False, "reason": f"JSON parse error: {e}", "actions": []}
    except Exception as e:
        return {"should_update": False, "reason": f"Error: {e}", "actions": []}


def apply_add_rule(vertical, rule):
    """Ajoute une règle au fichier vertical"""
    rules_file = CORTEX_V5 / "core" / "mediator" / "rules" / f"{vertical}.json"

    if not rules_file.exists():
        return False, f"Pas de fichier règles pour {vertical}"

    try:
        data = json.loads(rules_file.read_text())
        existing_ids = {r["id"] for r in data.get("rules", [])}

        if rule["id"] in existing_ids:
            return False, f"Règle {rule['id']} existe déjà"

        data["rules"].append(rule)
        rules_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        return True, f"Règle {rule['id']} ajoutée à {vertical}"
    except Exception as e:
        return False, str(e)


def apply_add_regulatory(doc):
    """Ajoute un document réglementaire au Knowledge Vault"""
    reg_dir = CORTEX_V5 / "data" / "vault" / "shared" / "regulatory"
    reg_dir.mkdir(parents=True, exist_ok=True)

    doc_path = reg_dir / f"{doc['id']}.json"
    if doc_path.exists():
        return False, f"Document {doc['id']} existe déjà"

    try:
        doc_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False))
        return True, f"Document réglementaire {doc['id']} ajouté"
    except Exception as e:
        return False, str(e)


def apply_add_advisory(paper, analysis):
    """Génère un advisory pour les agents Cortex Leman"""
    ADVISORY_DIR.mkdir(parents=True, exist_ok=True)

    advisory = {
        "id": f"advisory-{paper['arxiv_id']}",
        "type": "arxiv_insight",
        "source": f"arXiv:{paper['arxiv_id']}",
        "title": paper["title"],
        "domain": paper["domain"],
        "relevance_score": paper["relevance_score"],
        "summary": analysis.get("reason", ""),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "pending_review",
        "actions_proposed": len(analysis.get("actions", [])),
    }

    advisory_path = ADVISORY_DIR / f"{advisory['id']}.json"
    advisory_path.write_text(json.dumps(advisory, indent=2, ensure_ascii=False))
    return True, f"Advisory {advisory['id']} créé"


def send_telegram_report(paper, result):
    """Envoie le rapport d'application sur Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False

    if not result.get("should_update"):
        msg = f"📋 Paper analysé — pas de mise à jour nécessaire\n\n📄 {paper['title'][:80]}\n💡 {result.get('reason', '')}"
    else:
        actions_applied = result.get("_applied", [])
        actions_text = "\n".join(f"  {'✅' if ok else '⏭️'} {msg}" for ok, msg in actions_applied)

        msg = f"""🔧 CORTEX LEMAN MIS À JOUR

📄 {paper['title'][:80]}
🏷 {paper['arxiv_id']} | Score: {paper['relevance_score']:.2f}

💡 {result.get('reason', '')}

ACTIONS:
{actions_text}

⚡ Changements appliqués automatiquement."""

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg,
            "parse_mode": "Markdown"
        }, timeout=10)
        return True
    except:
        return False


def main():
    print("🔄 L'OEIL DE CORTEX → Cortex Leman Integration")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Seuil application: {APPLY_THRESHOLD}")
    print()

    processed = load_processed()
    papers = get_eligible_papers()
    cortex_context = get_cortex_context()

    new_papers = [p for p in papers if p["arxiv_id"] not in processed]

    if not new_papers:
        print("✅ Aucun nouveau paper à appliquer")
        return

    print(f"📋 {len(new_papers)} papers éligibles")
    print(f"🏗️  Cortex Leman: {len(cortex_context['verticals'])} verticales, "
          f"{sum(len(r) for r in cortex_context['existing_rules'].values())} règles existantes")
    print()

    for paper in new_papers:
        print(f"🔍 {paper['arxiv_id']} ({paper['relevance_score']:.2f}) — {paper['title'][:70]}")

        # Demander à l'agent
        print("  🤖 Analyse agent...")
        result = ask_agent_to_generate_updates(paper, cortex_context)

        if not result.get("should_update"):
            print(f"  ⏭️  Pas de mise à jour: {result.get('reason', '')}")
            processed[paper["arxiv_id"]] = {
                "date": datetime.now().isoformat(),
                "action": "skipped",
                "reason": result.get("reason", "")
            }
            save_processed(processed)
            continue

        # Appliquer les actions
        applied = []
        for action in result.get("actions", []):
            action_type = action.get("type")

            if action_type == "add_rule":
                vertical = action.get("vertical")
                rule = action.get("rule")
                if vertical and rule:
                    ok, msg = apply_add_rule(vertical, rule)
                    applied.append((ok, msg))
                    if ok:
                        # Update context for next papers
                        if vertical not in cortex_context["existing_rules"]:
                            cortex_context["existing_rules"][vertical] = []
                        cortex_context["existing_rules"][vertical].append(
                            {"id": rule["id"], "name": rule["name"]}
                        )

            elif action_type == "add_regulatory":
                doc = action.get("doc")
                if doc:
                    ok, msg = apply_add_regulatory(doc)
                    applied.append((ok, msg))

            elif action_type == "add_advisory":
                ok, msg = apply_add_advisory(paper, result)
                applied.append((ok, msg))

        # Toujours créer un advisory
        ok, msg = apply_add_advisory(paper, result)
        applied.append((ok, msg))

        result["_applied"] = applied

        # Logger
        for ok, msg in applied:
            status = "✅" if ok else "⏭️"
            print(f"  {status} {msg}")

        # Notifier
        send_telegram_report(paper, result)
        print("  📨 Telegram notifié")

        # Marquer traité
        processed[paper["arxiv_id"]] = {
            "date": datetime.now().isoformat(),
            "action": "applied",
            "updates": [msg for ok, msg in applied if ok]
        }
        save_processed(processed)
        print()

    print(f"✅ Traitement terminé — {len(new_papers)} papers évalués")


if __name__ == "__main__":
    main()
