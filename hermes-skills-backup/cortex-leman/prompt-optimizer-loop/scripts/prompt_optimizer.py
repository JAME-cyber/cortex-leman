#!/usr/bin/env python3
"""
Autoresearch-style prompt optimization loop for AI video generation.

Inspired by karpathy/autoresearch: generate → score → keep or discard → mutate → repeat.

Pattern:
  1. Generate a video from a base prompt (Hailuo Standard 6s 768p = 30cr)
  2. Extract mid-frame and score it via OmniRoute vision model (free, local)
  3. If score >= threshold (7/10): KEEP, record as winner
  4. If score < threshold: DISCARD, ask vision model for specific fixes,
     apply fixes to prompt, regenerate
  5. Repeat until budget exhausted or max iterations reached

Budget: 30cr per Hailuo Standard clip. With 400cr → ~12 iterations max.
QA is free (OmniRoute local proxy).

Usage:
  python3 prompt_optimizer.py --base-prompt "..." --budget 120 --threshold 7
  python3 prompt_optimizer.py --base-prompt-file prompt.txt --budget 180 --max-iters 5
"""
import argparse
import base64
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import http.client
import requests

# ── Config ──────────────────────────────────────────────────────────────────
KIE_API = "https://api.kie.ai/api/v1"
KIE_KEY = os.environ.get("KIE_AI_API_KEY", "")
KIE_HEADERS = {"Authorization": f"Bearer {KIE_KEY}", "Content-Type": "application/json"}

OMNI_HOST = "localhost"
OMNI_PORT = 20128
OMNI_MODEL = "auto/pro-vision"  # free local vision

HAILUO_MODEL = "hailuo/02-text-to-video-standard"  # T2V Standard = 30cr
HAILUO_COST = 30  # credits per clip

OUTPUT_DIR = Path(f"/tmp/prompt_optimizer_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
LOG_FILE = OUTPUT_DIR / "optimization_log.json"

# ── Kie.ai ──────────────────────────────────────────────────────────────────
def check_credits():
    r = requests.get(f"{KIE_API}/chat/credit", headers={"Authorization": f"Bearer {KIE_KEY}"})
    return r.json().get("data", 0)


def generate_video(prompt, out_path, duration="6", resolution="768P"):
    """Submit Hailuo Standard T2V job, poll, download."""
    payload = {
        "model": HAILUO_MODEL,
        "input": {
            "prompt": prompt,
            "duration": duration,
            "prompt_optimizer": True,  # built-in Hailuo prompt optimizer
        },
    }
    r = requests.post(f"{KIE_API}/jobs/createTask", headers=KIE_HEADERS, json=payload)
    resp = r.json()
    if resp.get("code") != 200:
        print(f"  SUBMIT ERROR: {json.dumps(resp)[:300]}")
        return None
    task_id = resp["data"]["taskId"]
    print(f"  taskId: {task_id}")

    # Poll
    for attempt in range(60):  # max 10 min
        time.sleep(10)
        r = requests.get(
            f"{KIE_API}/jobs/recordInfo?taskId={task_id}",
            headers={"Authorization": f"Bearer {KIE_KEY}"},
        )
        data = r.json().get("data", {})
        state = data.get("state", "unknown")
        print(f"  [{(attempt+1)*10}s] state={state}", flush=True)

        if state == "success":
            result_json = json.loads(data["resultJson"])
            urls = result_json.get("resultUrls", [])
            if urls:
                # Download
                resp_dl = requests.get(urls[0])
                resp_dl.raise_for_status()
                with open(out_path, "wb") as f:
                    f.write(resp_dl.content)
                print(f"  Downloaded: {out_path} ({len(resp_dl.content)/1024/1024:.1f}MB)")
                return task_id
        elif state == "fail":
            print(f"  FAILED: {data}")
            return None
    print("  TIMEOUT (10 min)")
    return None


# ── Frame extraction ────────────────────────────────────────────────────────
def extract_mid_frame(video_path, out_path="/tmp/opt_frame.jpg"):
    """Extract a frame at ~40% into the video."""
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", video_path],
        capture_output=True, text=True,
    )
    duration = float(json.loads(probe.stdout)["format"]["duration"])
    ts = duration * 0.4
    subprocess.run(
        ["ffmpeg", "-y", "-ss", str(ts), "-i", video_path, "-vframes", "1", out_path],
        capture_output=True, check=True,
    )
    return out_path


