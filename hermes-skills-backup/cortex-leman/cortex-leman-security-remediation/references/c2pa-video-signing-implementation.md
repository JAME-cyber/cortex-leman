# C2PA Video Signing — Working Implementation (c2pa-python)

Validated Aug 9, 2026 on African Heroes Ep. 2 (Mami Wata, 58 MB, 1080×1920, 1min50s).
Complements Pattern 4 (ChainMark text watermarking) with C2PA media provenance signing.

## Why This Exists

AI Act Art. 50(2) requires machine-readable marking of synthetic content since 2 Aug 2026.
ChainMark covers TEXT. C2PA covers IMAGES and VIDEO. Together = full Art. 50 compliance.

## Prerequisites

```bash
pip install c2pa-python   # ~5s, no cargo/rust needed
# cargo install c2patool  # AVOID: 300s+ compile time, times out
```

## Certificate Setup

C2PA requires X.509 certs from a recognized CA for "Valid" status. For testing, use the
official C2PA test certs from the c2pa-rs repo:

```bash
git clone --depth 1 https://github.com/contentauth/c2pa-rs.git /tmp/c2pa-rs
# Test certs: /tmp/c2pa-rs/cli/sample/es256_certs.pem + es256_private.key
# Trust anchors: /tmp/c2pa-rs/cli/sample/trust_anchors.pem
```

Self-signed certs (openssl req -x509) are REJECTED by c2pa-python with
`Signature: the certificate is invalid`. The c2pa-rs test certs work because they chain
to the C2PA Test Root CA included in the trust anchors.

Production: obtain a cert from a C2PA-recognized CA (~50-200 CHF/year).

## API Discovery (Non-Obvious)

The c2pa-python API (v0.37.5) has a multi-step setup that is NOT documented in the README:

```python
import c2pa, json

# Step 1: Read cert + key as BYTES (not strings!)
with open("es256_certs.pem", "rb") as f:
    cert_bytes = f.read()
with open("es256_private.key", "rb") as f:
    key_bytes = f.read()

# Step 2: Create C2paSignerInfo (bytes, not str)
signer_info = c2pa.C2paSignerInfo(
    alg=c2pa.C2paSigningAlg.ES256,
    sign_cert=cert_bytes,
    private_key=key_bytes,
    ta_url=None              # None = no timestamp authority (OK for testing)
                             # Production: set to a real TSA URL
)

# Step 3: Create Signer from info (separate step!)
signer = c2pa.c2pa.create_signer_from_info(signer_info)

# Step 4: Build manifest JSON (see structure below)
manifest_json = json.dumps(manifest, indent=2)

# Step 5: Sign
builder = c2pa.Builder(manifest_json)
builder.sign_file(source_path, dest_path, signer)  # NOTE: signer is 3rd arg

# Step 6: Verify
reader = c2pa.Reader(dest_path)
verified = json.loads(reader.json())
```

### Gotchas (all hit during implementation)

| Issue | Symptom | Fix |
|---|---|---|
| String vs bytes | `TypeError: bytes or integer address expected` | Read cert/key with `"rb"` mode |
| Signer type | `TypeError: expected str, bytes or os.PathLike, not C2paSignerInfo` | Use `create_signer_from_info()`, don't pass `C2paSignerInfo` directly to `sign_file` |
| `ta_url` HTTP 404 | `Signature: service responded with HTTP error (404)` | Set `ta_url=None` (not a URL string) for testing |
| Self-signed cert | `Signature: the certificate is invalid` | Use c2pa-rs test certs, not openssl self-signed |
| digitalSourceType enum int | `data did not match any variant of untagged enum DigitalSourceType` | Use full URI string: `http://cv.iptc.org/nv/newscode/digitalsourcetype/trainedAlgorithmicMedia` |
| First action type | `first action must be created or opened` | First action in `c2pa.actions` must be `"created"` or `"opened"`, not `"placed"` |

## Manifest Structure (Validated)

