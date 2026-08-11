#!/usr/bin/env python3
"""
Alerting and Reporting for Cortex Leman ArXiv Research
Generates alerts for important papers and daily/weekly reports
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Database path (Hermes profile aware)
DB_PATH = Path.home() / ".hermes" / "data" / "cortex_leman_research.db"

# Alert thresholds
ALERT_THRESHOLDS = {
    "high_impact": 50,          # >50 citations
    "high_relevance": 0.8,      # >80% relevance
    "critical_relevance": 0.9,  # >90% relevance
    "recent_days": 7,           # <7 days since publication
    "urgent": 100               # >100 citations = urgent
}

# Recipients for different alert types
ALERT_RECIPIENTS = {
    "legal_update": ["Le Gardien des Normes", "L'Architecte Lémanique"],
    "technical_update": ["L'Ingénieur de Flux", "L'Oeil de Cortex"],
    "high_impact": ["L'Architecte Lémanique", "Le Gardien des Normes", "L'Ingénieur de Flux"],
    "critical": ["Tous les agents Cortex Leman"]
}


def get_papers_needing_alert() -> List[Dict]:
    """
    Retrieve papers that need to generate alerts
    
    Returns:
        List of paper dictionaries
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Calculate date threshold
    recent_date = (datetime.now() - timedelta(days=ALERT_THRESHOLDS["recent_days"])).strftime("%Y-%m-%d")
    
    # Fetch papers meeting alert criteria
    cursor.execute("""
        SELECT id, arxiv_id, title, authors, published_date, 
               citation_count, influential_citation_count, 
               relevance_score, domain, abstract, pdf_url, scanned_date
        FROM arxiv_papers
        WHERE (
            relevance_score >= ? OR
            citation_count >= ? OR
            published_date >= ?
        )
        AND is_important = 1
        ORDER BY published_date DESC, relevance_score DESC
    """, (
        ALERT_THRESHOLDS["high_relevance"],
        ALERT_THRESHOLDS["high_impact"],
        recent_date
    ))
    
    papers = []
    for row in cursor.fetchall():
        papers.append({
            'id': row[0],
            'arxiv_id': row[1],
            'title': row[2],
            'authors': row[3],
            'published_date': row[4],
            'citation_count': row[5],
            'influential_citation_count': row[6],
            'relevance_score': row[7],
            'domain': row[8],
            'abstract': row[9],
            'pdf_url': row[10],
            'scanned_date': row[11]
        })
    
    conn.close()
    return papers


def calculate_alerts(paper: Dict) -> List[str]:
    """
    Calculate which alert types apply to a paper
    
    Args:
        paper: Paper dictionary
    
    Returns:
        List of alert types
    """
    alerts = []
    
    # Check urgency
    if paper['citation_count'] >= ALERT_THRESHOLDS['urgent']:
        alerts.append('URGENT')
    
    # Check critical relevance
    if paper['relevance_score'] >= ALERT_THRESHOLDS['critical_relevance']:
        alerts.append('CRITICAL')
    
    # Check high relevance
    if paper['relevance_score'] >= ALERT_THRESHOLDS['high_relevance']:
        alerts.append('HIGH_RELEVANCE')
    
    # Check high impact
    if paper['citation_count'] >= ALERT_THRESHOLDS['high_impact']:
        alerts.append('HIGH_IMPACT')
    
    # Check if recent
    published_date = datetime.strptime(paper['published_date'], "%Y-%m-%d")
    days_ago = (datetime.now() - published_date).days
    
    if days_ago <= ALERT_THRESHOLDS['recent_days']:
        alerts.append('RECENT')
    
    return alerts


def determine_alert_type(paper: Dict, alerts: List[str]) -> str:
    """
    Determine the main alert type for routing
    
    Args:
        paper: Paper dictionary
        alerts: List of alert tags
    
    Returns:
        Main alert type
    """
    # Priority: critical > legal_update > high_impact > technical_update
    if 'CRITICAL' in alerts:
        return 'critical'
    elif 'URGENT' in alerts:
        return 'critical'
    elif paper['domain'] in ['gdpr', 'ai_act', 'fr_ch_compliance']:
        return 'legal_update'
    elif 'HIGH_IMPACT' in alerts:
        return 'high_impact'
    elif paper['domain'] in ['vision', 'ocr', 'security']:
        return 'technical_update'
    else:
        return 'general'


