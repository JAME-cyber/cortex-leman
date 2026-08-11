# ChainMark Watermarking Pattern — Implementation Guide

**Origin**: TICKET-022, Cortex Leman v5 (2026-07-26)
**Paper**: arXiv:2607.18445 (ChainMark — model-free, closed-form calibration)
**Regulation**: EU AI Act Article 50(2) — machine-readable marking of synthetic content

## Module API

```python
from core.security.watermarker import ChainMarkWatermarker, WatermarkResult, DetectionResult

# Initialize (auto-generates Ed25519 keypair if no secret_key)
wm = ChainMarkWatermarker(tenant_id="client-abc")

# Watermark (apply all 3 layers)
result = wm.watermark(text, model="gpt-5.6", visible=True, language="fr")
# → WatermarkResult(text, metadata, visible_marker_added)

# Detect (extract + validate invisible watermark from any text)
detection = wm.detect(suspect_text)
# → DetectionResult(is_watermarked, tenant_id, timestamp, watermark_valid)

# Verify (cryptographic proof)
wm.verify_metadata(result.metadata, result.text)  # → bool
```

## Pipeline Integration (provider.py)

Insert as **Phase 6** in the LLM provider `generate()` method, after guardrails OUT:

```python
# === Phase 6: Watermarking AI Act Art. 50 ===
watermark_metadata = None
watermark_id = None
if text and not text.startswith("[Réponse filtrée"):
    try:
        from core.security.watermarker import ChainMarkWatermarker
        wm = ChainMarkWatermarker(tenant_id=client_id)
        wm_result = wm.watermark(text, model=actual_model, visible=True, language="fr")
        text = wm_result.text
        watermark_metadata = wm_result.metadata
        watermark_id = wm_result.metadata.get("watermark_id")
    except Exception as e:
        logger.error(f"Watermarking failed (non-blocking): {e}")
```

Add `"watermark_id"` and `"watermark_metadata"` to the return dict.

## Watermark Bit Layout (72 bits total)

```
| Magic (16 bits) | Tenant ID (16 bits) | Timestamp (32 bits) | CRC-8 (8 bits) |
|    0xC0DE       | sha256(tenant)[:2]  | epoch unix          | over bytes 0-7 |
```

Encoded as zero-width Unicode characters:
- `U+200B` (zero-width space) = bit 0
- `U+200C` (zero-width non-joiner) = bit 1

## Injection Strategy

```
[HEADER: 72 zero-width chars = full payload]  ← contiguous, at text start
[TEXT BODY with redundant bits at word boundaries]  ← mid-text fragments
[REMAINING bits appended at end if body too short]  ← edge case fallback
```

The contiguous header is critical: it guarantees that any substring taken from
the **beginning** of the text (≥ ~80 chars, enough to include all 72 header chars)
retains the full watermark.

## Detection Algorithm

1. Extract all zero-width chars from input text → bit stream
2. Slide a 72-bit window across the bit stream
3. For each window: convert to 9 bytes, check if first 2 bytes == `0xC0DE`
4. If magic found: validate CRC-8 over bytes 0-7
5. Return `DetectionResult(is_watermarked=True, watermark_valid=crc_ok, ...)`

## Test Matrix (9 tests)

| Test | What it validates |
|---|---|
| `test_watermark_preserves_readability` | Stripping zero-width chars recovers original text |
| `test_detect_finds_watermark` | Round-trip: watermark → detect → valid |
| `test_detect_non_watermarked_text` | No false positives on clean text |
| `test_watermark_survives_copy_paste` | Substring extraction retains watermark |
| `test_metadata_signature_verification` | Ed25519 signature valid; tampered text fails |
| `test_visible_marker_fr_and_en` | Multilingual visible markers present (after stripping zero-width) |
| `test_no_spaces_edge_case` | Text without spaces uses append fallback |
| `test_short_text` | Very short text (<10 words) still watermarked |
| `test_crc_validation_catches_corruption` | Bit corruption after magic prefix → CRC fails |

## Dependencies

- `cryptography` (Ed25519) — falls back to HMAC-SHA256 if unavailable
- No model access required (post-generation application)

## Limitations (Assumed)

| Limitation | Reason | Acceptable because |
|---|---|---|
| Substrings < ~80 chars may not detect | Not enough chars to include full 72-bit header | Art. 50 targets complete generated content |
| Aggressive rewriting strips watermark | Zero-width chars are removed when text is retyped | Cryptographic metadata remains as provenance proof |
| Steganalysis can detect the mark | Zero-width chars are visible to technical inspection | Art. 50 requires *machine-readable*, not invisible |
