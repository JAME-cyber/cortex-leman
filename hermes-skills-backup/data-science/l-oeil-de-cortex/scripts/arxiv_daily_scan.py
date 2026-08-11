#!/usr/bin/env python3
"""
ArXiv Daily Scan for Cortex Leman
Scans ArXiv for latest papers in GDPR, AI Act, Computer Vision, OCR, Cross-border compliance
Runs daily via cron job at 6:00 AM CET
"""

import subprocess
import json
import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

# Database path (Hermes profile aware)
DB_PATH = Path.home() / ".hermes" / "data" / "cortex_leman_research.db"

# ArXiv queries for Cortex Leman
QUERIES = {
    "gdpr": {
        "query": "ti:GDPR OR ti:privacy OR ti:compliance",
        "cat": "cs.CR",
        "max": 10
    },
    "ai_act": {
        "query": "ti:AI Act OR ti:AI regulation OR ti:artificial intelligence law OR ti:AI governance",
        "cat": "cs.AI",
        "max": 10
    },
    "vision": {
        "query": "ti:deepfake OR ti:document verification OR ti:signature detection OR ti:face recognition",
        "cat": "cs.CV",
        "max": 15
    },
    "ocr": {
        "query": "ti:OCR OR ti:text recognition OR ti:document analysis OR ti:layout detection",
        "cat": "cs.CV",
        "max": 10
    },
    "fr_ch_compliance": {
        "query": "ti:cross-border OR ti:international OR ti:transnational AND ti:compliance OR ti:regulation OR ti:GDPR",
        "cat": "cs.CR",
        "max": 10
    },
    "security_standards": {
        "query": "ti:NIST OR ti:OWASP OR ti:standard AND ti:security OR ti:compliance",
        "cat": "cs.CR",
        "max": 10
    }
}

# Keywords for relevance scoring
KEYWORDS_CORTEX_LEMAN = {
    "gdpr": ["GDPR", "data protection", "privacy", "compliance", "regulation", "Article 22"],
    "ai_act": ["AI Act", "AI regulation", "artificial intelligence law", "AI governance", "EU AI"],
    "vision": ["deepfake", "document verification", "signature detection", "face recognition", "vision"],
    "ocr": ["OCR", "text recognition", "document analysis", "layout detection", "table extraction"],
    "fr_ch": ["France", "Switzerland", "cross-border", "international", "transnational", "FR-CH"]
}


