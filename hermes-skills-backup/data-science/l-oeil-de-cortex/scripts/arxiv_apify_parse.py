#!/usr/bin/env python3
"""
ArXiv /new listings parser for Apify RAG Web Browser dumps.

PROVEN 2026-07-04: parsed 333 papers (cs.AI:86, cs.CR:19, cs.CV:127, cs.LG:101)
in a single pass, zero failures, correct scoring.

Usage:
    # 1. Scrape via Apify (4 parallel calls):
    #    mcp_apify_apify__rag_web_browser(query="https://arxiv.org/list/cs.AI/new", maxResults=1)
    #    ...repeat for cs.CR, cs.CV, cs.LG
    #
    # 2. Extract markdown: mcp_apify_get_dataset_items(datasetId=<id>, fields="markdown", limit=1)
    #    → large results saved to /tmp/hermes-results/call_XXXX.txt
    #
    # 3. Run this script (edit FILES dict below or pass paths as args):
    python3 arxiv_apify_parse.py

Output: JSON to /tmp/arxiv_scored.json + top-40 preview to stdout.

KEY PITFOLLS handled (see references/arxiv_apify_rag_method.md §Etape 3-4):
  - Double JSON encoding: dataset item wrapped in {"result":"...```toon markdown```..."}
    and the markdown value is ITSELF json-escaped. Needs TWO json.loads passes.
  - Escaped markdown brackets: entries are \[N\] [arXiv:ID], split regex must use \\\[.
"""
import re
import json
import sys
from pathlib import Path
from datetime import datetime

# Default: files saved by mcp_apify_get_dataset_items in /tmp/hermes-results/
# Override via CLI args: python3 arxiv_apify_parse.py /path/to/cs.AI.txt /path/to/cs.CR.txt ...
DEFAULT_FILES = {
    "cs.AI": "/tmp/hermes-results/call_add3af9ca67948348a87170d.txt",
    "cs.CR": "/tmp/hermes-results/call_cee7edcd5f924279944c692c.txt",
    "cs.CV": "/tmp/hermes-results/call_1c02438b504b48409b806bb0.txt",
    "cs.LG": "/tmp/hermes-results/call_3f790c3a934043009bd03303.txt",
}

# ── Scoring 0-20 (from SKILL.md) ──────────────────────────────────
CORE_KW = [  # +3 each — direct compliance terms
    "gdpr", "ai act", "compliance", "certification", "formal verification",
    "audit", "safety", "alignment", "unlearning", "erasure", "privacy",
    "governance",
]
STD_KW = [  # +2 each — standard relevance terms
    "security", "vulnerability", "attack", "defense", "robustness", "fairness",
    "bias", "ethics", "explainability", "transparency", "accountability",
    "data protection", "consent", "anonymization", "differential privacy",
    "federated", "risk", "trustworthy", "trust", "verif", "certif", "liveness",
    "jailbreak", "red team", "backdoor", "poisoning", "distillation",
    "intellectual property", "watermark", "attribution", "benchmark",
    "agent safety", "agent alignment", "autonomous", "responsible ai",
    "hallucination", "forensic", "misinformation", "deepfake", "document",
    "biometric", "anonym", "cryptograph", "adversarial", "guardrail",
    "robust", "interpretab", "membership inference", "model stealing",
    "data poisoning", "prompt injection", "fingerprinting", "trajectory privacy",
    "membership", "inference", "inversion", "reconstruction", "de-anonym",
]


def score_paper(text):
    t = text.lower()
    score = 0
    matched = []
    for kw in CORE_KW:
        if kw in t:
            score += 3
            matched.append(kw)
    for kw in STD_KW:
        if kw in t:
            score += 2
            matched.append(kw)
    return min(score, 20), matched


def decode_to_markdown(filepath):
    """Decode Apify RAG dump. Handles both legacy (code-fence) and current (pure JSON) formats.

    Format evolution (verified 2026-07-18):
    - Pre-2026-07-18: result wrapped in "items[1]{markdown}: ... ```" code fence (double-encoded)
    - 2026-07-18+:    result is a pure JSON string with items[0].markdown + trailing text summary.
                      Use raw_decode to stop at first JSON object boundary (avoid "Extra data" error).
    """
    raw = Path(filepath).read_text(encoding="utf-8", errors="replace")
    data = json.loads(raw)
    result = data.get("result", "")

    # Try current format first (2026-07-18+): result is pure JSON string
    try:
        decoder = json.JSONDecoder()
        inner, _ = decoder.raw_decode(result)
        if isinstance(inner, dict) and "items" in inner and inner["items"]:
            return inner["items"][0]["markdown"]
    except (json.JSONDecodeError, ValueError, KeyError, IndexError):
        pass

    # Legacy fallback: code-fence-wrapped markdown with double encoding
    marker = "items[1]{markdown}:"
    idx = result.find(marker)
    if idx < 0:
        return result
    q_start = result.find('"', idx)
    fence_idx = result.rfind("```")
    segment = result[q_start + 1:fence_idx] if fence_idx > q_start else result[q_start + 1:]
    close_q = segment.rfind('"')
    md_escaped = segment[:close_q] if close_q >= 0 else segment
    try:
        return json.loads('"' + md_escaped + '"')
    except (json.JSONDecodeError, ValueError):
        return md_escaped.replace("\\\\", "\\").replace("\\n", "\n").replace('\\"', '"')


