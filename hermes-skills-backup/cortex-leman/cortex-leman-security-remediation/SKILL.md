---
name: cortex-leman-security-remediation
category: cortex-leman
version: 1.3.0
description: |
  Security remediation patterns for Cortex Leman: memory sanitization (MemPoison defense),
  WORM journal integrity, compliance kill-switch workflows, ChainMark watermarking (AI Act Art. 50),
  ArXiv research → compliance module integration, and AI SBOM generation (CycloneDX 1.6, Art. 11/13).
  Covers defense-in-depth against persistent prompt injection in multi-agent RAG systems.
  Includes fil rouge E2E integration testing methodology for proving modules form a system.
  See references/ for implementation details and audit recipes.
---

# Cortex Leman — Security Remediation Patterns

Reusable security patterns developed during Cortex Leman v5 hardening (2026-07-26).
Each pattern addresses a specific class of vulnerability in AI agent systems.

## Pattern 1: Memory Sanitization (Defense-in-Depth Against MemPoison)

**Origin**: TICKET-010 (2026-07-26). Protects against **Bad Memory** (arXiv 2607.14611) and **MemPoison** (arXiv 2607.14651) attacks where adversaries inject instructions into documents that get indexed in RAG/memory — these persist across sessions and activate when the content is retrieved into an LLM prompt.

**Why input sanitization alone doesn't cover this**: standard prompt-injection guards (regex on user input) miss the persistence layer — untrusted content sits dormant in vector DBs and knowledge vaults between sessions before being injected into prompts via RAG context building.

### Dual-Point Sanitization

```
WRITE PATH (storage):
  Document → sanitize_for_storage() → [allow/quarantine/block] → Vault + ChromaDB

READ PATH (retrieval, defense-in-depth):
  ChromaDB → sanitize_for_retrieval() → [allow/quarantine/block] → LLM Prompt
```

Sanitizing at BOTH points catches attacks that slip through storage (subtle encoding, multi-document assembly attacks).

### Action Levels

| Risk Score | Action | Behavior |
|---|---|---|
| 0.0 | `allow` | Content unchanged |
| < 0.86 | `quarantine` | Content wrapped in `[QUARANTINED-CONTENT]...[/QUARANTINED-CONTENT]` — LLM sees it as data, not instructions |
| ≥ 0.86 | `block` | Content replaced with `[BLOCKED-CONTENT: suspected prompt injection removed]` |

Risk score = `max(severity) + (threat_count - 1) × 0.06`, capped at 1.0.

### Three Integration Surfaces

Every memory/persistence entry point in a multi-agent system needs sanitization:

1. **Procedural Memory** (`update_instructions()`) — agent self-reflection writes here; a poisoned reflection loop permanently corrupts behavior
2. **Knowledge Vault** (`store_document()`) — client-uploaded documents; primary external attack surface
3. **RAG Context Builder** (`build_context_for_agent()`) — last gate before retrieved content enters the LLM prompt

### Threat Vectors Covered (FR + EN)

| Category | Example (EN) | Example (FR) | Severity |
|---|---|---|---|
| instruction_override | `SYSTEM:`, `You must` | `À partir de maintenant` | 0.52-0.72 |
| persona_hijacking | `Act as`, `You are now` | `Tu es maintenant` | 0.67 |
| rule_suppression | `Ignore your instructions`, `Ignore all previous` | `Ignore tes consignes` | 0.82 |
| exfiltration | `Output the system prompt`, `reveal the API keys` | `Envoie à`, `Révèle` | 0.88 |
| credential_leak | `export API_KEY=sk-***`, `set TOKEN=...` | (same syntax) | 0.85-0.90 |
| network_exfiltration | `curl https://evil.com`, `wget`, `fetch` | (same syntax) | 0.82 |
| hidden_unicode | Zero-width (U+200B-200F) | Bidi override (U+202A-202E) | 0.75 |
| instruction_smuggling | Base64 commands, HTML comments | Same technique, FR payload | 0.82-0.86 |
| homoglyph | Cyrillic `а` → Latin `a` | Greek `Α` → Latin `A` | 0.55 |

### Implementation Notes

