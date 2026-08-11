#!/usr/bin/env python3
"""
Relevance Scoring for Cortex Leman Papers
Scores papers based on their relevance to Cortex Leman's mission
"""

import sqlite3
from pathlib import Path
from typing import Dict, List
import re

# Database path (Hermes profile aware)
DB_PATH = Path.home() / ".hermes" / "data" / "cortex_leman_research.db"


# Keywords for each domain
KEYWORDS_CORTEX_LEMAN = {
    "gdpr": [
        "GDPR", "data protection", "privacy", "compliance", "regulation",
        "Article 22", "automated decision making", "data subject", "right to explanation",
        "consent", "data processing", "data controller", "data processor",
        "privacy by design", "privacy by default", "data portability", "right to be forgotten"
    ],
    "ai_act": [
        "AI Act", "AI regulation", "artificial intelligence law", "AI governance",
        "EU AI", "high-risk AI", "AI systems", "AI classification", "AI risk assessment",
        "AI transparency", "AI accountability", "AI oversight", "AI compliance",
        "conformity assessment", "notified body", "AI provider", "AI user"
    ],
    "vision": [
        "deepfake", "document verification", "signature detection", "face recognition",
        "computer vision", "CV", "image recognition", "object detection", "document forgery",
        "signature verification", "biometric", "face detection", "image classification",
        "visual inspection", "document authentication", "tampering detection"
    ],
    "ocr": [
        "OCR", "optical character recognition", "text recognition", "document analysis",
        "layout detection", "table extraction", "document segmentation", "text extraction",
        "handwriting recognition", "document parsing", "structured extraction",
        "document layout", "document classification", "text detection"
    ],
    "fr_ch": [
        "France", "Switzerland", "cross-border", "international", "transnational",
        "FR-CH", "Franco-Swiss", "France-Suisse", "border data transfer",
        "international compliance", "transnational regulation", "cross-border data flow",
        "data transfer mechanism", "adequacy decision", "standard contractual clauses"
    ],
    "security": [
        "NIST", "OWASP", "ISO 27001", "security", "cybersecurity", "vulnerability",
        "penetration testing", "security audit", "threat modeling", "risk assessment",
        "security controls", "zero trust", "defense in depth", "security framework",
        "information security", "data security", "application security"
    ]
}

# Domain weights for scoring
DOMAIN_WEIGHTS = {
    "gdpr": 1.2,      # Higher weight - critical for compliance
    "ai_act": 1.2,    # Higher weight - critical for compliance
    "vision": 1.0,    # Standard weight - core technology
    "ocr": 1.0,       # Standard weight - core technology
    "fr_ch": 1.1,     # Slightly higher - target market
    "security": 1.1   # Slightly higher - enterprise requirement
}


def calculate_keyword_score(content: str, keywords: List[str]) -> float:
    """
    Calculate keyword match score for a domain
    
    Args:
        content: Text content (title + abstract)
        keywords: List of keywords to search for
    
    Returns:
        Score between 0 and 1
    """
    content_lower = content.lower()
    matches = 0
    
    for keyword in keywords:
        if keyword.lower() in content_lower:
            matches += 1
    
    # Normalize by number of keywords
    return matches / len(keywords)


def calculate_relevance_score(paper: Dict) -> float:
    """
    Calculate overall relevance score for Cortex Leman (0-1)
    
    Args:
        paper: Paper dictionary with 'title', 'summary', 'category'
    
    Returns:
        Relevance score between 0 and 1
    """
    title = paper.get('title', '')
    summary = paper.get('summary', '')
    content = title + ' ' + summary
    
    total_score = 0.0
    max_possible = len(DOMAIN_WEIGHTS)
    
    for domain, keywords in KEYWORDS_CORTEX_LEMAN.items():
        domain_score = calculate_keyword_score(content, keywords)
        
        # Apply domain weight
        weighted_score = domain_score * DOMAIN_WEIGHTS[domain]
        total_score += weighted_score
    
    # Normalize final score
    max_weighted = sum(DOMAIN_WEIGHTS.values())
    final_score = min(total_score / max_weighted, 1.0)
    
    return round(final_score, 2)


def classify_paper_importance(relevance_score: float, citation_count: int = 0) -> str:
    """
    Classify paper importance based on relevance and citations
    
    Args:
        relevance_score: Relevance score (0-1)
        citation_count: Number of citations
    
    Returns:
        Importance category: 'critical', 'high', 'medium', 'low'
    """
    if relevance_score >= 0.8:
        return 'critical'
    elif relevance_score >= 0.6:
        return 'high'
    elif relevance_score >= 0.4:
        return 'medium'
    else:
        return 'low'


