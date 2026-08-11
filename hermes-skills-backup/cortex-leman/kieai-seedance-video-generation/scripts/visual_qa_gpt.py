#!/usr/bin/env python3
"""
Visual QA for Seedance-generated videos using GPT-5.6 vision via OpenRouter.

Extracts a mid-video frame (or a specified frame number), sends it to GPT-5.6
with a VFX-supervisor prompt, and returns a structured critique.

Usage:
  python visual_qa_gpt.py <video.mp4> [--frame N] [--model openai/gpt-5.6]

Requirements:
  - OPENROUTER_API_KEY env var
  - ffmpeg (for frame extraction)
  - requests library

Workflow:
  1. Agent generates Seedance video
  2. Run this script for automated visual QA
  3. Feed the critique back into prompt fixes
  4. Regenerate if needed

Cost: ~$0.06 per analysis (based on 838 prompt + 800 completion tokens)
"""
import argparse, base64, json, os, subprocess, sys, requests

def extract_frame(video_path: str, frame_num: int = None, out_path: str = "/tmp/qa_frame.jpg") -> str:
    """Extract a single frame from a video via ffmpeg."""
    if frame_num is None:
        # Default: ~40% into the video (avoids blank intro/outro frames)
        probe = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", video_path],
            capture_output=True, text=True
        )
        duration = float(json.loads(probe.stdout)["format"]["duration"])
        timestamp = duration * 0.4
        subprocess.run(
            ["ffmpeg", "-y", "-ss", str(timestamp), "-i", video_path,
             "-vframes", "1", out_path],
            capture_output=True, check=True
        )
    else:
        subprocess.run(
            ["ffmpeg", "-y", "-i", video_path,
             "-vf", f"select=eq(n\\,{frame_num})", "-vframes", "1", out_path],
            capture_output=True, check=True
        )
    return out_path


def analyze_frame(frame_path: str, model: str = "openai/gpt-5.6", context: str = "") -> dict:
    """Send frame to GPT-5.6 vision via OpenRouter for VFX-supervisor critique."""
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        sys.exit("ERROR: OPENROUTER_API_KEY not set")

    with open(frame_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    context_line = f"\nContext: {context}" if context else ""

    prompt = f"""You are a senior VFX supervisor and AI video generation expert.
Analyze this frame from an AI-generated video.{context_line}

Be brutally honest and technically specific. Rate each dimension 1-10:

1. WATER/SURFACE REALISM (if applicable): reflections, ripples, physical coherence
2. LIGHTING/ATMOSPHERE: golden hour, mist, color gradient, natural feel
3. CHARACTER RENDERING: drift, warping, plastic skin, anatomical issues, limb fusion
4. BACKGROUND/ENVIRONMENT: geographic accuracy, texture quality, CGI vs real
5. COMPOSITION: framing for the aspect ratio, balance, visual flow
6. OVERALL PHOTOREALISM: would a casual viewer mistake this for real footage?

Then list:
- AI ARTIFACTS: every specific defect visible (blur, fusion, texture, polygon artifacts)
- TOP 3 FIXES: specific prompt changes to improve the next iteration
- VERDICT: usable as client deliverable as-is, or needs resolution upgrade?

Respond in French. Be concise (max 600 words)."""

    payload = {
        "model": model,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
            ]
        }],
        "max_tokens": 1000
    }

    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json=payload, timeout=120
    )
    if r.status_code != 200:
        sys.exit(f"OpenRouter error {r.status_code}: {r.text[:300]}")

    data = r.json()
    return {
        "analysis": data["choices"][0]["message"]["content"],
        "model": data.get("model", "?"),
        "cost": data.get("usage", {}).get("cost", "?"),
        "tokens": data.get("usage", {}).get("total_tokens", "?")
    }


def main():
    p = argparse.ArgumentParser(description="Visual QA for Seedance videos via GPT-5.6")
    p.add_argument("video", help="Path to video file")
    p.add_argument("--frame", type=int, default=None, help="Specific frame number (default: 40% in)")
    p.add_argument("--model", default="openai/gpt-5.6", help="OpenRouter model (default: openai/gpt-5.6)")
    p.add_argument("--context", default="", help="Extra context (e.g. 'paddleboard on Lake Geneva, Seedance 2.0 Mini 480p')")
    args = p.parse_args()

    frame = extract_frame(args.video, args.frame)
    print(f"Frame extracted: {frame}")

    result = analyze_frame(frame, args.model, args.context)
    print(f"\nModel: {result['model']} | Cost: ${result['cost']} | Tokens: {result['tokens']}")
    print(f"\n{'='*60}\nCONTRE-ANALYSE {args.model}\n{'='*60}\n")
    print(result["analysis"])


if __name__ == "__main__":
    main()