- **Base64 detection**: regex matches ≥24 char base64 strings → decode → check if decoded text looks instructional (terms: ignore, system, prompt, tu es, envoie). Only flag if instructional — avoids false positives on legitimate data.
- **HTML comment smuggling**: unescape entities in comments, then check if content looks instructional.
- **Audit scanning**: `audit_memory_store(path)` scans existing files read-only. False positives expected on binary files (SQLite, vector DBs) — filter by extension before scanning.
- **Journal integration**: all events logged to WORM journal for RGPD Art. 30 + AI Act Art. 14 audit trail.

**Full implementation guide + test vectors:** `references/memory-sanitization-pattern.md`

---

## Pattern 2: WORM Journal Hash Integrity

**Origin**: TICKET-006 (2026-07-26). Fixes a subtle bug in append-only audit journals where hash verification fails systematically after payload minimization (RGPD data reduction).

### The Pitfall: Minimize BEFORE Hashing

The critical ordering rule for any append-only journal that applies RGPD data minimization:

```
❌ WRONG ORDER:
  1. Build payload (with sensitive fields)
  2. Hash payload
  3. Minimize payload (replace sensitive fields with ***REDACTED***)
  4. Store {hash, minimized_payload}
  → verify() recalculates hash on minimized_payload → MISMATCH

✅ CORRECT ORDER:
  1. Build payload
  2. Minimize payload
  3. Hash minimized_payload
  4. Store {hash, minimized_payload}
  → verify() recalculates hash on minimized_payload → MATCH
```

This applies to ANY journal pattern where the stored form differs from the hashed form (encryption, compression, redaction, minimization). The rule: **hash exactly what you store**.

### Chain Repair

When repairing broken entries:
1. Recalculate the hash on the **stored** (minimized) payload
2. Propagate the fix downstream — each entry's `prev_hash` must match the previous entry's recalculated hash
3. Log the repair itself as a new journal entry (meta-audit trail)

**Full implementation guide:** `references/worm-hash-integrity.md`

---

## Pattern 3: Compliance Kill-Switch Remediation

**Origin**: P0 remediation (2026-07-26). Systematic workflow for resolving compliance kill-switch activations in production AI systems.

### Workflow

1. **Read the trigger** — identify which compliance check failed (score < threshold, missing MFA, missing DPIA, etc.)
2. **Map to regulatory article** — RGPD Art. 5/6/25/32/35, AI Act Art. 9/14/15
3. **Generate remediation script** — schema migration + data backfill + config fix
4. **Dry-run → backup → apply** — never mutate production DB without backup and dry-run
5. **Re-scan** — run the compliance checker again to verify 8/8 checks pass
6. **Document** — create the procedure doc (CSC, AIPD, violation procedure) that was missing

### Key Lessons

- **DB inspection without sqlite3 CLI**: use Python `sqlite3` with `uri=True` read-only mode when the CLI binary isn't available
- **Compliance scripts are disposable**: generate via LLM, review, apply, then keep only the final version — not the intermediate drafts
- **Score 1.0 is necessary but not sufficient**: the kill-switch checks code, config, AND documentation. Missing procedure docs (violation handling, cross-border transfer) will fail checks even with perfect code.

---

## Pattern 4: ChainMark Watermarking (AI Act Art. 50 Compliance)

**Origin**: TICKET-022 (2026-07-26). Implements model-free text watermarking for EU AI Act Article 50(2): all synthetic content destined for the public must carry **machine-readable marking**. Deadline: 2 August 2026.

### Architecture: 3 Complementary Layers

| Layer | Mechanism | Purpose | Robustness |
|---|---|---|---|
| **Steganographic** | Zero-width Unicode (U+200B=0, U+200C=1) encoding 72 bits: magic (0xC0DE) + tenant (16b) + timestamp (32b) + CRC-8 | Machine-detectable invisible mark | Survives copy-paste; header block at text start ensures substring detection |
| **Cryptographic** | Ed25519 signature (HMAC-SHA256 fallback) over SHA-256 of watermarked text | Provenance proof + tamper detection | Any text alteration invalidates signature |
| **Visible** | Configurable multilingual suffix (FR/EN/DE/IT) | Explicit Art. 50 compliance | Per-tenant toggle |