def init_database():
    """Initialize SQLite database for research papers"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS arxiv_papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            arxiv_id TEXT UNIQUE,
            title TEXT,
            authors TEXT,
            published_date TEXT,
            category TEXT,
            abstract TEXT,
            pdf_url TEXT,
            citation_count INTEGER DEFAULT 0,
            influential_citation_count INTEGER DEFAULT 0,
            relevance_score REAL DEFAULT 0.0,
            domain TEXT,
            scanned_date TEXT,
            is_important BOOLEAN DEFAULT 0
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS paper_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paper_id INTEGER REFERENCES arxiv_papers(id),
            alert_type TEXT,
            sent_to TEXT,
            action_taken TEXT,
            created_at TEXT
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_arxiv_papers_domain ON arxiv_papers(domain)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_arxiv_papers_date ON arxiv_papers(published_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_arxiv_papers_relevance ON arxiv_papers(relevance_score)")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized: {DB_PATH}")


def parse_arxiv_xml(xml_string):
    """Parse ArXiv XML response and extract paper data"""
    ns = {'a': 'http://www.w3.org/2005/Atom'}
    root = ET.fromstring(xml_string)
    
    papers = []
    for entry in root.findall('a:entry', ns):
        paper = {
            'arxiv_id': entry.find('a:id', ns).text.strip().split('/abs/')[-1],
            'title': entry.find('a:title', ns).text.strip().replace('\n', ' '),
            'authors': ', '.join(a.find('a:name', ns).text for a in entry.findall('a:author', ns)),
            'published': entry.find('a:published', ns).text[:10],
            'summary': entry.find('a:summary', ns).text.strip()[:500],
            'categories': ', '.join(c.get('term') for c in entry.findall('a:category', ns)),
            'pdf_url': f"https://arxiv.org/pdf/{entry.find('a:id', ns).text.strip().split('/abs/')[-1]}"
        }
        papers.append(paper)
    
    return papers


def calculate_relevance_score(paper):
    """Calculate relevance score for Cortex Leman (0-1)"""
    title = paper.get('title', '').lower()
    summary = paper.get('summary', '').lower()
    content = title + ' ' + summary
    
    score = 0.0
    
    # Check each domain's keywords
    for domain, keywords in KEYWORDS_CORTEX_LEMAN.items():
        domain_score = 0
        for keyword in keywords:
            if keyword.lower() in content:
                domain_score += 1
        
        # Normalize domain score (max 1 per domain)
        if domain_score > 0:
            score += min(domain_score / len(keywords), 1.0)
    
    # Normalize final score (max 1.0)
    max_possible = len(KEYWORDS_CORTEX_LEMAN)
    return min(score / max_possible, 1.0)


def save_papers_to_db(papers, domain):
    """Save papers to database, handling duplicates"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    scanned_date = datetime.now().strftime("%Y-%m-%d")
    saved_count = 0
    updated_count = 0
    
    for paper in papers:
        arxiv_id = paper['arxiv_id']
        title = paper['title']
        authors = paper['authors']
        published_date = paper['published']
        summary = paper['summary']
        pdf_url = paper['pdf_url']
        categories = paper['categories']
        
        # Calculate relevance score
        relevance_score = calculate_relevance_score(paper)
        
        # Mark as important if relevance > 0.8
        is_important = 1 if relevance_score > 0.8 else 0
        
        try:
            cursor.execute("""
                INSERT INTO arxiv_papers 
                (arxiv_id, title, authors, published_date, category, abstract, pdf_url, 
                 relevance_score, domain, scanned_date, is_important)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (arxiv_id, title, authors, published_date, categories, summary, pdf_url,
                  relevance_score, domain, scanned_date, is_important))
            saved_count += 1
            print(f"  ✅ NEW: {arxiv_id} - {title[:60]}... (relevance: {relevance_score:.2f})")
        except sqlite3.IntegrityError:
            # Paper already exists, update metadata if needed
            cursor.execute("""
                UPDATE arxiv_papers 
                SET scanned_date = ?, relevance_score = ?, category = ?
                WHERE arxiv_id = ?
            """, (scanned_date, relevance_score, categories, arxiv_id))
            updated_count += 1
            print(f"  📝 UPDATE: {arxiv_id} - {title[:60]}... (relevance: {relevance_score:.2f})")
    
    conn.commit()
    conn.close()
    
    return saved_count, updated_count


def run_arxiv_scan():
    """Run daily ArXiv scan for all domains"""
    print("=" * 70)
    print(f"🔬 CORTEX LEMAN - ArXiv Daily Scan")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Initialize database
    init_database()
    
    # Scan each domain
    total_papers = 0
    total_saved = 0
    total_updated = 0
    important_papers = []
    
    for domain, config in QUERIES.items():
        print(f"\n📚 Scanning domain: {domain.upper()}")
        print(f"   Query: {config['query'][:80]}...")
        
        # Build ArXiv API URL
        query_encoded = config['query'].replace(' ', '+')
        url = (f"https://export.arxiv.org/api/query?"
               f"search_query={query_encoded}&cat:{config['cat']}&"
               f"sortBy=submittedDate&sortOrder=descending&max_results={config['max']}")
        
        # Fetch data
        try:
            output = subprocess.run(
                ["curl", "-s", url],
                capture_output=True,
                text=True,
                timeout=30
            ).stdout
            
            papers = parse_arxiv_xml(output)
            total_papers += len(papers)
            
            # Save to database
            saved, updated = save_papers_to_db(papers, domain)
            total_saved += saved
            total_updated += updated
            
            # Track important papers
            for paper in papers:
                if calculate_relevance_score(paper) > 0.8:
                    important_papers.append({
                        **paper,
                        'domain': domain,
                        'relevance': calculate_relevance_score(paper)
                    })
            
            print(f"   ✅ {len(papers)} papers retrieved ({saved} new, {updated} updated)")
            
        except subprocess.TimeoutExpired:
            print(f"   ❌ Timeout fetching {domain}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Generate summary
    print("\n" + "=" * 70)
    print("📊 SCAN SUMMARY")
    print("=" * 70)
    print(f"Total papers retrieved: {total_papers}")
    print(f"New papers saved: {total_saved}")
    print(f"Existing papers updated: {total_updated}")
    print(f"Important papers (relevance > 0.8): {len(important_papers)}")
    
    # Show important papers
    if important_papers:
        print("\n⭐ IMPORTANT PAPERS")
        print("=" * 70)
        for i, paper in enumerate(important_papers, 1):
            print(f"\n{i}. [{paper['domain'].upper()}] {paper['arxiv_id']}")
            print(f"   Title: {paper['title'][:80]}...")
            print(f"   Relevance: {paper['relevance']:.2f} | Authors: {paper['authors'][:50]}...")
            print(f"   Published: {paper['published']} | PDF: {paper['pdf_url']}")
    
    print("\n" + "=" * 70)
    print(f"✅ Scan completed successfully!")
    print(f"Next scan: Tomorrow at 06:00 AM CET")
    print("=" * 70)
    
    return {
        'total_papers': total_papers,
        'new_papers': total_saved,
        'updated_papers': total_updated,
        'important_papers': len(important_papers),
        'important_paper_list': important_papers
    }


if __name__ == "__main__":
    run_arxiv_scan()