```json
{
  "claim_generator_info": [
    {"name": "Tars Video Pipeline", "version": "1.0"}
  ],
  "format": "application/c2pa",
  "title": "Mami Wata — African Heroes Episode 2",
  "vendor": "tars",
  "assertions": [
    {
      "label": "c2pa.creation",
      "data": {"dateTime": "2026-08-02T20:08:00Z"}
    },
    {
      "label": "c2pa.actions",
      "data": {
        "actions": [
          {
            "action": "created",
            "dateTime": "2026-08-02T20:08:00Z",
            "softwareAgent": {"name": "Seedance 2.0 via kie.ai", "version": "2.0"},
            "digitalSourceType": "http://cv.iptc.org/nv/newscode/digitalsourcetype/trainedAlgorithmicMedia"
          },
          {
            "action": "edited",
            "dateTime": "2026-08-02T20:15:00Z",
            "softwareAgent": {"name": "ffmpeg"},
            "digitalSourceType": "http://cv.iptc.org/nv/newscode/digitalsourcetype/compositeWithTrainedAlgorithmicMedia"
          }
        ]
      }
    },
    {
      "label": "c2pa.ai_generative_training",
      "data": {
        "use": "trained",
        "entries": [
          {"name": "Seedance Video Model (ByteDance)", "version": "2.0"},
          {"name": "Edge TTS (Microsoft)", "version": "fr-FR-DeniseNeural"}
        ]
      }
    }
  ]
}
```

### digitalSourceType URI Values

| Source Type | URI Suffix |
|---|---|
| Pure AI generated | `trainedAlgorithmicMedia` |
| AI + human composite | `compositeWithTrainedAlgorithmicMedia` |
| AI enhanced | `algorithmicallyEnhanced` |
| Human + AI edits | `humanEdits` |

Full base URI: `http://cv.iptc.org/nv/newscode/digitalsourcetype/`

## Verification Output

After signing, `c2pa.Reader(output_path).json()` returns:
- `active_manifest`: URN of the active manifest
- `manifests`: full manifest data (assertions, signature info, claim generator)
- `validation_status`: per-manifest validation results
- `validation_state`: "Valid" (production cert) or "Invalid" (test cert — expected)

### Test cert validation failures (EXPECTED)

With c2pa-rs test certs, `validation_state` will be "Invalid" with:
- `signingCredential.untrusted` — test cert not in production trust list
- This is NORMAL for testing. All assertions, hashes, and the manifest structure are valid.

## Performance

- 58 MB video: signing takes <2 seconds
- Overhead: ~14 KB (0.02% of file size)
- C2PA metadata is embedded in the file container (JUMBF boxes in MP4)

## Pipeline Integration

C2PA signing should be the LAST step in video production:

```
Script → Seedance generation → ffmpeg assembly → VO/music mix → C2PA sign → publish
```

The reusable signing script is at `scripts/sign_video.py`. It supports project presets
(african-heroes, culture-en-saveur, darkom, socialpulse, default) with pre-configured
model declarations.

## Legal Compliance Summary

| Jurisdiction | Status (Aug 2026) | Impact |
|---|---|---|
| EU AI Act Art. 50 | In force since 2 Aug 2026 | Synthetic content must be machine-readably marked |
| Switzerland | No direct obligation | But YouTube/IG accessible from EU = indirectly concerned |
| Omnibus extension | Systems pre-Aug 2 get until Dec 2, 2026 | Grace period for existing pipelines |

## Project Priority Matrix

| Project | Obligation | Why |
|---|---|---|
| culture-en-saveur | Mandatory | FB/IG visible in EU, children involved |
| african-heroes | Mandatory | YouTube global, realistic historical content |
| socialpulse-immo | Strong reco | B2B site EU-accessible |
| darkom-launch | Strong reco | B2B site EU-accessible |
| crypto/tiktok shorts | Optional | Short-form, not "realistic" per Art. 50 |