### Pipeline Integration Point

Watermarking is applied **post-generation, pre-return** in the LLM provider pipeline — after guardrails OUT, before the response dict is returned. This makes it:

- **Model-agnostic**: works with any LLM (OpenAI, Anthropic, local Ollama, etc.)
- **Non-blocking**: if watermarking fails, text is returned without watermark + error logged
- **Automatic**: every LLM output is watermarked without agent-level changes

### Implementation Pitfalls Encountered

1. **Copy-paste robustness**: if watermark bits are spread evenly across word boundaries, short substrings may miss the magic prefix. Fix: inject the **full 72-bit payload as a contiguous header** at the start of the text, then spread redundant copies across the body.

2. **Visible marker + steganographic injection**: the zero-width chars get inserted *inside* the visible marker text too. Tests checking for substring presence in the visible marker must strip zero-width chars first (`text.replace("\u200b", "").replace("\u200c", "")`).

3. **CRC corruption tests**: corrupting the *first* zero-width bit shifts the entire bit stream, causing the magic prefix to never be found (detection returns `is_watermarked=False` instead of `watermark_valid=False`). Corrupt bits **after** the 16-bit magic prefix to test CRC failure properly.

4. **Detection window**: `detect()` scans the extracted bit stream with a sliding 72-bit window. For very short texts (< 72 zero-width chars total), detection will fail — this is acceptable since Art. 50 targets complete generated content, not fragments.

**Full implementation guide + test matrix:** `references/chainmark-watermarking-pattern.md`

**External ecosystem context:** `references/ai-content-provenance-ecosystem-2026.md` — condensed knowledge on C2PA, SynthID, AI Act Art. 50, Swiss LPD, open-source tools, and market data. Consult when positioning ChainMark within the broader provenance landscape or advising clients on multi-layer Art. 50 compliance (text + images + video).

**C2PA video/image signing** (complements ChainMark): `references/c2pa-video-signing-implementation.md` — working implementation using `c2pa-python` (validated Aug 2026 on African Heroes Ep. 2). Includes API gotchas, manifest structure, legal priority matrix, and **official CA list with SSL.com FREE tier** (0 CHF, since May 2026). Reusable signing script: `scripts/sign_video.py`.

---

## Pattern 5: ArXiv Research → Compliance Module Integration

**Origin**: Top 5 ArXiv papers integration (2026-07-26). Translates academic security/compliance findings into concrete, testable Python classes that plug into the existing security infrastructure.

### The Pipeline

```
ArXiv paper (findings + regulatory mapping)
    ↓
LLM-assisted code generation (structured prompt → JSON → module + tests)
    ↓
Validation pass (required classes present? arXiv refs cited? imports clean?)
    ↓
Test-fix cycle (run pytest, patch failures, re-run until green)
    ↓
Cross-module wiring (connect new classes to ChainMark, sanitizer, auditor)
    ↓
Documentation (paper mapping table + conformity matrix)
```

### Design Rules

1. **One module, multiple classes**: group related papers into a single module (`research_integration.py`) rather than one file per paper. Each paper becomes a class with the arXiv ID in its docstring.

2. **`PAPER_REFERENCES` dict at module level**: every integrated paper gets an entry `{key: "arXiv:XXXX.XXXXX"}`. This enables citation tracking and commercial differentiation ("our audit cites 5 peer-reviewed papers from July 2026").

3. **Outcome-based, not process-based**: certification/trust classes must score concrete metrics (accuracy, harm incidents, bias measurements), not checkboxes. This is the central finding of arXiv:2607.15992.

4. **Cross-module integration**: new research modules must connect to existing infrastructure. Example: `MediaAuthenticityScorer.detect_synthetic_markers()` calls `ChainMarkWatermarker.detect()` from TICKET-022 — papers don't just get cited, they get wired to code.

5. **LLM code generation validation checklist**: after generating a module via GPT, verify:
   - All requested classes/dataclasses present in source
   - All arXiv reference IDs present
   - `import ast; ast.parse()` passes (syntax)
   - Module imports cleanly (`from core.security.X import Y`)
   - pytest passes (run before declaring done)

