# Z.ai API Capabilities (Coding Plan Endpoint)

## Endpoint

```
Base URL: https://api.z.ai/api/coding/paas/v4
Auth: Bearer GLM_API_KEY (from ~/.hermes/.env)
```

## What Works ✓

| Feature | Model | Notes |
|---------|-------|-------|
| Chat completions | `glm-4.7` | OpenAI-compatible `/chat/completions`. Returns `reasoning_content` (CoT) alongside `content`. |
| Model listing | — | `/models` endpoint returns available models. |

### Chat Completions Example

```bash
curl -s https://api.z.ai/api/coding/paas/v4/chat/completions \
  -H "Authorization: Bearer $GLM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"glm-4.7","messages":[{"role":"user","content":"Bonjour"}],"max_tokens":50}'
```

Response includes `reasoning_content` in the message — this is the model's chain-of-thought. Useful for debugging but adds to token usage.

## What Does NOT Work ✗

| Feature | Error | Notes |
|---------|-------|-------|
| Audio transcriptions (Whisper) | `{"error":{"code":"1211","message":"Unknown Model"}}` | Z.ai coding endpoint has no speech-to-text. Use Groq Whisper or browser Web Speech API instead. |
| Vision/image analysis via browser tools | `{"error":{"code":"1210","message":"messages.content.type is invalid"}}` | The `browser_vision` tool sends image content that Z.ai rejects. Screenshots are still saved to `~/.hermes/cache/screenshots/`. Use `vision_analyze` tool as fallback (it routes to a vision-capable model). |

## Key Gotcha

The **coding endpoint** (`api.z.ai/api/coding/paas/v4`) is different from Z.ai's **general endpoint**. Using the wrong one → 429 or "Unknown Model". The Hermes config pins the coding endpoint; scripts that need the LLM should read from `~/.hermes/.env` to get the same key.
