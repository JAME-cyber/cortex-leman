#!/usr/bin/env python3
"""Generic Seedance 2.0 video generation script.
Works for ANY project (CES, Cortex Leman, african-heroes).

Usage:
  python seedance_generate.py --prompt-file prompt.txt --out clip.mp4
  python seedance_generate.py --prompt "your prompt" --out clip.mp4 \
      --model bytedance/seedance-2 --res 720p --ratio 9:16 --duration 5
  python seedance_generate.py --prompt-file prompt.txt --out clip.mp4 --mini

Decision: use --mini (seedance-2-mini) when credits < 205 or for prompt validation.
          use full seedance-2 for client deliverables.

Prerequisites:
  - KIE_AI_API_KEY env var must be set
  - pip install requests
"""
import argparse
import json
import os
import sys
import time

import requests

API = "https://api.kie.ai/api/v1"
KEY = os.environ.get("KIE_AI_API_KEY", "")
H = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}


def check_credits():
    r = requests.get(f"{API}/chat/credit", headers={"Authorization": f"Bearer {KEY}"})
    data = r.json()
    credits = data.get("data", 0)
    print(f"Credits: {credits} (~${credits * 0.005:.2f})")
    return credits


def submit_task(prompt, model, resolution, aspect_ratio, duration, generate_audio=True):
    payload = {
        "model": model,
        "input": {
            "prompt": prompt,
            "generate_audio": generate_audio,
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
            "duration": duration,
            "nsfw_checker": False,
        },
    }
    r = requests.post(f"{API}/jobs/createTask", headers=H, json=payload)
    resp = r.json()
    if resp.get("code") != 200:
        print(f"SUBMIT FAILED: {json.dumps(resp, indent=2)}")
        sys.exit(1)
    task_id = resp["data"]["taskId"]
    # Save taskId immediately — background scripts can timeout and lose it
    with open("/tmp/seedance_last_taskid.txt", "w") as f:
        f.write(task_id)
    print(f"taskId: {task_id}")
    return task_id


def poll_until_done(task_id, max_wait=600, interval=10):
    print("Polling...", flush=True)
    for i in range(max_wait // interval):
        time.sleep(interval)
        r = requests.get(
            f"{API}/jobs/recordInfo?taskId={task_id}",
            headers={"Authorization": f"Bearer {KEY}"},
        )
        data = r.json().get("data", {})
        state = data.get("state", "unknown")  # NOT "status" — pitfall #8
        print(f"  [{i * interval}s] state={state}", flush=True)

        if state == "success":
            result_json = json.loads(data["resultJson"])
            urls = result_json.get("resultUrls", [])
            print(f"URLs: {urls}")
            return urls
        elif state == "fail":
            print(f"FAILED: {data}")
            sys.exit(1)
    print("TIMEOUT")
    sys.exit(1)


def download(url, out_path):
    print(f"Downloading to {out_path}...")
    r = requests.get(url)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        f.write(r.content)
    size_mb = len(r.content) / (1024 * 1024)
    print(f"Saved: {out_path} ({size_mb:.1f} MB)")


def main():
    p = argparse.ArgumentParser(description="Seedance 2.0 video generation")
    p.add_argument("--prompt", type=str, help="Inline prompt text")
    p.add_argument("--prompt-file", type=str, help="Read prompt from file")
    p.add_argument("--out", type=str, required=True, help="Output .mp4 path")
    p.add_argument("--model", type=str, default="bytedance/seedance-2")
    p.add_argument("--mini", action="store_true", help="Use seedance-2-mini (cheaper)")
    p.add_argument("--res", type=str, default="720p",
                   choices=["480p", "720p", "1080p", "4k"])
    p.add_argument("--ratio", type=str, default="9:16",
                   choices=["1:1", "4:3", "3:4", "16:9", "9:16", "21:9", "adaptive"])
    p.add_argument("--duration", type=int, default=5, help="Seconds (4-15)")
    p.add_argument("--no-audio", action="store_true")
    args = p.parse_args()

    if args.mini:
        args.model = "bytedance/seedance-2-mini"
    if not KEY:
        print("ERROR: KIE_AI_API_KEY not set")
        sys.exit(1)

    prompt = args.prompt
    if args.prompt_file:
        with open(args.prompt_file) as f:
            prompt = f.read()
    if not prompt:
        print("ERROR: provide --prompt or --prompt-file")
        sys.exit(1)

    print(f"Model: {args.model} | {args.res} {args.ratio} | {args.duration}s")
    check_credits()

    task_id = submit_task(
        prompt, args.model, args.res, args.ratio, args.duration,
        generate_audio=not args.no_audio,
    )
    urls = poll_until_done(task_id)
    if urls:
        download(urls[0], args.out)
    check_credits()
    print("Done.")


if __name__ == "__main__":
    main()
