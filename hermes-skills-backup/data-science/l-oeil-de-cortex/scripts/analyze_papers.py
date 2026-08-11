#!/usr/bin/env python3
"""
Paper Impact Analysis using Semantic Scholar API
Analyzes citation counts, influential citations, and finds related works
"""

import requests
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Database path (Hermes profile aware)
DB_PATH = Path.home() / ".hermes" / "data" / "cortex_leman_research.db"


SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1"


def get_paper_impact(arxiv_id: str) -> Optional[Dict]:
    """
    Retrieve paper impact metrics from Semantic Scholar
    
    Args:
        arxiv_id: ArXiv paper ID (e.g., "2402.03300")
    
    Returns:
        Dict with citation data or None if not found
    """
    url = f"{SEMANTIC_SCHOLAR_API}/paper/arXiv:{arxiv_id}"
    params = {
        "fields": "title,citationCount,influentialCitationCount,year,abstract,authors,publicationVenue"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'citation_count': data.get('citationCount', 0),
                'influential_citation_count': data.get('influentialCitationCount', 0),
                'year': data.get('year'),
                'publication_venue': data.get('publicationVenue', {}).get('name') if data.get('publicationVenue') else None
            }
        elif response.status_code == 404:
            print(f"⚠️  Paper not found in Semantic Scholar: {arxiv_id}")
            return None
        else:
            print(f"❌ Error fetching {arxiv_id}: HTTP {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"⏱️  Timeout fetching {arxiv_id}")
        return None
    except Exception as e:
        print(f"❌ Error fetching {arxiv_id}: {e}")
        return None


def get_related_works(arxiv_id: str, limit: int = 10) -> List[Dict]:
    """
    Find related papers (references) from Semantic Scholar
    
    Args:
        arxiv_id: ArXiv paper ID
        limit: Maximum number of related works to retrieve
    
    Returns:
        List of related paper dictionaries
    """
    url = f"{SEMANTIC_SCHOLAR_API}/paper/arXiv:{arxiv_id}/references"
    params = {
        "fields": "title,citationCount,year,externalIds,authors",
        "limit": limit
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            related = data.get("data", [])
            
            related_papers = []
            for item in related:
                related_papers.append({
                    'title': item.get('title', ''),
                    'citation_count': item.get('citationCount', 0),
                    'year': item.get('year'),
                    'arxiv_id': item.get('externalIds', {}).get('ArXiv') if item.get('externalIds') else None
                })
            
            return related_papers
        else:
            print(f"❌ Error fetching references for {arxiv_id}: HTTP {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error fetching references for {arxiv_id}: {e}")
        return []


def update_papers_in_db(limit: int = 50) -> Dict:
    """
    Update citation counts for papers in database
    
    Args:
        limit: Maximum number of papers to update (most recent important papers)
    
    Returns:
        Dict with update statistics
    """
    print("=" * 70)
    print(f"📊 SEMANTIC SCHOLAR - Paper Impact Analysis")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Fetch important papers (relevance > 0.8) with missing citation data
    cursor.execute("""
        SELECT id, arxiv_id, title, citation_count 
        FROM arxiv_papers 
        WHERE is_important = 1 
        AND (citation_count = 0 OR citation_count IS NULL)
        ORDER BY published_date DESC
        LIMIT ?
    """, (limit,))
    
    papers_to_update = cursor.fetchall()
    
    if not papers_to_update:
        print("\n✅ No papers need updating (all have citation data)")
        return {'updated': 0, 'failed': 0}
    
    print(f"\n📚 Found {len(papers_to_update)} papers to analyze\n")
    
    updated = 0
    failed = 0
    
    for paper_id, arxiv_id, title, current_citations in papers_to_update:
        print(f"🔍 Analyzing: {arxiv_id} - {title[:60]}...")
        
        # Fetch impact data
        impact = get_paper_impact(arxiv_id)
        
        if impact:
            # Update database
            cursor.execute("""
                UPDATE arxiv_papers 
                SET citation_count = ?, influential_citation_count = ?
                WHERE id = ?
            """, (impact['citation_count'], impact['influential_citation_count'], paper_id))
            
            updated += 1
            print(f"   ✅ Updated: {impact['citation_count']} citations, "
                  f"{impact['influential_citation_count']} influential")
            
            # Fetch related works for high-impact papers
            if impact['citation_count'] > 50:
                print(f"   🔗 Fetching related works...")
                related = get_related_works(arxiv_id, limit=5)
                
                if related:
                    print(f"      Found {len(related)} related works:")
                    for i, ref in enumerate(related, 1):
                        print(f"        {i}. {ref['title'][:50]}... "
                              f"({ref['citation_count']} citations)")
        else:
            failed += 1
            print(f"   ❌ Could not fetch impact data")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 70)
    print("📊 UPDATE SUMMARY")
    print("=" * 70)
    print(f"Papers analyzed: {len(papers_to_update)}")
    print(f"Successfully updated: {updated}")
    print(f"Failed to fetch: {failed}")
    print("=" * 70)
    
    return {
        'analyzed': len(papers_to_update),
        'updated': updated,
        'failed': failed
    }


def generate_impact_report(days: int = 7) -> Dict:
    """
    Generate impact report for recent papers
    
    Args:
        days: Number of days to look back
    
    Returns:
        Dict with report data
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Fetch papers from last X days with citation data
    cursor.execute("""
        SELECT arxiv_id, title, authors, published_date, 
               citation_count, influential_citation_count, 
               relevance_score, domain
        FROM arxiv_papers
        WHERE published_date >= date('now', '-' || ? || ' days')
        AND citation_count > 0
        ORDER BY citation_count DESC
    """, (days,))
    
    papers = cursor.fetchall()
    
    report = {
        'period_days': days,
        'total_papers': len(papers),
        'high_impact': [],
        'high_relevance': []
    }
    
    for arxiv_id, title, authors, published_date, citations, influential, relevance, domain in papers:
        paper_data = {
            'arxiv_id': arxiv_id,
            'title': title,
            'authors': authors,
            'published_date': published_date,
            'citation_count': citations,
            'influential_citation_count': influential,
            'relevance_score': relevance,
            'domain': domain
        }
        
        # High impact: >50 citations
        if citations > 50:
            report['high_impact'].append(paper_data)
        
        # High relevance: >0.8
        if relevance > 0.8:
            report['high_relevance'].append(paper_data)
    
    conn.close()
    
    return report


def display_impact_report(report: Dict):
    """Display formatted impact report"""
    print("\n" + "=" * 70)
    print(f"📊 IMPACT REPORT (Last {report['period_days']} days)")
    print("=" * 70)
    print(f"Total papers with citation data: {report['total_papers']}")
    print(f"High impact (>50 citations): {len(report['high_impact'])}")
    print(f"High relevance (>0.8): {len(report['high_relevance'])}")
    
    # Show high impact papers
    if report['high_impact']:
        print("\n🚨 HIGH IMPACT PAPERS")
        print("-" * 70)
        for i, paper in enumerate(report['high_impact'], 1):
            print(f"\n{i}. [{paper['domain'].upper()}] {paper['arxiv_id']}")
            print(f"   Title: {paper['title'][:70]}...")
            print(f"   Citations: {paper['citation_count']} (influential: {paper['influential_citation_count']})")
            print(f"   Published: {paper['published_date']}")
    
    # Show high relevance papers
    if report['high_relevance']:
        print("\n⭐ HIGH RELEVANCE PAPERS")
        print("-" * 70)
        for i, paper in enumerate(report['high_relevance'], 1):
            print(f"\n{i}. [{paper['domain'].upper()}] {paper['arxiv_id']}")
            print(f"   Title: {paper['title'][:70]}...")
            print(f"   Citations: {paper['citation_count']} | Relevance: {paper['relevance_score']:.2f}")
            print(f"   Published: {paper['published_date']}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze paper impact using Semantic Scholar")
    parser.add_argument("--update", action="store_true", help="Update citation counts in database")
    parser.add_argument("--limit", type=int, default=50, help="Max papers to update")
    parser.add_argument("--report", type=int, default=7, help="Generate report for last N days")
    
    args = parser.parse_args()
    
    if args.update:
        update_papers_in_db(limit=args.limit)
    
    # Always generate report
    report = generate_impact_report(days=args.report)
    display_impact_report(report)