# ── Vision QA via OmniRoute ─────────────────────────────────────────────────
def score_frame(frame_path, prompt_used, iteration):
    """Send frame to OmniRoute vision model. Returns {score, fixes, analysis}."""
    with open(frame_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    user_text = f"""You are a senior VFX supervisor evaluating AI-generated video.
This is iteration #{iteration} of an optimization loop. The prompt used was:
---
{prompt_used[:500]}
---

Rate this frame 1-10 on:
1. CHARACTER QUALITY (faces, anatomy, clothing, identity coherence)
2. ENVIRONMENT (lighting, texture, realism, depth)
3. COMPOSITION (framing, visual flow, aesthetic appeal)

Then give:
- OVERALL SCORE (single integer 1-10, weighted average)
- TOP 3 FIXES: specific prompt changes that would improve the next iteration.
  Be concrete: name exact tokens to ADD or REMOVE from the prompt.

Respond in EXACTLY this JSON format:
{{"score": <int>, "character": <int>, "environment": <int>, "composition": <int>, "fixes": ["fix1", "fix2", "fix3"], "notes": "brief analysis"}}"""

    payload = {
        "model": OMNI_MODEL,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": user_text},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
        ]}],
        "max_tokens": 500,
        "stream": False,
    }

    for retry in range(3):
        try:
            conn = http.client.HTTPConnection(OMNI_HOST, OMNI_PORT, timeout=60)
            conn.request("POST", "/v1/chat/completions", json.dumps(payload), {"Content-Type": "application/json"})
            resp = conn.getresponse()
            raw = resp.read().decode()

            # Parse streaming or non-streaming
            content = ""
            if "data: " in raw:
                for line in raw.split("\n"):
                    if line.startswith("data: ") and "[DONE]" not in line:
                        try:
                            chunk = json.loads(line[6:])
                            c = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if c:
                                content += c
                        except:
                            pass
            else:
                d = json.loads(raw)
                content = d.get("choices", [{}])[0].get("message", {}).get("content", "")

            if not content.strip():
                print(f"  [QA retry {retry+1}] Empty response, retrying...")
                time.sleep(2)
                continue

            # Strip markdown code fences (```json ... ```)
            cleaned = content.strip()
            if cleaned.startswith("```"):
                lines = cleaned.split("\n")
                # Remove first line (```json or ```) and last line (```)
                lines = [l for l in lines if not l.strip().startswith("```")]
                cleaned = "\n".join(lines)

            # Extract JSON from response
            json_match = None
            for start in range(len(cleaned)):
                if cleaned[start] == '{':
                    # Find matching closing brace
                    depth = 0
                    for end in range(start, len(cleaned)):
                        if cleaned[end] == '{':
                            depth += 1
                        elif cleaned[end] == '}':
                            depth -= 1
                            if depth == 0:
                                json_match = cleaned[start:end + 1]
                                break
                    if json_match:
                        break

            if json_match:
                result = json.loads(json_match)
                return result
            else:
                # Fallback: try to find a number
                print(f"  [QA] Could not parse JSON, raw: {content[:200]}")
                return {"score": 5, "fixes": [], "notes": content[:200]}

        except Exception as e:
            print(f"  [QA retry {retry+1}] Error: {e}")
            time.sleep(2)

    return {"score": 0, "fixes": [], "notes": "QA failed after 3 retries"}