def generate_alert_message(paper: Dict, alerts: List[str], alert_type: str) -> str:
    """
    Generate alert message for a paper
    
    Args:
        paper: Paper dictionary
        alerts: List of alert tags
        alert_type: Main alert type
    
    Returns:
        Formatted alert message
    """
    alert_badge = " ".join([f"[{alert}]" for alert in alerts])
    
    message = f"""
🚨 CORTEX LEMAN - RESEARCH ALERT
{'=' * 70}

Alert Type: {alert_type.upper()}
{alert_badge}

📄 PAPER DETAILS
ArXiv ID: {paper['arxiv_id']}
Title: {paper['title']}
Authors: {paper['authors'] if paper['authors'] else 'N/A'}
Published: {paper['published_date']}
Domain: {paper['domain'].upper()}
Relevance: {paper['relevance_score']:.2f}
Citations: {paper['citation_count']} (influential: {paper['influential_citation_count']})

📝 ABSTRACT
{paper['abstract'][:300]}...

🔗 LINKS
ArXiv: https://arxiv.org/abs/{paper['arxiv_id']}
PDF: {paper['pdf_url']}

📋 ACTION REQUIRED
"""
    
    # Add action recommendations based on domain
    if paper['domain'] == 'gdpr':
        message += "- Review GDPR compliance controls for AI systems\n"
        message += "- Check for new Article 22 interpretations\n"
    elif paper['domain'] == 'ai_act':
        message += "- Update AI Act classification framework\n"
        message += "- Review conformity assessment procedures\n"
    elif paper['domain'] in ['vision', 'ocr']:
        message += "- Evaluate integration into L'Oeil de Cortex\n"
        message += "- Test on French/Swiss documents\n"
    elif paper['domain'] == 'fr_ch_compliance':
        message += "- Review cross-border compliance guidelines\n"
        message += "- Update FR-CH compliance checklist\n"
    
    # Add recipients
    recipients = ALERT_RECIPIENTS.get(alert_type, ['L\'Architecte Lémanique'])
    message += f"\n📧 SENT TO: {', '.join(recipients)}\n"
    message += f"📅 Alert generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    message += "=" * 70 + "\n"
    
    return message


def generate_daily_report() -> str:
    """
    Generate daily research report
    
    Returns:
        Formatted daily report
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Calculate statistics
    cursor.execute("SELECT COUNT(*) FROM arxiv_papers")
    total_papers = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM arxiv_papers WHERE is_important = 1")
    important_papers = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(relevance_score) FROM arxiv_papers")
    avg_relevance = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT AVG(citation_count) FROM arxiv_papers WHERE citation_count > 0")
    avg_citations = cursor.fetchone()[0] or 0
    
    cursor.execute("""
        SELECT COUNT(*) FROM arxiv_papers 
        WHERE published_date >= date('now', '-7 days')
    """)
    recent_papers = cursor.fetchone()[0]
    
    # Get top papers
    cursor.execute("""
        SELECT arxiv_id, title, domain, relevance_score, citation_count, published_date
        FROM arxiv_papers
        WHERE is_important = 1
        ORDER BY relevance_score DESC, citation_count DESC
        LIMIT 5
    """)
    
    top_papers = cursor.fetchall()
    
    conn.close()
    
    # Build report
    report = f"""
📊 CORTEX LEMAN - DAILY RESEARCH REPORT
{'=' * 70}
📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📈 STATISTIQUES
─────────────────────────────────
Total papers in database: {total_papers}
Important papers (relevance > 0.8): {important_papers}
New papers (<7 days): {recent_papers}
Average relevance score: {avg_relevance:.2f}
Average citation count: {avg_citations:.1f}

