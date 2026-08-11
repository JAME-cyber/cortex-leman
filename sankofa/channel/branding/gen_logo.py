#!/usr/bin/env python3
"""Génère le logo Sankofa illustré via Seedream 5.0 Pro (kie.ai)."""
import os, requests, json, time, sys

# Load env
KIE_KEY = None
for line in open("/home/tars/.hermes/.env"):
    line = line.strip()
    if line.startswith("KIE_AI_API_KEY") and "=" in line:
        KIE_KEY = line.split("=", 1)[1].strip()
        break

if not KIE_KEY:
    print("ERROR: KIE_AI_API_KEY not found", file=sys.stderr)
    sys.exit(1)

BASE = "https://api.kie.ai"
OUT = "/home/tars/african-heroes/CHANNEL/branding/logo_sankofa_illustrated.png"

PROMPT = """Premium brand logo for "Sankofa" — an African history YouTube channel. 

Central element: a majestic Sankofa bird, stylized and elegant. The bird's body faces forward (to the right) but its head is gracefully turned backward (to the left), holding a single egg in its beak. This is the ancient Adinkra symbol of the Akan people of Ghana, meaning "go back and retrieve what was forgotten."

Art direction:
- Modern, premium brand identity — think tech startup meets cultural heritage
- Geometric, clean illustration style — not a flat traditional Adinkra print, but a sophisticated 3D-ish sculptural rendering
- Rich golden amber (#E8A33D) as primary color for the bird
- Deep anthracite (#1A1A1A) background  
- Subtle terra cotta (#B5522E) accents on the tail feathers
- The egg is warm ivory/sand colored (#F4E8D0)
- Soft volumetric lighting from upper left, giving the bird depth and presence
- Centered composition, symmetrical balance
- No text, no words, no letters — pure icon
- Clean edges suitable for use as avatar/favicon/thumbnail watermark
- Evokes wisdom, heritage, and forward motion grounded in the past"""

S = requests.Session()
S.headers.update({
    "Authorization": f"Bearer {KIE_KEY}",
    "Content-Type": "application/json"
})

# Step 1: Create task
print("Creating Seedream 5.0 Pro task...")
body = {
    "model": "seedream/5-pro-text-to-image",
    "input": {
        "prompt": PROMPT,
        "aspect_ratio": "1:1",
        "quality": "high",
        "output_format": "png",
        "nsfw_checker": False
    }
}

resp = S.post(f"{BASE}/api/v1/jobs/createTask", json=body, timeout=30)
data = resp.json()
print(f"Response: {json.dumps(data, indent=2)[:500]}")

if data.get("code") != 200:
    print(f"ERROR: {data}", file=sys.stderr)
    sys.exit(1)

task_id = data["data"]["taskId"]
print(f"Task ID: {task_id}")

# Step 2: Poll for result
print("Polling for result...")
for attempt in range(60):
    time.sleep(5)
    resp = S.get(f"{BASE}/api/v1/jobs/getTaskDetail?taskId={task_id}", timeout=15)
    result = resp.json()
    status = result.get("data", {}).get("status", "unknown")
    print(f"  [{attempt+1}] status={status}")
    
    if status == "success" or status == "SUCCEEDED":
        # Find image URL
        img_data = result["data"]
        img_url = img_data.get("resultUrl") or img_data.get("output") or img_data.get("url")
        if not img_url and isinstance(img_data.get("result"), list):
            img_url = img_data["result"][0].get("url")
        if not img_url and isinstance(img_data.get("result"), str):
            img_url = img_data["result"]
        
        if not img_url:
            print(f"Full result: {json.dumps(result, indent=2)[:1000]}")
            sys.exit(1)
        
        print(f"Downloading from: {img_url}")
        img_resp = requests.get(img_url, timeout=30)
        with open(OUT, "wb") as f:
            f.write(img_resp.content)
        print(f"Saved: {OUT} ({len(img_resp.content)} bytes)")
        break
    elif status in ("failed", "FAILED", "error"):
        print(f"FAILED: {json.dumps(result, indent=2)[:500]}")
        sys.exit(1)
else:
    print("TIMEOUT after 60 attempts", file=sys.stderr)
    sys.exit(1)