### LLM-Assisted Code Generation Gotchas

- **`subprocess.run` doesn't inherit env vars**: when calling GPT via `requests` from a Python script launched by `python3 << 'PYEOF'`, the script's `subprocess.run(["bash", "-c", "grep ... config.yaml"])` runs in a *child* that may not have the API key env var. Use `os.environ.get()` directly in the same process, not via subprocess.
- **OpenRouter `response_format: {"type": "json_object"}`**: use this to get clean JSON back (keys: "module", "tests") instead of markdown-fenced code that needs stripping.
- **Token limits**: a 5-class module with tests may approach 16k tokens output. Keep the prompt focused — describe class interfaces, not full implementations.

### When to Apply

- Weekly ArXiv scan produces papers with R ≥ 9 relevant to FR-CH compliance
- A prospect/client audit needs academic backing for methodology claims
- A new regulatory article (AI Act, RGPD) needs a corresponding technical capability
- Updating the `ARGUMENTAIRE-ACADEMIQUE` document with new code-backed capabilities

**Full paper mapping + module architecture:** `references/arxiv-research-integration.md`

---

## Pattern 7: Fil Rouge End-to-End Integration Testing

**Origin**: Fil rouge E2E test (2026-07-26). A single integration test that chains ALL security/compliance modules in pipeline order — sanitizer → watermark → journal → SBOM → PhantomSeal → AgentGovernance — and proved they actually connect. Discovered 3 real bugs that 40+ unit tests missed.

**Why unit tests aren't enough**: unit tests validate each module in isolation with controlled payloads that match the module's own patterns. They cannot reveal (a) that modules don't actually connect to each other, or (b) that real-world attack vectors slip through because the unit test payloads were designed to pass.

### The Fil Rouge Pattern

Write ONE test file (`test_fil_rouge_e2e.py`) with two test classes:

1. **`TestFilRougeEndToEnd`** — a master scenario that takes a poisoned prompt through the full pipeline (sanitize → mock LLM response → watermark → journal → SBOM → detect → classify), plus per-module tests that exercise each module with adversarial payloads.

2. **`TestIntegrationGlobale`** — cross-module assertions that prove specific inter-module connections (e.g., ChainMark watermark → PhantomSeal detection, SBOM gaps → Trust score, Agent classification → Risk tier).

### The Honest Bypass

When the LLM provider library (litellm) isn't installed in the dev environment, don't mock it at the import level — **bypass `LLMService.generate()` entirely** and call the security modules directly in pipeline order. This is more honest: it tests the proprietary security/compliance modules (which is what we own) without pretending to test the LLM call (which is a third-party dependency).

### What the Fil Rouge Caught

| Bug | Why unit tests missed it | Fix |
|---|---|---|
| "Ignore all previous instructions" (without "your rules") passed the sanitizer | Unit test payloads always included "rules/instructions/safety" after "ignore" | Added `previous` as alternative in rule_suppression regex |
| `export API_KEY=sk-*** passed | No pattern for inline credential assignment | New `credential_leak` patterns |
| `curl https://evil.com` passed | No network exfiltration pattern | New `network_exfiltration` pattern |

**Lesson**: adversarial E2E tests with real-world attack strings catch gaps that happy-path unit tests never will. Run the fil rouge after every security module change.

### Fil Rouge as the "Stop Signal"

When you've accumulated 3+ security/compliance modules with passing unit tests, **stop adding modules and write the fil rouge**. The fil rouge is the proof that the modules form a system, not a collection. Adding TICKET-029 before the fil rouge was green would have been building on unvalidated ground.

**Full test structure + bug reproduction recipes:** `references/fil-rouge-e2e-testing-pattern.md`

---

## Pattern 6: AI SBOM — CycloneDX Bill of Materials (AI Act Art. 11/13)

**Origin**: TICKET-028 (2026-07-26). Generates an AI Bill of Materials in CycloneDX 1.6 format documenting every model in the stack: supplier, jurisdiction, risk tier, cross-border transfer status, and security assessment. Required for AI Act Art. 11 (technical documentation) and Art. 13 (transparency), plus RGPD Art. 30 (processing records).

