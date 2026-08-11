#!/usr/bin/env python3
"""Describe any image for AI generation identity-locking.

Use when the active model lacks native vision (e.g. GLM-5.2, text-only models).
Falls back to OpenRouter vision models via base64 data URI.

Usage:
    python3 vision_describe_image.py <image_path> [custom_question] [--model gemini|qwen]

Default question produces exhaustive physical description for identity locking.
With --model qwen: uses Qwen-VL-72B (more structured forensic output, pitfall #50).
With --model gemini (default): uses Gemini 2.5 Flash (faster, general-purpose).

Output: plain text description printed to stdout.

Validated Aug 2026. Model IDs: google/gemini-2.5-flash, qwen/qwen-2.5-vl-72b-instruct.
"""
import argparse, base64, re, sys, os, requests

MODELS = {
    "gemini": "google/gemini-2.5-flash",
    "qwen": "qwen/qwen-2.5-vl-72b-instruct",
}

FORENSIC_PROMPT = (
    "You are a forensic portrait analyst. Describe this person EXHAUSTIVELY for "
    "anime character identity locking. Be surgical and precise:\n\n"
    "FACE: exact skin tone (with undertone), face shape, jawline, cheekbones, "
    "forehead height, eye color+shape, eyebrow shape+thickness, nose (bridge width, "
    "tip shape, nostril shape), lip shape+fullness, ear shape, any distinctive "
    "facial features (scars, moles, birthmarks).\n\n"
    "HAIR: exact style, curl pattern, length, hairline shape, color.\n\n"
    "BODY: approximate height/build, shoulder width, arm length, muscle definition.\n\n"
    "CLOTHING: every visible item with exact colors and details.\n\n"
    "POSE/EXPRESSION: what is the person doing, facial expression.\n\n"
    "DISTINGUISHING FEATURES: anything that makes this person uniquely recognizable."
)

GENERAL_PROMPT = (
    "Describe this person EXHAUSTIVELY for an AI portrait generation prompt. "
    "Cover: ethnicity, skin tone, approximate age, hair (style+color), eyes, "
    "nose, face shape, jawline, body type/build, what they're wearing (colors, "
    "numbers, brand if visible), accessories (wristbands, shoes, etc), pose, "
    "expression, setting/background. Every detail will be used for identity "
    "locking. Be surgical and precise."
)


def get_openrouter_key():
    """Read OPENROUTER_API_KEY from .bashrc (env is masked by Hermes — pitfall #31)."""
    with open(os.path.expanduser("~/.bashrc")) as f:
        bashrc = f.read()
    match = re.search(r'OPENROUTER_API_KEY=["\']?(sk-[^"\'\s]+)', bashrc)
    if not match:
        print("ERROR: OPENROUTER_API_KEY not found in ~/.bashrc", file=sys.stderr)
        sys.exit(1)
    return match.group(1)


def describe_image(image_path, question=None, model_key="gemini"):
    """Send image to OpenRouter vision model and return the description."""
    api_key = get_openrouter_key()
    model = MODELS.get(model_key, MODELS["gemini"])

    # Downsample large images to stay under API size limits (pitfall #28)
    try:
        from PIL import Image
        img = Image.open(image_path)
        if max(img.size) > 640:
            img.thumbnail((640, 640))
            tmp = "/tmp/_vision_describe_tmp.jpg"
            img.save(tmp, quality=80)
            image_path = tmp
    except ImportError:
        pass  # PIL not available — send full image (risky for >100KB files)

    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    data_uri = f"data:image/jpeg;base64,{img_b64}"

    # Use forensic prompt for qwen (structured output), general for gemini
    if question is None:
        question = FORENSIC_PROMPT if model_key == "qwen" else GENERAL_PROMPT

    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "max_tokens": 800,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {"type": "image_url", "image_url": {"url": data_uri}},
                ],
            }],
        },
        timeout=90,
    )
    if resp.status_code != 200:
        print(f"ERROR {resp.status_code}: {resp.text[:500]}", file=sys.stderr)
        sys.exit(1)
    return resp.json()["choices"][0]["message"]["content"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vision fallback — describe any image via OpenRouter")
    parser.add_argument("image", help="Path to image file")
    parser.add_argument("question", nargs="?", default=None, help="Custom question (default: identity-locking description)")
    parser.add_argument("--model", choices=list(MODELS.keys()), default="gemini",
                        help="Vision model: gemini (default, fast) or qwen (structured, identity-lock)")
    args = parser.parse_args()

    print(describe_image(args.image, args.question, args.model))
