# NVIDIA Embedding API Failover Guide

Condensed from a real outage (2026-07-04): `baai/bge-m3` went down for 48h+ with HTTP 500. This document captures the provider landscape, dimension compatibility, and decision tree.

## NVIDIA Embedding Models (verified 2026-07-04)

| Model | Dimensions | Status During Outage | Requires `input_type` |
|-------|-----------|---------------------|----------------------|
| `baai/bge-m3` | 1024 | ❌ HTTP 500 (down) | No |
| `nvidia/nv-embedqa-e5-v5` | **1024** | ✅ Working | Yes (`query` / `passage`) |
| `nvidia/nv-embed-v1` | 4096 | ✅ Working | No |
| `nvidia/llama-nemotron-embed-1b-v2` | 2048 | ✅ Working | Yes |
| `nvidia/nv-embedqa-mistral-7b-v2` | ? | ❌ Error | Yes |

## Key Insight: Dimension Match ≠ Vector Space Match

`baai/bge-m3` and `nvidia/nv-embedqa-e5-v5` both produce 1024-dimensional vectors. **But they use different embedding spaces.** You cannot mix vectors from the two models in the same ChromaDB collection.

**Switching models requires a full reindex** of all chunks, even if dimensions match.

## Failover Decision Tree

```
bge-m3 is DOWN (HTTP 500/429/503)
│
├─ Expected downtime < 48h?
│  └─ YES → Wait. Set up watchdog cron (see service-watchdog-cron skill).
│            Existing index stays intact. No data loss.
│
├─ Downtime > 48h or recurring?
│  └─ Switch to nv-embedqa-e5-v5 (1024-d, closest match):
│     1. Update config.yaml: model = "nvidia/nv-embedqa-e5-v5"
│     2. Add input_type to embed calls: "query" for search, "passage" for indexing
│     3. Delete ChromaDB collection (or rename for backup)
│     4. Full reindex: all chunks re-embedded with new model
│     5. Rebuild BM25 index (unchanged — lexical, not affected)
│     6. Re-run evaluation baseline
│
└─ Need to verify a model works before committing?
   └─ Test with curl first:
      curl -s "https://integrate.api.nvidia.com/v1/embeddings" \
        -H "Authorization: Bearer $KEY" \
        -H "Content-Type: application/json" \
        -d '{"input": ["test"], "model": "nvidia/nv-embedqa-e5-v5", "input_type": "query"}'
      # Check: HTTP 200 + data[0].embedding length = 1024
```

## Testing NVIDIA API Health

```bash
# Quick health check for any NVIDIA embedding model
KEY=$(grep NVIDIA_API_KEY ~/.hermes/.env | head -1 | cut -d= -f2)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  "https://integrate.api.nvidia.com/v1/embeddings" \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": ["test"], "model": "baai/bge-m3"}')

# 200 = healthy, 500 = model error, 429 = rate limited, 401 = key issue
```

## Listing All Available NVIDIA Models

```bash
curl -s "https://integrate.api.nvidia.com/v1/models" \
  -H "Authorization: Bearer $KEY" | \
  python3 -c "
import sys, json
d = json.load(sys.stdin)
models = [m['id'] for m in d.get('data', [])]
embed = [m for m in models if 'embed' in m.lower() or 'bge' in m.lower()]
print(f'Total: {len(models)}, Embedding: {len(embed)}')
for m in embed: print(f'  {m}')
"
```

## RAG Impact Assessment

When the embedding provider is down:

| Component | Impact |
|-----------|--------|
| **Search/query** | ❌ Broken — can't embed the query |
| **Indexing new files** | ❌ Broken — can't embed new chunks |
| **Existing index** | ✅ Intact — ChromaDB data persists |
| **BM25 (lexical search)** | ✅ Unaffected — doesn't use embeddings |
| **Manifest/delta tracking** | ✅ Unaffected — file hashes, not vectors |

## Alternative Providers (non-NVIDIA)

If NVIDIA is chronically unreliable:

| Provider | Model | Dimensions | Free Tier | Notes |
|----------|-------|-----------|-----------|-------|
| Jina AI | `jina-embeddings-v3` | 1024 | Yes (1M tokens) | Multilingual, good FR support |
| OpenAI | `text-embedding-3-small` | 1536 | No | Reliable but different dim → full reindex |
| Local | `sentence-transformers/paraphrase-multilingual` | 384 | Free | Offline, CPU-friendly, small dim |
| Cohere | `embed-multilingual-v3` | 1024 | Trial | Good multilingual |