# ── Prompt mutation ─────────────────────────────────────────────────────────
def apply_fixes(prompt, fixes, iteration):
    """Apply vision-model-suggested fixes to the prompt."""
    if not fixes:
        # Auto-mutation: add specificity tokens
        mutations = [
            ", photorealistic textures, subsurface scattering on skin, individual hair strands catching light",
            ", shallow depth of field, natural golden hour lighting, soft ambient shadows",
            ", ultra-detailed fabric weave, visible skin pores, micro-imperfections, no CGI smoothness",
        ]
        addition = mutations[iteration % len(mutations)]
        return prompt + addition

    mutated = prompt
    for fix in fixes:
        # Simple heuristic: if fix says "add X", append X
        fix_lower = fix.lower()
        if "add" in fix_lower or "include" in fix_lower:
            # Extract the suggested content after the directive
            parts = fix.split(":", 1)
            if len(parts) > 1:
                addition = parts[1].strip().rstrip(".")
                mutated += f", {addition}"
        elif "remove" in fix_lower or "avoid" in fix_lower or "no " in fix_lower:
            parts = fix.split(":", 1)
            if len(parts) > 1:
                # Try to remove the token
                token = parts[1].strip().rstrip(".").strip('"').strip("'").lower()
                if token.lower() in mutated.lower():
                    # Case-insensitive replace
                    import re
                    mutated = re.sub(re.escape(token), "", mutated, flags=re.IGNORECASE)
    return mutated


