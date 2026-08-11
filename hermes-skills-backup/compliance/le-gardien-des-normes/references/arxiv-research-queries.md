# ArXiv Research Queries — Veille Réglementaire

**Database:** `/home/tars/.hermes/data/hermes_research.db` (SQLite)
**Advisories:** `/home/tars/.hermes/data/arxiv_advisories/`
**Applied advisories:** `/home/tars/.hermes/data/cortex_applied.json`
**Last verified:** 2026-05-04

## Statistiques (au 2026-05-04)

| Domaine | Papers |
|---------|--------|
| gdpr | 92 |
| ai_act | 52 |
| fr_ch | 35 |
| security | 25 |
| ocr | 91 |
| vision | 126 |
| **Total** | **421** |

## Tables

### `arxiv_papers`

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| arxiv_id | TEXT UNIQUE | Identifiant ArXiv (ex: 2604.13767v1) |
| title | TEXT | Titre du paper |
| authors | TEXT | Auteurs |
| published_date | TEXT | Date de publication |
| category | TEXT | Catégorie ArXiv (cs.CR, cs.AI, etc.) |
| abstract | TEXT | Résumé |
| pdf_url | TEXT | Lien PDF |
| citation_count | INTEGER | Citations (Semantic Scholar) |
| influential_citation_count | INTEGER | Citations influentes |
| relevance_score | REAL | Score de pertinence Cortex Leman (0-1) |
| domain | TEXT | Domaine (gdpr, ai_act, fr_ch, security, vision, ocr) |
| scanned_date | TEXT | Date du scan |
| is_important | BOOLEAN | Flag importance |

### `paper_alerts`

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| paper_id | INTEGER FK | Référence vers arxiv_papers |
| alert_type | TEXT | HIGH_IMPACT, HIGH_RELEVANCE, RECENT |
| sent_to | TEXT | Destinataires (ex: "Le Gardien des Normes, L'Architecte Lémanique") |
| action_taken | TEXT | Action prise (NULL si pas encore traité) |
| created_at | TEXT | Date de création de l'alerte |

## Requêtes de Veille

```python
import sqlite3

def check_research_updates(db_path="/home/tars/.hermes/data/hermes_research.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    results = {}
    
    # 1. Papers importants non traités
    c.execute("""
        SELECT p.arxiv_id, p.title, p.domain, p.relevance_score, p.published_date
        FROM arxiv_papers p
        LEFT JOIN paper_alerts a ON p.id = a.paper_id AND a.action_taken IS NOT NULL
        WHERE p.is_important = 1 AND a.id IS NULL
        ORDER BY p.published_date DESC
    """)
    results["unprocessed_important"] = c.fetchall()
    
    # 2. Nouveaux papers GDPR/AI Act (7 derniers jours)
    c.execute("""
        SELECT arxiv_id, title, domain, relevance_score, published_date
        FROM arxiv_papers
        WHERE domain IN ('gdpr', 'ai_act')
        AND published_date >= date('now', '-7 days')
        ORDER BY relevance_score DESC
    """)
    results["recent_compliance_papers"] = c.fetchall()
    
    # 3. Alertes non traitées
    c.execute("""
        SELECT p.arxiv_id, p.title, a.alert_type, a.created_at
        FROM paper_alerts a
        JOIN arxiv_papers p ON a.paper_id = p.id
        WHERE a.action_taken IS NULL
        ORDER BY a.created_at DESC
    """)
    results["pending_alerts"]
    
    # 4. High relevance papers (>=0.8)
    c.execute("""
        SELECT arxiv_id, title, domain, relevance_score, published_date
        FROM arxiv_papers
        WHERE relevance_score >= 0.8
        ORDER BY published_date DESC
    """)
    results["high_relevance"] = c.fetchall()
    
    conn.close()
    return results
```

## Papers Critiques Identifiés (Persistants)

| ArXiv ID | Titre | Domaine | Relevance | Action |
|----------|-------|---------|-----------|--------|
| 2604.13767v1 | Making AI Compliance Evidence Machine-Readable | gdpr | 0.85 | Règle comptable-012 intégrée |
| 2604.22789v1 | UGAF-ITS: Standards Harmonization Framework | ai_act | 0.84 | Règle comptable-009 intégrée |
| 2503.20464v1 | Modelling Privacy Compliance in Cross-border Data Transfers | fr_ch | 0.80 | Règle comptable-010 intégrée |
| 2603.22920 | The EU AI Act and the Rights-Based Approach | fr_ch | 0.79 | Règle comptable-011 intégrée |
| 2501.09182v1 | Blockchain-Enabled Approach to Cross-Border Compliance | fr_ch | 0.76 | Règle comptable-012 intégrée |

## Advisory Format

```json
{
  "id": "advisory-<arxiv_id>",
  "type": "arxiv_insight",
  "source": "arXiv:<arxiv_id>",
  "title": "<paper_title>",
  "domain": "<domain>",
  "relevance_score": 0.85,
  "summary": "<résumé en français pour Le Gardien>",
  "generated_at": "<ISO datetime>"
}
```

## Pipeline ArXiv (Cron)

1. **Scan quotidien** (6h00 CET) — `scripts/arxiv_daily_scan.py`
2. **Impact analysis** (6h30 CET) — `scripts/analyze_papers.py` (Semantic Scholar API)
3. **Scoring** (7h00 CET) — `scripts/score_relevance.py`
4. **Alertes** (7h30 CET) — `scripts/alert_papers.py`
5. **Weekly report** (Lundi 9h00 CET) — Rapport pour L'Architecte Lémanique

**Note :** Le script `analyze_papers.py` peut bloquer indéfiniment (API Semantic Scholar). Voir troubleshooting dans le skill `l-oeil-de-cortex-arxiv-integration`.
