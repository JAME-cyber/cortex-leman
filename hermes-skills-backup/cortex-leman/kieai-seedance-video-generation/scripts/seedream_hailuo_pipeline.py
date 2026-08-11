#!/usr/bin/env python3
"""
Generic Seedream 5.0 Pro → Hailuo 2.3 Pro I2V pipeline.
Cost: ~59cr (14cr image + 45cr video) vs 205cr for direct Seedance T2V.

Use when: you need a cost-effective image-to-video pipeline, especially for
styles that benefit from a high-quality reference frame (cel-shaded anime,
illustrative, stylized) before animation.

CLI:
  python seedream_hailuo_pipeline.py \
    --image-prompt "cel-shaded 3D anime warrior..." \
    --video-prompt "character turns head, wind blows..." \
    --aspect-ratio 9:16 \
    --out-dir ./output

Requires: KIE_AI_API_KEY env var.
"""

import argparse, json, os, sys, time, requests

API_BASE = "https://api.kie.ai/api/v1"
HEADERS = lambda: {
    "Authorization": f"Bearer {os.environ['KIE_AI_API_KEY']}",
    "Content-Type": "application/json",
}


def submit(model, input_data):
    """Submit a kie.ai task. Returns taskId."""
    payload = {"model": model, "input": input_data}
    r = requests.post(f"{API_BASE}/jobs/createTask", json=payload,
                      headers=HEADERS(), timeout=30)
    resp = r.json()
    if resp.get("code") != 200:
        print(f"ERROR: submit failed — {resp}", file=sys.stderr)
        sys.exit(1)
    task_id = resp["data"]["taskId"]
    print(f"Submitted: {model} → taskId={task_id}")
    return task_id


def poll(task_id, timeout=600, interval=5):
    """Poll until success or timeout. Returns result URL."""
    print(f"Polling (timeout={timeout}s)...")
    start = time.time()
    while time.time() - start < timeout:
        time.sleep(interval)
        pr = requests.get(f"{API_BASE}/jobs/recordInfo",
                          params={"taskId": task_id},
                          headers=HEADERS(), timeout=30)
        data = pr.json().get("data", {})
        state = data.get("state", "")
        elapsed = int(time.time() - start)
        print(f"  [{elapsed}s] state={state}")
        if state == "success":
            result = json.loads(data["resultJson"])
            url = result["resultUrls"][0]
            print(f"✅ Success: {url}")
            return url
        elif state == "fail":
            print(f"❌ FAILED: {data}", file=sys.stderr)
            sys.exit(1)
    # Timeout — check one more time before giving up (pitfall #15)
    pr = requests.get(f"{API_BASE}/jobs/recordInfo",
                      params={"taskId": task_id},
                      headers=HEADERS(), timeout=30)
    data = pr.json().get("data", {})
    if data.get("state") == "success":
        result = json.loads(data["resultJson"])
        return result["resultUrls"][0]
    print(f"❌ Timeout after {timeout}s", file=sys.stderr)
    sys.exit(1)


def download(url, path):
    """Download a URL to a local file."""
    resp = requests.get(url, timeout=60)
    with open(path, "wb") as f:
        f.write(resp.content)
    size_kb = len(resp.content) // 1024
    print(f"✅ Saved: {path} ({size_kb}KB)")
    return path


def check_credits():
    """Return remaining credit balance."""
    r = requests.get(f"{API_BASE}/chat/credit", headers=HEADERS(), timeout=30)
    return r.json().get("data", "?")


def main():
    ap = argparse.ArgumentParser(description="Seedream → Hailuo I2V pipeline (~59cr)")
    ap.add_argument("--image-prompt", required=True, help="Seedream image generation prompt")
    ap.add_argument("--video-prompt", required=True, help="Hailuo video motion description")
    ap.add_argument("--aspect-ratio", default="9:16",
                    choices=["1:1", "4:3", "3:4", "16:9", "9:16", "21:9"])
    ap.add_argument("--out-dir", default="./output", help="Output directory")
    ap.add_argument("--name", default="pipeline_output", help="Base filename (no extension)")
    ap.add_argument("--duration", default="6", choices=["6", "10"], help="Video duration (Hailuo)")
    ap.add_argument("--resolution", default="768P", choices=["768P", "1080P"], help="Video resolution")
    ap.add_argument("--image-timeout", type=int, default=600, help="Seedream poll timeout (s)")
    ap.add_argument("--video-timeout", type=int, default=300, help="Hailuo poll timeout (s)")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    before = check_credits()
    print(f"Starting credits: {before}\n")

    # ── Step 1: Seedream image ──
    print("=" * 50)
    print("STEP 1: Seedream 5.0 Pro — reference frame")
    print("=" * 50)
    img_task = submit("seedream/5-pro-text-to-image", {
        "prompt": args.image_prompt,
        "aspect_ratio": args.aspect_ratio,
        "quality": "high",
        "output_format": "png",
        "nsfw_checker": False,
    })
    img_url = poll(img_task, timeout=args.image_timeout)
    img_path = os.path.join(args.out_dir, f"{args.name}.png")
    download(img_url, img_path)

    # ── Step 2: Hailuo I2V (URL passthrough — no upload needed) ──
    print(f"\n{'=' * 50}")
    print("STEP 2: Hailuo 2.3 Pro — animate frame (I2V)")
    print("=" * 50)
    vid_task = submit("hailuo/2-3-image-to-video-pro", {
        "prompt": args.video_prompt,
        "image_url": img_url,
        "duration": args.duration,
        "resolution": args.resolution,
        "nsfw_checker": False,
    })
    vid_url = poll(vid_task, timeout=args.video_timeout)
    vid_path = os.path.join(args.out_dir, f"{args.name}.mp4")
    download(vid_url, vid_path)

    # ── Summary ──
    after = check_credits()
    spent = round(before - after, 1) if isinstance(before, (int, float)) and isinstance(after, (int, float)) else "?"
    print(f"\n{'=' * 50}")
    print(f"DONE — Spent: {spent}cr | Remaining: {after}cr")
    print(f"Image: {img_path}")
    print(f"Video: {vid_path}")
    print("=" * 50)


if __name__ == "__main__":
    main()