# ── Main loop ───────────────────────────────────────────────────────────────
def run_optimization(base_prompt, budget_credits, threshold, max_iters, duration, resolution):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    credits_start = check_credits()
    print(f"{'='*60}")
    print(f"AI VIDEO PROMPT OPTIMIZER (autoresearch pattern)")
    print(f"{'='*60}")
    print(f"Credits: {credits_start} (~${credits_start * 0.005:.2f})")
    print(f"Budget: {budget_credits}cr ({budget_credits // HAILUO_COST} iterations max)")
    print(f"Threshold: {threshold}/10 to keep")
    print(f"Max iterations: {max_iters}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"{'='*60}\n")

    current_prompt = base_prompt
    best_score = 0
    best_prompt = base_prompt
    best_clip = None
    log = []

    for i in range(1, max_iters + 1):
        remaining = check_credits()
        if remaining < HAILUO_COST:
            print(f"\n❌ STOP: Not enough credits ({remaining}cr < {HAILUO_COST}cr)")
            break

        credits_spent = credits_start - remaining
        if credits_spent >= budget_credits:
            print(f"\n✅ Budget reached: {credits_spent}cr spent (limit: {budget_credits}cr)")
            break

        print(f"\n{'─'*50}")
        print(f"ITERATION {i}/{max_iters} | Credits: {remaining} (spent: {credits_spent}/{budget_credits}cr)")
        print(f"{'─'*50}")
        print(f"Prompt ({len(current_prompt)} chars):")
        print(f"  {current_prompt[:200]}{'...' if len(current_prompt) > 200 else ''}")

        # Step 1: Generate
        clip_path = OUTPUT_DIR / f"iter_{i:02d}.mp4"
        print(f"\n[GEN] Generating clip #{i}...")
        task_id = generate_video(current_prompt, str(clip_path), duration, resolution)
        if not task_id:
            print(f"  Generation failed, skipping")
            current_prompt = base_prompt  # reset
            continue

        # Step 2: Extract frame
        frame_path = str(OUTPUT_DIR / f"iter_{i:02d}_frame.jpg")
        extract_mid_frame(str(clip_path), frame_path)
        print(f"  Frame extracted: {frame_path}")

        # Step 3: Score
        print(f"\n[QA] Scoring via OmniRoute vision...")
        result = score_frame(frame_path, current_prompt, i)
        score = result.get("score", 0)
        fixes = result.get("fixes", [])
        notes = result.get("notes", "")
        char_score = result.get("character", "?")
        env_score = result.get("environment", "?")
        comp_score = result.get("composition", "?")

        print(f"  Score: {score}/10 (char={char_score}, env={env_score}, comp={comp_score})")
        if fixes:
            print(f"  Fixes suggested:")
            for j, fix in enumerate(fixes, 1):
                print(f"    {j}. {fix}")
        if notes:
            print(f"  Notes: {notes[:150]}")

        # Step 4: Keep or discard
        entry = {
            "iteration": i,
            "task_id": task_id,
            "clip": str(clip_path),
            "frame": frame_path,
            "prompt": current_prompt,
            "score": score,
            "scores": {"character": char_score, "environment": env_score, "composition": comp_score},
            "fixes": fixes,
            "notes": notes,
            "kept": score >= threshold,
        }
        log.append(entry)

        if score >= threshold:
            print(f"\n  ✅ KEEP (score {score} >= {threshold})")
            if score > best_score:
                best_score = score
                best_prompt = current_prompt
                best_clip = str(clip_path)
                print(f"  🏆 NEW BEST: {best_score}/10")
        else:
            print(f"\n  ❌ DISCARD (score {score} < {threshold}), will mutate prompt")

        # Step 5: Mutate for next iteration
        current_prompt = apply_fixes(current_prompt, fixes, i)

        # Save log after each iteration
        with open(LOG_FILE, "w") as f:
            json.dump({
                "base_prompt": base_prompt,
                "best_score": best_score,
                "best_prompt": best_prompt,
                "best_clip": best_clip,
                "iterations": log,
                "credits_start": credits_start,
                "credits_end": check_credits(),
            }, f, indent=2, ensure_ascii=False)

    # ── Summary ──────────────────────────────────────────────────────────────
    credits_end = check_credits()
    print(f"\n{'='*60}")
    print(f"OPTIMIZATION COMPLETE")
    print(f"{'='*60}")
    print(f"Iterations: {len(log)}")
    print(f"Credits used: {credits_start - credits_end}cr (~${(credits_start - credits_end) * 0.005:.2f})")
    print(f"Best score: {best_score}/10")
    if best_clip:
        print(f"Best clip: {best_clip}")
    print(f"\nBest prompt ({len(best_prompt)} chars):")
    print(f"  {best_prompt}")
    print(f"\nFull log: {LOG_FILE}")

    # Show progression
    if log:
        print(f"\nScore progression:")
        for entry in log:
            bar = "█" * entry["score"] + "░" * (10 - entry["score"])
            status = "✅" if entry["kept"] else "❌"
            print(f"  #{entry['iteration']:02d} {bar} {entry['score']}/10 {status}")

    return {"best_score": best_score, "best_prompt": best_prompt, "best_clip": best_clip, "log": log}


def main():
    p = argparse.ArgumentParser(
        description="Autoresearch-style prompt optimizer for AI video generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  # Optimize a cooking scene prompt with 120cr budget (4 iterations)
  python3 prompt_optimizer.py \\
    --base-prompt "A warm kitchen scene with a Somali woman cooking canjeero" \\
    --budget 120 --threshold 7 --max-iters 4

  # Use a prompt file
  python3 prompt_optimizer.py --base-prompt-file prompt.txt --budget 90
""")
    p.add_argument("--base-prompt", type=str, help="Base prompt to optimize")
    p.add_argument("--base-prompt-file", type=str, help="Read base prompt from file")
    p.add_argument("--budget", type=int, default=120, help="Max credits to spend (default: 120 = 4 clips)")
    p.add_argument("--threshold", type=int, default=7, help="Score threshold to keep (1-10, default: 7)")
    p.add_argument("--max-iters", type=int, default=6, help="Max iterations (default: 6)")
    p.add_argument("--duration", type=str, default="6", help="Video duration: 6 or 10 (default: 6)")
    p.add_argument("--resolution", type=str, default="768P", help="768P or 1080P (default: 768P)")
    args = p.parse_args()

    if not KIE_KEY:
        print("ERROR: KIE_AI_API_KEY not set")
        sys.exit(1)

    prompt = args.base_prompt
    if args.base_prompt_file:
        with open(args.base_prompt_file) as f:
            prompt = f.read()
    if not prompt:
        print("ERROR: provide --base-prompt or --base-prompt-file")
        sys.exit(1)

    run_optimization(
        prompt, args.budget, args.threshold, args.max_iters,
        args.duration, args.resolution,
    )


if __name__ == "__main__":
    main()
