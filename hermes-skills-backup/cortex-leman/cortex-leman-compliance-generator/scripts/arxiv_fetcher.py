import requests
import feedparser
from datetime import datetime, timedelta

ARXIV_FEED = "https://export.arxiv.org/api/query?search_query=cat:cs.AI+AND+submittedDate:[{start}+TO+{end}]&start=0&max_results=5"
OUTPUT_FILE = "/tmp/arxiv_latest.md"

def fetch_latest_arxiv_papers(days=7):
    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    url = ARXIV_FEED.format(start=start, end=end)
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Échec de récupération des données arXiv")

    feed = feedparser.parse(response.text)
    
    with open(OUTPUT_FILE, 'w') as f:
        f.write(f"# Derniers papiers arXiv (last {days} days)\n")
        f.write(f"## Mise à jour: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        
        for entry in feed.entries:
            title = entry.title.replace('\n', ' ').strip()
            summary = entry.summary.replace('\n', ' ').strip()
            link = entry.link
            published = entry.published

            f.write(f"### [{title}]({link})\n")
            f.write(f"**Publié:** {published}\n")
            f.write(f"**Résumé:** {summary}\n\n")

    print(f"[✅] Récupération arXiv terminée → {OUTPUT_FILE}")

if __name__ == "__main__":
    fetch_latest_arxiv_papers()