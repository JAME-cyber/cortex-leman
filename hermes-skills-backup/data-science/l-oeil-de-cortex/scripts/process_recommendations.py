#!/usr/bin/env python3
"""
L'OEIL DE CORTEX - Process Recommendations
Script autonome qui demande à l'agent Hermes de traiter les papers high-relevance.
Pour chaque paper au-dessus du seuil, l'agent:
  1. Analyse le paper (abstract + PDF)
  2. Évalue l'impact sur Cortex Leman (compliance, vision, OCR, etc.)
  3. Propose des actions concrètes (maj contrôles, nouveau check, etc.)
  4. Envoie un résumé actionnable via Telegram
"""

import os
import json
import sqlite3
import requests
from datetime import datetime
from pathlib import Path

DB_PATH = Path.home() / ".hermes" / "data" / "hermes_research.db"
PROCESSED_LOG = Path.home() / ".hermes" / "data" / "arxiv_processed.json"

# Charger .env
_env_file = Path.home() / ".hermes" / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _key, _, _val = _line.partition("=")
            os.environ.setdefault(_key.strip(), _val.strip())

# Hermes API (OpenAI-compatible) ou fallback OpenRouter direct
HERMES_API = os.environ.get("HERMES_API_URL", "http://localhost:8642/v1/chat/completions")
OPENROUTER_API = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# Seuil pour déclencher l'analyse agent
HIGH_RELEVANCE_THRESHOLD = float(os.environ.get("HIGH_RELEVANCE_THRESHOLD", "0.6"))

# Telegram pour notification finale
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID") or os.environ.get("TELEGRAM_HOME_CHANNEL")


def load_processed():
    """Charge la liste des papers déjà traités"""
    if PROCESSED_LOG.exists():
        try:
            return set(json.loads(PROCESSED_LOG.read_text()))
        except:
            return set()
    return set()


def save_processed(processed):
    """Sauvegarde la liste des papers traités"""
    PROCESSED_LOG.parent.mkdir(parents=True, exist_ok=True)
    PROCESSED_LOG.write_text(json.dumps(list(processed)[-500:]))  # Garder les 500 derniers


def get_high_relevance_papers(threshold=HIGH_RELEVANCE_THRESHOLD):
    """Récupère les papers non-traités au-dessus du seuil"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT arxiv_id, title, abstract, authors, domain, relevance_score,
                   citation_count, published_date, pdf_url, category
            FROM arxiv_papers
            WHERE relevance_score >= ?
            ORDER BY relevance_score DESC
            LIMIT 10
        ''', (threshold,))

        papers = []
        for row in cursor.fetchall():
            papers.append({
                "arxiv_id": row[0],
                "title": row[1],
                "abstract": row[2],
                "authors": row[3],
                "domain": row[4],
                "relevance_score": row[5],
                "citation_count": row[6],
                "published_date": row[7],
                "pdf_url": row[8],
                "category": row[9]
            })
        return papers
    finally:
        conn.close()


def ask_hermes_agent(paper):
    """Envoie le paper à l'agent Hermes (API server) ou fallback vers OpenRouter direct"""

    prompt = f"""Tu es L'Architecte Lémanique, expert compliance et technologie pour Cortex Leman.
Analyse ce paper ArXiv et propose des actions concrètes.

## PAPER
- **Titre**: {paper['title']}
- **arXiv**: {paper['arxiv_id']}
- **Domaine**: {paper['domain']}
- **Score pertinence**: {paper['relevance_score']}/1.0
- **Citations**: {paper['citation_count']}
- **Publié le**: {paper['published_date']}
- **PDF**: {paper['pdf_url']}

## ABSTRACT
{paper['abstract']}

## TA MISSION
1. **Résumé** (2-3 phrases): De quoi parle ce paper?
2. **Impact Cortex Leman** (1-2 phrases): Pourquoi c'est pertinent pour notre système de compliance cross-border FR-CH?
3. **Actions concrètes** (1-3 actions): Que devrait-on faire?
   - Nouveau contrôle à ajouter?
   - Module OCR/Vision à mettre à jour?
   - Changement réglementaire à anticiper?
   - Architecture à adapter?

Sois précis et actionnable. Pas de blabla."""

    # Try Hermes API server first
    try:
        response = requests.post(
            HERMES_API,
            json={
                "model": "hermes-agent",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 800
            },
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
    except requests.exceptions.ConnectionError:
        pass  # Fallback to OpenRouter
    except Exception:
        pass  # Fallback to OpenRouter

    # Fallback: OpenRouter direct
    if not OPENROUTER_KEY:
        return "⚠️ Ni Hermes API ni OPENROUTER_API_KEY disponibles"

    try:
        response = requests.post(
            OPENROUTER_API,
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 800
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENROUTER_KEY}"
            },
            timeout=60
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        else:
            return f"⚠️ Erreur OpenRouter (HTTP {response.status_code})"
    except Exception as e:
        return f"⚠️ Erreur: {e}"


