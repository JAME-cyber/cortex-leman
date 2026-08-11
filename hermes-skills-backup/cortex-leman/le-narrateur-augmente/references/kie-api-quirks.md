# Kie.ai API — Quirks & Pitfalls

Condensed from live debugging sessions (July 2026). Kie.ai wraps multiple
model providers behind a unified jobs API, but the response shapes are
non-obvious and cost real debugging time.

## API Structure

Two endpoint families:
- **Dedicated Veo API:** `POST /api/v1/veo/generate` + `GET /api/v1/veo/recordInfo`
- **Market Jobs API** (everything else): `POST /api/v1/jobs/createTask` + `GET /api/v1/jobs/recordInfo`

Auth: `Authorization: Bearer <KIE_API_KEY>` header.

## Critical Quirks (cost us debugging cycles)

### 1. `state` ≠ `status`

The task status field is called **`state`**, not `status`. Polling for
`data["data"].get("status")` returns `None` / empty string forever.

```python
# WRONG — returns "?" indefinitely
status = data["data"].get("status", "")

# CORRECT
status = data["data"].get("state", "")
# Values: "waiting", "success", "fail"
```

Terminal states: `"success"`, `"fail"`. Intermediate: `"waiting"`.

### 2. `resultJson` is a JSON string, not an object

The result URLs are inside a field called `resultJson` which is a
**stringified JSON** containing `{"resultUrls": ["https://..."]}`.

```python
import json
result_json_str = data["data"].get("resultJson")  # it's a STRING
if result_json_str:
    rj = json.loads(result_json_str)
    urls = rj.get("resultUrls", [])  # list of URLs
    video_url = urls[0]
```

Do NOT look for `data["data"]["outputs"]` or `data["data"]["url"]` — those
don't exist for most market models.

### 3. Model identifiers require full provider paths

When calling `createTask` directly, the `model` field needs the **full
path** with provider prefix, not the friendly short name.

```python
# WRONG — returns {"code": 500, "data": null} silently
{"model": "seedance-2-fast", ...}

# CORRECT
{"model": "bytedance/seedance-2-fast", ...}
```

Known mappings:
| Friendly | Full path |
|----------|-----------|
| seedance-2-fast | `bytedance/seedance-2-fast` |
| seedance-2 | `bytedance/seedance-2` |
| kling-v3-turbo | `kling/v3-turbo-text-to-video` |
| wan-2.7-t2v | `wan/2-7-text-to-video` |
| nano-banana-2 | `nano-banana-2` (image — no prefix needed) |
| veo3 | uses dedicated `/api/v1/veo/` endpoints, not jobs API |

### 4. No public balance/credits endpoint

There is no documented API to check remaining credits. The only way to
discover insufficient credits is submitting a task and getting:

```json
{"code": 500, "msg": "Credits insufficient : Your current balance isn't enough..."}
```

**Check balance by logging into the kie.ai dashboard** before launching
a batch of clips. Each seedance-2-fast clip costs ~165 credits.

### 5. Temp URLs are directly downloadable

Result URLs like `https://tempfile.aiquickdraw.com/...` are publicly
accessible — no auth header needed for download. No need for a
`/common/download-url` conversion step.

```python
# Simple download, no auth
resp = requests.get(video_url, timeout=60)
Path(output).write_bytes(resp.content)
```

### 6. Error responses have `data: null`

When an error occurs (insufficient credits, bad model name, etc.), the
response is `{"code": 500, "msg": "...", "data": null}`. Always null-check
`data` before calling `.get()` on it:

```python
tdata = resp.json().get("data")
if not tdata or not isinstance(tdata, dict):
    # handle error — do NOT call tdata.get("taskId")
    error_msg = resp.json().get("msg", "unknown error")
```

## Image Generation (nano-banana-2, FLUX-2, etc.)

Same jobs API, same quirks. Key differences:
- Models like `nano-banana-2` do NOT need a provider prefix
- Cost: ~8 credits per image (vs ~165 per video clip)
- Poll interval: 5s, typical generation time: 15-20s
- Response shape is identical (`state`, `resultJson` with `resultUrls`)

## Python version note

The Hermes venv runs Python 3.11, but `kokoro-onnx` and `soundfile` are
installed under Python 3.12. TTS generation must use `python3.12`:

```bash
python3.12 -c "from kokoro_onnx import Kokoro; ..."
```

Kokoro can hang/timeout when generating 6+ clips in a single process.
Generate one clip per process invocation if memory pressure appears.