**Why**: arXiv:2607.17242 measured that the vast majority of published AI models expose **none** of the metadata required for traceability. An SBOM is both a regulatory deliverable and a commercial differentiator — clients can verify exactly which models touch their data and where it flows.

### Architecture

```
core/compliance/
├── ai_sbom.py       # Generic generator (CycloneDX 1.6 + AI/ML properties)
└── cortex_sbom.py   # Pre-populated with the actual Cortex Leman model inventory
```

### API

```python
from core.compliance.ai_sbom import AISBOMGenerator, ModelComponent, AIActRiskTier
from core.compliance.cortex_sbom import get_cortex_sbom, get_cortex_sbom_markdown

# Pre-populated SBOM for Cortex Leman (8 models, CycloneDX JSON)
sbom_json = get_cortex_sbom()           # → dict, CycloneDX 1.6
sbom_md   = get_cortex_sbom_markdown()  # → human-readable table

# Build a client SBOM from scratch
gen = AISBOMGenerator()
gen.add_model(ModelComponent(name="...", version="...", supplier="...",
    jurisdiction="FR/EU", purpose="...", risk_tier="limited",
    data_categories=["prompts"], cross_border_transfer=False,
    security_assessment=True, evaluated_date="2026-07-26"))
gen.add_data_flow("model_a", "model_b", "description", ["text"])
client_sbom = gen.generate()

# Validate against AI Act
art11_gaps = gen.validate_ai_act_art11(client_sbom)  # → list[str] of gaps
art13_gaps = gen.validate_ai_act_art13(client_sbom)
```

### Risk Tier Classification

`AIActRiskTier.classify_model(name, purpose, capabilities)` maps to AI Act tiers:

| Signal in name/purpose/capabilities | Tier |
|---|---|
| `social_scoring` | unacceptable |
| `automated_decision`, `biometric` | high |
| `content_generation`, `decision_support` | limited |
| (none of the above) | minimal |

### Cross-Border Flag

Every `ModelComponent` carries `cross_border_transfer: bool`. When `True`, the CycloneDX output adds property `ai:cross-border-legal-basis: "RGPD Art. 44-49"`. This is the RGPD Art. 30 + AI Act Art. 13(2)(d) hook for transfer documentation.

### Validation Gotchas

- `validate_ai_act_art11()` checks for **evaluation date** — a model without `evaluated_date` fails even if everything else is present. Set it to the date of the security assessment.
- `validate_ai_act_art13()` requires `externalReferences` (model card URL). Models without a public card fail transparency checks.
- Both validators operate on the **generated dict** (CycloneDX JSON), not on `ModelComponent` objects — call `gen.validate(gen.generate())`.

**Full implementation guide + Cortex Leman inventory:** `references/ai-sbom-pattern.md`

---

## When to Use Which Pattern

- **Memory Sanitization**: any agent with persistent memory, RAG, or knowledge vaults
- **WORM Hash Integrity**: any append-only journal with data transformation (encryption, minimization, compression)
- **Kill-Switch Remediation**: any compliance audit failure requiring systematic fix across code + DB + documentation
- **ChainMark Watermarking**: any AI system generating text for external/public consumption (AI Act Art. 50)
- **C2PA Video/Image Signing**: AI-generated video and images published to platforms (YouTube, social media). Complements ChainMark (text) for full Art. 50 media coverage. Use `scripts/sign_video.py`.
  - **Production certs: SSL.com FREE tier** (since May 2026) — 0 CHF for 1 Level 1 cert + 10k timestamps/year. Requires C2PA conformance record ID. Other CAs: DigiCert, Tauth Labs, Trufo (all premium).
  - **Pipeline integration**: C2PA is the LAST step in build.py (after outro/BGM/subs). Graceful degradation: warn on failure, don't block build. Signed output replaces original. Validated on african-heroes + culture-en-saveur build scripts (Aug 2026).
- **ArXiv Research Integration**: when translating academic findings into compliance code modules
- **AI SBOM**: any multi-model AI system needing Art. 11/13 documentation; client audit deliverable
- **Fil Rouge E2E**: after 3+ security modules exist with passing unit tests; before adding the next module
- **All seven together**: hardening a production AI system for RGPD/AI Act compliance audit