def update_relevance_scores_in_db():
    """Update relevance scores for all papers in database"""
    print("=" * 70)
    print(f"📊 RELEVANCE SCORING - Cortex Leman")
    print("=" * 70)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Fetch all papers
    cursor.execute("""
        SELECT id, arxiv_id, title, abstract, category
        FROM arxiv_papers
        ORDER BY published_date DESC
    """)
    
    papers = cursor.fetchall()
    
    if not papers:
        print("❌ No papers found in database")
        return
    
    print(f"\n📚 Analyzing {len(papers)} papers...\n")
    
    updated = 0
    importance_distribution = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    
    for paper_id, arxiv_id, title, abstract, category in papers:
        paper_data = {
            'title': title,
            'summary': abstract,
            'category': category
        }
        
        # Calculate relevance score
        relevance_score = calculate_relevance_score(paper_data)
        
        # Classify importance
        importance = classify_paper_importance(relevance_score)
        
        # Update database
        is_important = 1 if importance in ['critical', 'high'] else 0
        
        cursor.execute("""
            UPDATE arxiv_papers 
            SET relevance_score = ?, is_important = ?
            WHERE id = ?
        """, (relevance_score, is_important, paper_id))
        
        updated += 1
        importance_distribution[importance] += 1
        
        # Show progress for important papers
        if is_important:
            print(f"⭐ [{importance.upper()}] {arxiv_id}")
            print(f"   Title: {title[:60]}...")
            print(f"   Relevance: {relevance_score:.2f}")
    
    conn.commit()
    conn.close()
    
    # Display summary
    print("\n" + "=" * 70)
    print("📊 SCORING SUMMARY")
    print("=" * 70)
    print(f"Papers analyzed: {len(papers)}")
    print(f"Papers updated: {updated}")
    print(f"\nImportance Distribution:")
    print(f"  Critical (≥0.8):  {importance_distribution['critical']}")
    print(f"  High (≥0.6):      {importance_distribution['high']}")
    print(f"  Medium (≥0.4):    {importance_distribution['medium']}")
    print(f"  Low (<0.4):       {importance_distribution['low']}")
    print(f"  Important total:  {importance_distribution['critical'] + importance_distribution['high']}")
    print("=" * 70)
    
    return {
        'analyzed': len(papers),
        'updated': updated,
        'distribution': importance_distribution
    }


def get_top_papers_by_relevance(limit: int = 10) -> List[Dict]:
    """
    Get top papers by relevance score
    
    Args:
        limit: Maximum number of papers to return
    
    Returns:
        List of paper dictionaries
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT arxiv_id, title, authors, published_date, 
               relevance_score, domain, citation_count
        FROM arxiv_papers
        WHERE relevance_score > 0
        ORDER BY relevance_score DESC, citation_count DESC
        LIMIT ?
    """, (limit,))
    
    papers = []
    for row in cursor.fetchall():
        papers.append({
            'arxiv_id': row[0],
            'title': row[1],
            'authors': row[2],
            'published_date': row[3],
            'relevance_score': row[4],
            'domain': row[5],
            'citation_count': row[6]
        })
    
    conn.close()
    return papers


def display_top_papers(papers: List[Dict]):
    """Display top papers by relevance"""
    print("\n" + "=" * 70)
    print("⭐ TOP PAPERS BY RELEVANCE")
    print("=" * 70)
    
    for i, paper in enumerate(papers, 1):
        print(f"\n{i}. [{paper['domain'].upper()}] {paper['arxiv_id']}")
        print(f"   Relevance: {paper['relevance_score']:.2f} | Citations: {paper['citation_count']}")
        print(f"   Title: {paper['title'][:70]}...")
        print(f"   Published: {paper['published_date']}")
        if paper['authors']:
            print(f"   Authors: {paper['authors'][:50]}...")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Score papers by relevance to Cortex Leman")
    parser.add_argument("--update", action="store_true", help="Update all relevance scores in database")
    parser.add_argument("--top", type=int, default=10, help="Show top N papers by relevance")
    
    args = parser.parse_args()
    
    if args.update:
        update_relevance_scores_in_db()
    
    # Always show top papers
    top_papers = get_top_papers_by_relevance(limit=args.top)
    display_top_papers(top_papers)
