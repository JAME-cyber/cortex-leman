# WORM Journal Hash Integrity — Pattern and Pitfall

**Origin**: TICKET-006 (2026-07-26), Cortex Leman v5
**Bug**: `verify_integrity()` systematically failed on entries where RGPD data minimization was applied

## Root Cause: Hash-Store Mismatch

The journal applied RGPD data minimization (replacing sensitive fields with `***REDACTED***`) **AFTER** computing the integrity hash. This meant the stored entry's payload didn't match the hash:

```
append() flow (BUGGY):
  1. entry = {payload: {"user": "Jean Dupont", "email": "jean@example.com", ...}}
  2. entry["hash"] = sha256(json.dumps(entry["payload"]))   ← hashes FULL payload
  3. entry["payload"] = minimize(entry["payload"])           ← NOW payload is different
  4. write entry to journal file
  → stored: {hash: <hash_of_full>, payload: {user: "***REDACTED***", email: "***REDACTED***"}}

verify_integrity() flow:
  1. read entry from journal
  2. recalc = sha256(json.dumps(entry["payload"]))            ← hashes MINIMIZED payload
  3. compare recalc vs entry["hash"]                          ← MISMATCH (always)
```

## Fix: Minimize BEFORE Hashing

```
append() flow (FIXED):
  1. entry = {payload: {"user": "Jean Dupont", "email": "jean@example.com", ...}}
  2. entry["payload"] = minimize(entry["payload"])            ← minimize FIRST
  3. entry["hash"] = sha256(json.dumps(entry["payload"]))     ← hash what you store
  4. write entry to journal
  → stored: {hash: <hash_of_minimized>, payload: {minimized}}

verify_integrity() flow:
  1. read entry
  2. recalc = sha256(json.dumps(entry["payload"]))            ← hashes MINIMIZED payload
  3. compare recalc vs entry["hash"]                          ← MATCH ✅
```

## General Rule

**Hash exactly what you store.** This applies to ANY transformation applied between hashing and storage:

| Transformation | Pitfall | Fix |
|---|---|---|
| RGPD minimization (redaction) | Hash computed on full, stored minimized | Minimize → hash → store |
| Encryption (Fernet, AES) | Hash computed on plaintext, stored ciphertext | Encrypt → hash(ciphertext) → store |
| Compression | Hash computed on raw, stored compressed | Compress → hash(compressed) → store |
| Serialization (JSON key ordering) | Hash on dict, stored as string | Serialize → hash(serialized) → store |

## Chain Integrity

WORM journals typically chain entries: each entry references the previous entry's hash:

```json
{"seq": 1, "payload": "...", "prev_hash": null, "hash": "aaa..."}
{"seq": 2, "payload": "...", "prev_hash": "aaa...", "hash": "bbb..."}
{"seq": 3, "payload": "...", "prev_hash": "bbb...", "hash": "ccc..."}
```

If any entry's hash is recalculated during repair, **all downstream entries' `prev_hash` must be updated** to maintain chain validity.

### Repair Procedure

1. Recalculate hash for the broken entry (on the stored payload)
2. Update the next entry's `prev_hash` to the new hash
3. Recalculate the next entry's hash (since its content changed)
4. Repeat until end of chain
5. Log the repair as a new journal entry

## Implementation (Cortex Leman v5)

File: `core/journal/append_only_journal.py`

Key method: `append()` — fixed to call `_minimize_payload()` BEFORE computing `content_hash`.

Key method: `verify_integrity()` — reads stored entries, recomputes hash on stored payload, verifies chain.

Key method: `_repair_entry()` — recalculates hash + propagates fix downstream.

## Testing (4 tests)

| Test | What it verifies |
|---|---|
| `test_append_and_verify` | Round-trip: append entry → verify passes |
| `test_minimized_payload_hash` | Entries with sensitive fields (minimized) verify correctly |
| `test_hash_chain_sequence` | Chain integrity: each entry links to previous |
| `test_repair_broken_entries` | Repair tool fixes broken hashes + propagates downstream |

All 4 tests pass. 579/579 production journal entries verified after fix + repair.
