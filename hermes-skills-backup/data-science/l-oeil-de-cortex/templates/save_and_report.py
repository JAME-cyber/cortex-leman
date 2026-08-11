#!/usr/bin/env python3
"""
Template: Save ArXiv scan results to DB and generate daily report.
Usage: Update the PAPERS list with today's scan results, then run.
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.expanduser('~/.hermes/data/hermes_research.db')
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
today = datetime.now().strftime('%Y-%m-%d')

# ═══════════════════════════════════════════════════════
# UPDATE THIS SECTION WITH TODAY'S SCAN RESULTS
# Format: (domain, arxiv_id, title, abstract, published_date, category, pdf_url)
# ═══════════════════════════════════════════════════════
PAPERS = [
    # ("gdpr", "XXXX.XXXXX", "Title", "Abstract summary.", "2026-XX-XX", "cs.CR", "https://arxiv.org/abs/XXXX.XXXXX"),
]
# ═══════════════════════════════════════════════════════

# Relevance scoring
KEYWORDS = {
    "gdpr": ["rgpd", "data protection", "privacy", "compliance", "gdpr", "consent", "dark pattern", "cookie"],
    "ai_act": ["ai act", "ai regulation", "artificial intelligence law", "ai governance", "high-risk", "conformity assessment"],
    "vision": ["deepfake", "document verification", "signature detection", "face recognition", "forensic", "watermarking"],
    "ocr": ["ocr", "text recognition", "document analysis", "layout detection", "document parsing", "key information extraction"],
    "fr_ch": ["france", "switzerland", "cross-border", "international", "transnational", "jurisdiction"],
    "security": ["nist", "owasp", "iso", "security", "standard", "fips", "adversarial", "robustness"]
}

def score_relevance(title, abstract, domain):
    content = (title + " " + abstract).lower()
    score = 0.0
    for d, kws in KEYWORDS.items():
        for keyword in kws:
            if keyword in content:
                score += 0.05
    for keyword in KEYWORDS.get(domain, []):
        if keyword in content:
            score += 0.08
    return min(score, 1.0)

# Insert papers
inserted = 0
skipped = 0
for domain, arxiv_id, title, abstract, pub_date, category, pdf_url in PAPERS:
    c.execute('SELECT id FROM arxiv_papers WHERE arxiv_id=?', (arxiv_id,))
    if c.fetchone():
        skipped += 1
        continue
    rel_score = score_relevance(title, abstract, domain)
    is_important = 1 if rel_score >= 0.15 else 0
    c.execute('''INSERT INTO arxiv_papers
        (arxiv_id, title, authors, published_date, category, abstract, pdf_url,
         citation_count, influential_citation_count, relevance_score, domain,
         scanned_date, is_important)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?, ?, ?)''',
        (arxiv_id, title, "", pub_date, category, abstract, pdf_url,
         rel_score, domain, today, is_important))
    inserted += 1

conn.commit()
print(f"Inserted: {inserted}, Skipped (existing): {skipped}")

# ─── Generate Report ───────────────────────────────────
c.execute('''SELECT arxiv_id, title, domain, relevance_score, citation_count,
             published_date, pdf_url, abstract
             FROM arxiv_papers
             WHERE scanned_date=?
             ORDER BY relevance_score DESC, citation_count DESC''', (today,))
papers = c.fetchall()

c.execute('SELECT COUNT(*) FROM arxiv_papers')
total_all = c.fetchone()[0]

high_relevance = [p for p in papers if p[3] >= 0.15]
critical = [p for p in papers if p[3] >= 0.30]
recent = [p for p in papers if p[5] >= (datetime.now().strftime('%Y-%m-%d'))[:-2] + str(int(datetime.now().strftime('%d'))-7).zfill(2)]

c.execute('SELECT domain, COUNT(*) FROM arxiv_papers WHERE scanned_date=? GROUP BY domain', (today,))
domain_counts = dict(c.fetchall())

report = f"""📊 CORTEX LEMAN - ArXiv Daily Report
Date: {today}

📈 STATISTIQUES
─────────────────────────────────
Papers scannés: {len(papers)}
Papers importants (rel ≥ 0.15): {len(high_relevance)} ({100*len(high_relevance)/max(len(papers),1):.1f}%)
High relevance (rel ≥ 0.30): {len(critical)}
High impact (>50 citations): {len([p for p in papers if p[4] > 50])}
Récents (<7 jours): {len(recent)}
Total base de données: {total_all} papers

📂 PAR DOMAIN
─────────────────────────────────"""

for domain, count in sorted(domain_counts.items(), key=lambda x: x[1], reverse=True):
    domain_papers = [p for p in papers if p[2] == domain]
    avg_rel = sum(p[3] for p in domain_papers) / max(len(domain_papers), 1)
    report += f"\n  {domain:12s}: {count:2d} papers | avg relevance: {avg_rel:.3f}"

if critical:
    report += f"""

🚨 ALERTES CRITIQUES (relevance ≥ 0.30)
─────────────────────────────────"""
    for p in critical:
        report += f"""
[{p[2].upper()} | rel={p[3]:.2f}]
Paper: "{p[1][:80]}{'...' if len(p[1])>80 else ''}"
arXiv: {p[0]} | Published: {p[5]} | Citations: {p[4]}
→ {p[7][:120]}{'...' if len(p[7])>120 else ''}"""

if high_relevance:
    report += f"""

📋 PAPERS IMPORTANTS (relevance ≥ 0.15)
─────────────────────────────────"""
    for i, p in enumerate(high_relevance, 1):
        report += f"""
{i}. "{p[1][:75]}{'...' if len(p[1])>75 else ''}"
   arXiv: {p[0]} | {p[2]} | rel={p[3]:.2f} | {p[5]}"""

if recent:
    report += f"""

🆕 PAPERS RÉCENTS (<7 jours)
─────────────────────────────────"""
    for i, p in enumerate(recent, 1):
        report += f"""
{i}. "{p[1][:75]}{'...' if len(p[1])>75 else ''}"
   arXiv: {p[0]} | {p[2]} | rel={p[3]:.2f}"""

report += f"""

📊 MÉTRIQUES VEILLE
─────────────────────────────────
Base de données totale: {total_all} papers
Dernier scan: {today}
Papers aujourd'hui: {len(papers)}
Avg relevance: {sum(p[3] for p in papers)/max(len(papers),1):.3f}
Max relevance: {max((p[3] for p in papers), default=0):.3f}
Domain couverts: {len(domain_counts)}/6

Prochain scan: demain 06:00 CET
💡 Pour approfondir ces résultats, posez vos questions dans votre session Hermes — l'agent peut analyser et détailler chaque papier."""

conn.close()
print(report)