def send_telegram_summary(paper, analysis):
    """Envoie l'analyse via Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️  Telegram non configuré, skip notification")
        return False

    # Truncate analysis to Telegram limits
    if len(analysis) > 3500:
        analysis = analysis[:3500] + "\n\n✂️ (tronqué)"

    message = f"""🧠 **ANALYSE AGENT — Paper High-Relevance**

📄 **{paper['title'][:80]}**
🏷 `{paper['arxiv_id']}` | {paper['domain']} | Score: {paper['relevance_score']:.2f}

{analysis}

🔗 [PDF]({paper['pdf_url']})"""

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"⚠️  Erreur Telegram: {e}")
        return False


def save_analysis_report(papers_analyses):
    """Sauvegarde le rapport d'analyse"""
    report_path = Path.home() / ".hermes" / "data" / f"arxiv_agent_analysis_{datetime.now().strftime('%Y%m%d')}.json"

    report = {
        "date": datetime.now().isoformat(),
        "papers_analyzed": len(papers_analyses),
        "analyses": papers_analyses
    }

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    return report_path


def main():
    print("🧠 L'OEIL DE CORTEX - Process Recommendations")
    print(f"⏰ Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Seuil: {HIGH_RELEVANCE_THRESHOLD}")
    print()

    # Load already processed papers
    processed = load_processed()

    # Get high relevance papers
    papers = get_high_relevance_papers()

    # Filter out already processed
    new_papers = [p for p in papers if p["arxiv_id"] not in processed]

    if not new_papers:
        print("✅ Aucun nouveau paper à traiter par l'agent")
        return

    print(f"📋 {len(new_papers)} papers à analyser par l'agent")
    print()

    analyses = []

    for i, paper in enumerate(new_papers, 1):
        print(f"[{i}/{len(new_papers)}] {paper['arxiv_id']} (score: {paper['relevance_score']:.2f})")
        print(f"  → {paper['title'][:70]}")

        # Ask Hermes agent
        print("  🤖 Envoi à l'agent Hermes...")
        analysis = ask_hermes_agent(paper)

        if analysis.startswith("⚠️"):
            print(f"  {analysis}")
            continue

        print(f"  ✅ Analyse reçue ({len(analysis)} chars)")

        # Send via Telegram
        if send_telegram_summary(paper, analysis):
            print("  📨 Résumé envoyé sur Telegram")

        # Mark as processed
        processed.add(paper["arxiv_id"])

        analyses.append({
            "arxiv_id": paper["arxiv_id"],
            "title": paper["title"],
            "domain": paper["domain"],
            "relevance_score": paper["relevance_score"],
            "analysis": analysis
        })

        print()

    # Save processed list
    save_processed(processed)

    # Save analysis report
    report_path = save_analysis_report(analyses)
    print(f"📄 Rapport sauvegardé: {report_path}")
    print()
    print(f"✅ {len(analyses)} papers analysés par l'agent")


if __name__ == "__main__":
    main()