⭐ TOP PAPERS (BY RELEVANCE)
─────────────────────────────────
"""
    
    for i, (arxiv_id, title, domain, relevance, citations, published) in enumerate(top_papers, 1):
        report += f"\n{i}. [{domain.upper()}] {arxiv_id}\n"
        report += f"   Title: {title[:60]}...\n"
        report += f"   Relevance: {relevance:.2f} | Citations: {citations}\n"
        report += f"   Published: {published}\n"
    
    report += f"\n{'=' * 70}\nNext report: Tomorrow at 09:00 AM CET\n"
    
    return report


def generate_weekly_summary() -> str:
    """
    Generate weekly research summary
    
    Returns:
        Formatted weekly summary
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Papers this week
    cursor.execute("""
        SELECT COUNT(*) FROM arxiv_papers 
        WHERE published_date >= date('now', '-7 days')
    """)
    papers_this_week = cursor.fetchone()[0]
    
    # High impact papers this week
    cursor.execute("""
        SELECT COUNT(*) FROM arxiv_papers 
        WHERE published_date >= date('now', '-7 days')
        AND citation_count >= 50
    """)
    high_impact_this_week = cursor.fetchone()[0]
    
    # Critical papers this week
    cursor.execute("""
        SELECT COUNT(*) FROM arxiv_papers 
        WHERE published_date >= date('now', '-7 days')
        AND relevance_score >= 0.9
    """)
    critical_this_week = cursor.fetchone()[0]
    
    # Top domains
    cursor.execute("""
        SELECT domain, COUNT(*) as count
        FROM arxiv_papers
        WHERE published_date >= date('now', '-7 days')
        GROUP BY domain
        ORDER BY count DESC
    """)
    
    top_domains = cursor.fetchall()
    
    conn.close()
    
    # Build summary
    summary = f"""
📊 CORTEX LEMAN - WEEKLY RESEARCH SUMMARY
{'=' * 70}
📅 Week of: {datetime.now().strftime('%Y-%m-%d')}

📈 THIS WEEK'S ACTIVITY
─────────────────────────────────
Papers scanned: {papers_this_week}
High impact papers (>50 citations): {high_impact_this_week}
Critical papers (relevance > 0.9): {critical_this_week}

📚 DOMAINS
─────────────────────────────────
"""
    
    for domain, count in top_domains:
        summary += f"{domain.upper()}: {count} papers\n"
    
    summary += f"\n{'=' * 70}\nNext summary: Next Monday at 09:00 AM CET\n"
    
    return summary


def save_alert(paper: Dict, alerts: List[str], alert_type: str):
    """
    Save alert to database for tracking
    
    Args:
        paper: Paper dictionary
        alerts: List of alert tags
        alert_type: Main alert type
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    alert_list = ", ".join(alerts)
    recipients = ", ".join(ALERT_RECIPIENTS.get(alert_type, ['L\'Architecte Lémanique']))
    
    cursor.execute("""
        INSERT INTO paper_alerts (paper_id, alert_type, sent_to, action_taken, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        paper['id'],
        alert_list,
        recipients,
        'Pending',
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    
    conn.commit()
    conn.close()


def run_alerting():
    """
    Run alerting process for all papers
    """
    print("=" * 70)
    print(f"🚨 CORTEX LEMAN - Paper Alerting")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Get papers needing alerts
    papers = get_papers_needing_alert()
    
    if not papers:
        print("\n✅ No papers requiring alerts")
        return
    
    print(f"\n📚 Found {len(papers)} papers requiring alerts\n")
    
    alerts_generated = 0
    
    for paper in papers:
        alerts = calculate_alerts(paper)
        alert_type = determine_alert_type(paper, alerts)
        
        # Generate alert message
        message = generate_alert_message(paper, alerts, alert_type)
        
        # Print alert
        print(message)
        
        # Save to database
        save_alert(paper, alerts, alert_type)
        alerts_generated += 1
    
    # Generate daily report
    print("\n" + "=" * 70)
    print("📊 DAILY REPORT")
    print("=" * 70)
    report = generate_daily_report()
    print(report)
    
    print(f"\n✅ Alerting completed: {alerts_generated} alerts generated")
    print("=" * 70)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Alert and report on Cortex Leman research")
    parser.add_argument("--alert", action="store_true", help="Generate alerts for papers")
    parser.add_argument("--daily-report", action="store_true", help="Generate daily report")
    parser.add_argument("--weekly-report", action="store_true", help="Generate weekly summary")
    
    args = parser.parse_args()
    
    if args.alert:
        run_alerting()
    
    if args.daily_report:
        print(generate_daily_report())
    
    if args.weekly_report:
        print(generate_weekly_summary())
    
    # Default: run alerting
    if not (args.alert or args.daily_report or args.weekly_report):
        run_alerting()