def extract_new_submissions(markdown):
    start_m = re.search(r'###\s*New submissions', markdown)
    if not start_m:
        return ""
    start = start_m.end()
    end_m = re.search(r'###\s*(Cross|Replacements)', markdown[start:])
    end = start + end_m.start() if end_m else len(markdown)
    return markdown[start:end]


def parse_entries(section):
    papers = []
    parts = re.split(r'\\\[(\d+)\\\]\s*\[arXiv:', section)
    for i in range(1, len(parts), 2):
        if i + 1 >= len(parts):
            break
        block = parts[i + 1]
        id_m = re.match(r'(\d+\.\d+)', block)
        if not id_m:
            continue
        aid = id_m.group(1)
        title_m = re.search(r'Title:\s*(.+?)(?:\n\n|\n\\\[)', block, re.DOTALL)
        title = re.sub(r'\s+', ' ', title_m.group(1)).strip() if title_m else ""
        subj_m = re.search(r'Subjects:\s*(.+?)(?:\n|$)', block)
        subjects = subj_m.group(1).strip()[:200] if subj_m else ""
        abstract = ""
        if "Subjects:" in block:
            abstract = re.sub(r'\s+', ' ', block.split("Subjects:", 1)[-1]).strip()[:1500]
        papers.append({"arxiv_id": aid, "title": title, "subjects": subjects, "abstract": abstract})
    return papers


def main():
    files = DEFAULT_FILES
    if len(sys.argv) > 1:
        # CLI override: positional args map to cs.AI, cs.CR, cs.CV, cs.LG in order
        domains = ["cs.AI", "cs.CR", "cs.CV", "cs.LG"]
        files = {domains[i]: sys.argv[i + 1] for i in range(min(len(domains), len(sys.argv) - 1))}

    all_papers = []
    counts = {}
    for domain, fp in files.items():
        md = decode_to_markdown(fp)
        section = extract_new_submissions(md)
        entries = parse_entries(section)
        for e in entries:
            e["domain"] = domain
        counts[domain] = len(entries)
        all_papers.extend(entries)

    # Deduplicate (cross-lists may appear in multiple domains)
    seen = set()
    unique = []
    for p in all_papers:
        if p["arxiv_id"] not in seen:
            seen.add(p["arxiv_id"])
            unique.append(p)
    all_papers = unique

    for p in all_papers:
        text = p["title"] + " " + p["abstract"] + " " + p["subjects"]
        p["score"], p["matched"] = score_paper(text)

    all_papers.sort(key=lambda x: x["score"], reverse=True)

    important = [p for p in all_papers if p["score"] >= 7]
    high_rel = [p for p in all_papers if p["score"] >= 10]
    critical = [p for p in all_papers if p["score"] >= 15]

    print("=== SCAN RESULTS ===")
    print(f"TOTAL_NEW: {len(all_papers)}")
    print(f"BY_DOMAIN: {json.dumps(counts)}")
    print(f"IMPORTANT (>=7): {len(important)}")
    print(f"HIGH_RELEVANCE (>=10): {len(high_rel)}")
    print(f"CRITICAL (>=15): {len(critical)}")
    print("\n=== TOP 40 BY SCORE ===")
    for p in all_papers[:40]:
        print(f"[{p['score']:2d}] {p['domain']:5s} {p['arxiv_id']} | {','.join(p['matched'][:4]):30s} | {p['title'][:100]}")

    Path("/tmp/arxiv_scored.json").write_text(json.dumps({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "counts": counts,
        "total": len(all_papers),
        "important": len(important),
        "high_relevance": len(high_rel),
        "critical": len(critical),
        "papers": all_papers,
    }, ensure_ascii=False, indent=2))
    print(f"\nSaved {len(all_papers)} papers to /tmp/arxiv_scored.json")


if __name__ == "__main__":
    main()
