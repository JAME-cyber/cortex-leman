#!/usr/bin/env python3
"""Seedance 2.0 — Template de génération vidéo via kie.ai API
Usage: python3 seedance_generate.py --prompt "..." --duration 10 --ratio 9:16 --res 720p

Dépendances: aucune (stdlib uniquement). Variable d'env: KIE_AI_API_KEY

Workflow:
1. POST /api/v1/jobs/createTask → task_id (sauvé dans /tmp/seedance_task_id.txt)
2. Poll /api/v1/jobs/recordInfo?taskId=... toutes les 10s
3. Download resultUrls[0] → output path
"""
import os, json, urllib.request, urllib.parse, time, sys, argparse

API_KEY = os.environ.get("KIE_AI_API_KEY")
if not API_KEY:
    print("ERROR: KIE_AI_API_KEY not set"); sys.exit(1)

BASE = "https://api.kie.ai"

def api_request(path, method="GET", body=None):
    url = f"{BASE}{path}"
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())

def submit_task(prompt, duration=10, ratio="9:16", resolution="720p", audio=True,
                model="bytedance/seedance-2", first_frame=None, last_frame=None,
                reference_images=None):
    payload = {
        "model": model,
        "input": {
            "prompt": prompt,
            "generate_audio": audio,
            "resolution": resolution,
            "aspect_ratio": ratio,
            "duration": duration,
            "nsfw_checker": False
        }
    }
    if first_frame: payload["input"]["first_frame_url"] = first_frame
    if last_frame: payload["input"]["last_frame_url"] = last_frame
    if reference_images: payload["input"]["reference_image_urls"] = reference_images

    result = api_request("/api/v1/jobs/createTask", "POST", payload)
    if result.get("code") != 200:
        print(f"ERROR: {json.dumps(result, indent=2)}"); sys.exit(1)

    task_id = result["data"]["taskId"]
    # CRITICAL: save task_id immediately in case of timeout
    with open("/tmp/seedance_task_id.txt", "w") as f:
        f.write(task_id)
    return task_id

def poll_task(task_id, max_wait=900, interval=10):
    """Poll until success/fail or timeout. Returns video URLs."""
    for attempt in range(max_wait // interval):
        time.sleep(interval)
        result = api_request(f"/api/v1/jobs/recordInfo?taskId={urllib.parse.quote(task_id)}")
        data = result.get("data", {})
        state = data.get("state", "unknown")
        print(f"  [{attempt+1}] State: {state}")

        if state == "success":
            result_json = data.get("resultJson", "{}")
            try:
                result_data = json.loads(result_json) if isinstance(result_json, str) else result_json
            except: result_data = {}
            urls = result_data.get("resultUrls", [])
            if not urls:
                print(f"Success but no URLs. Full: {json.dumps(result, indent=2)}"); return []
            return urls
        elif state == "fail":
            print(f"FAILED: {json.dumps(result, indent=2)}"); return []
    print(f"Timeout after {max_wait}s. Last state: {state}"); return []

def download_video(url, output_path):
    """Download via /api/v1/common/download-url (direct tempfile URL → 403)."""
    dl_result = api_request("/api/v1/common/download-url", "POST", {"url": url})
    if dl_result.get("code") != 200 or not dl_result.get("data"):
        print(f"ERROR getting download URL: {json.dumps(dl_result, indent=2)}")
        sys.exit(1)
    signed_url = dl_result["data"]  # valid 20 minutes only
    req = urllib.request.Request(signed_url)
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = resp.read()
    with open(output_path, "wb") as f:
        f.write(data)
    size_mb = len(data) / 1024 / 1024
    print(f"Downloaded: {output_path} ({size_mb:.1f} MB)")
    return output_path

def check_credits():
    result = api_request("/api/v1/chat/credit")
    return result.get("data", "?")

# --- Resume mode: if /tmp/seedance_task_id.txt exists, can resume polling ---
def resume_polling(task_id=None):
    if not task_id:
        try:
            with open("/tmp/seedance_task_id.txt") as f:
                task_id = f.read().strip()
        except FileNotFoundError:
            print("No task_id to resume."); return []
    print(f"Resuming polling for task: {task_id}")
    return poll_task(task_id)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seedance 2.0 video generation via kie.ai")
    parser.add_argument("--prompt", "-p", required=True, help="Text prompt (3-20000 chars)")
    parser.add_argument("--duration", "-d", type=int, default=10, help="Duration 4-15s (default: 10)")
    parser.add_argument("--ratio", "-r", default="9:16", help="Aspect ratio (default: 9:16)")
    parser.add_argument("--resolution", default="720p", help="480p/720p/1080p/4k (default: 720p)")
    parser.add_argument("--model", "-m", default="bytedance/seedance-2", help="Model name")
    parser.add_argument("--output", "-o", default="output.mp4", help="Output file path")
    parser.add_argument("--no-audio", action="store_true", help="Disable audio generation")
    parser.add_argument("--first-frame", help="First frame image URL")
    parser.add_argument("--last-frame", help="Last frame image URL")
    parser.add_argument("--resume", action="store_true", help="Resume polling from saved task_id")
    args = parser.parse_args()

    credits = check_credits()
    print(f"Credits: {credits}")

    if args.resume:
        urls = resume_polling()
    else:
        task_id = submit_task(
            prompt=args.prompt, duration=args.duration, ratio=args.ratio,
            resolution=args.resolution, audio=not args.no_audio, model=args.model,
            first_frame=args.first_frame, last_frame=args.last_frame
        )
        print(f"Task: {task_id}")
        urls = poll_task(task_id)

    if urls:
        download_video(urls[0], args.output)
    else:
        print("No video generated."); sys.exit(1)
