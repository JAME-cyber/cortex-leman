#!/usr/bin/env python3
"""Vision check via Qwen 2.5 VL 72B (OpenRouter free tier).

Falls back to this when GLM-5.2 vision_analyze fails with error 1210
("messages.content.type is invalid, allowed values: ['text']").

Usage:
    python3 scripts/vision_check.py <image_path> [question]

Examples:
    # OCR a document/image from the project
    python3 scripts/vision_check.py /tmp/poster.jpg "Extract all text from this image"

    # Validate a video frame (contact sheet)
    python3 scripts/vision_check.py /tmp/contact_sheet.jpg "Check subtitles visibility and bandeau height"

    # Validate brand colors after build
    python3 scripts/vision_check.py /tmp/title_card.jpg "What are the dominant colors? Is terracotta present?"

Requirements:
    - OPENROUTER_API_KEY environment variable set
    - Python 3.6+ (stdlib only)
"""
import json, os, base64, subprocess, sys

img_path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/contact_sheet.jpg"
question = sys.argv[2] if len(sys.argv) > 2 else "Describe what you see in detail."

if not os.path.exists(img_path):
    print(f"Error: {img_path} not found", file=sys.stderr)
    sys.exit(1)

api_key = os.environ.get("OPENROUTER_API_KEY")
if not api_key:
    print("Error: OPENROUTER_API_KEY not set", file=sys.stderr)
    sys.exit(1)

with open(img_path, "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

payload = {
    "model": "qwen/qwen2.5-vl-72b-instruct",
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": question},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
            ]
        }
    ],
    "max_tokens": 1000
}

# Write payload to temp file to avoid arg-too-long errors with large images
with open("/tmp/qwen_payload.json", "w") as f:
    f.write(json.dumps(payload))

result = subprocess.run([
    "curl", "-s", "https://openrouter.ai/api/v1/chat/completions",
    "-H", f"Authorization: Bearer {api_key}",
    "-H", "Content-Type: application/json",
    "-d", "@/tmp/qwen_payload.json"
], capture_output=True, text=True, timeout=60)

try:
    resp = json.loads(result.stdout)
    if "choices" in resp:
        print(resp["choices"][0]["message"]["content"])
    else:
        print(f"Error: {json.dumps(resp)[:500]}", file=sys.stderr)
        sys.exit(1)
except json.JSONDecodeError:
    print(f"Error parsing response: {result.stdout[:500]}", file=sys.stderr)
    sys.exit(1)
