#!/usr/bin/env python3
"""
C2PA Signing Script for AI-Generated Videos
Signs videos with Content Provenance Authenticity metadata.

Usage:
  python sign_video.py <input_video> <output_video> [--title "Title"] [--project PROJECT]

Requirements:
  pip install c2pa-python
  Test certs from: https://github.com/contentauth/c2pa-rs (cli/sample/)
"""

import c2pa
import json
import os
import sys
import argparse
from datetime import datetime, timezone


# ─── Config ──────────────────────────────────────────────────────────────

CERT_DIR = os.environ.get(
    "C2PA_CERT_DIR",
    "/tmp/c2pa-rs/cli/sample"  # Default: test certs. Override for production.
)

# Project-specific metadata
PROJECTS = {
    "african-heroes": {
        "generator": "Tars Video Pipeline — African Heroes",
        "models": [
            {"name": "Seedance Video Model (ByteDance)", "version": "2.0"},
            {"name": "Edge TTS (Microsoft)", "version": "fr-FR-DeniseNeural"}
        ],
        "source_type": "trainedAlgorithmicMedia"
    },
    "culture-en-saveur": {
        "generator": "Tars Video Pipeline — Culture en Saveur",
        "models": [
            {"name": "Seedance Video Model (ByteDance)", "version": "2.0"},
            {"name": "Edge TTS (Microsoft)", "version": "fr-CH-SoraNeural"}
        ],
        "source_type": "trainedAlgorithmicMedia"
    },
    "darkom": {
        "generator": "Tars Video Pipeline — Darkom",
        "models": [
            {"name": "Seedance Video Model (ByteDance)", "version": "2.0"}
        ],
        "source_type": "compositeWithTrainedAlgorithmicMedia"
    },
    "socialpulse": {
        "generator": "Tars Video Pipeline — SocialPulse",
        "models": [
            {"name": "Seedance Video Model (ByteDance)", "version": "2.0"}
        ],
        "source_type": "compositeWithTrainedAlgorithmicMedia"
    },
    "default": {
        "generator": "Tars Video Pipeline",
        "models": [],
        "source_type": "trainedAlgorithmicMedia"
    }
}

SOURCE_TYPE_URI = "http://cv.iptc.org/nv/newscode/digitalsourcetype/"


def load_signer():
    """Load C2PA signer from certificate files."""
    cert_path = os.path.join(CERT_DIR, "es256_certs.pem")
    key_path = os.path.join(CERT_DIR, "es256_private.key")

    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        print(f"❌ Certificate files not found in {CERT_DIR}")
        print(f"   Clone: git clone https://github.com/contentauth/c2pa-rs.git /tmp/c2pa-rs")
        sys.exit(1)

    with open(cert_path, "rb") as f:
        cert_bytes = f.read()
    with open(key_path, "rb") as f:
        key_bytes = f.read()

    signer_info = c2pa.C2paSignerInfo(
        alg=c2pa.C2paSigningAlg.ES256,
        sign_cert=cert_bytes,
        private_key=key_bytes,
        ta_url=None
    )
    return c2pa.c2pa.create_signer_from_info(signer_info)


def build_manifest(title, project_name, extra_models=None):
    """Build C2PA manifest JSON for the video."""
    project = PROJECTS.get(project_name, PROJECTS["default"])
    models = project["models"].copy()
    if extra_models:
        models.extend(extra_models)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    source_type = f"{SOURCE_TYPE_URI}{project['source_type']}"

    manifest = {
        "claim_generator_info": [
            {"name": project["generator"], "version": "1.0"}
        ],
        "format": "application/c2pa",
        "title": title,
        "vendor": "tars",
        "assertions": [
            {
                "label": "c2pa.creation",
                "data": {"dateTime": now}
            },
            {
                "label": "c2pa.actions",
                "data": {
                    "actions": [
                        {
                            "action": "created",
                            "dateTime": now,
                            "softwareAgent": {
                                "name": models[0]["name"] if models else "Unknown",
                                "version": models[0].get("version", "") if models else ""
                            },
                            "digitalSourceType": source_type
                        }
                    ]
                }
            }
        ]
    }

    if models:
        manifest["assertions"].append({
            "label": "c2pa.ai_generative_training",
            "data": {
                "use": "trained",
                "entries": models
            }
        })

    return json.dumps(manifest, indent=2)


def sign_video(input_path, output_path, title, project_name):
    """Sign a video with C2PA metadata."""
    if not os.path.exists(input_path):
        print(f"❌ Input video not found: {input_path}")
        sys.exit(1)

    signer = load_signer()
    manifest = build_manifest(title, project_name)

    orig_size = os.path.getsize(input_path)

    builder = c2pa.Builder(manifest)
    builder.sign_file(input_path, output_path, signer)

    signed_size = os.path.getsize(output_path)
    overhead_kb = (signed_size - orig_size) / 1024

    return {
        "input": input_path,
        "output": output_path,
        "original_mb": orig_size / 1024 / 1024,
        "signed_mb": signed_size / 1024 / 1024,
        "overhead_kb": overhead_kb
    }


def verify_video(video_path):
    """Verify C2PA signature on a video."""
    reader = c2pa.Reader(video_path)
    raw = json.loads(reader.json())

    manifest = raw["manifests"][raw["active_manifest"]]
    state = raw.get("validation_state", "Unknown")

    return {
        "title": manifest.get("title", "N/A"),
        "generator": manifest["claim_generator_info"][0]["name"],
        "assertions": len(manifest.get("assertions", [])),
        "signature_alg": manifest["signature_info"]["alg"],
        "validation_state": state
    }


def main():
    parser = argparse.ArgumentParser(description="C2PA sign AI-generated videos")
    parser.add_argument("input", help="Input video path")
    parser.add_argument("output", help="Output signed video path")
    parser.add_argument("--title", default="AI-Generated Content (C2PA Signed)",
                       help="Title for the C2PA manifest")
    parser.add_argument("--project", default="default",
                       choices=list(PROJECTS.keys()),
                       help="Project preset for metadata")
    parser.add_argument("--verify-only", action="store_true",
                       help="Only verify existing C2PA signature")

    args = parser.parse_args()

    if args.verify_only:
        print("Verifying C2PA signature...")
        info = verify_video(args.input)
        print(f"  Title:       {info['title']}")
        print(f"  Generator:   {info['generator']}")
        print(f"  Assertions:  {info['assertions']}")
        print(f"  Algorithm:   {info['signature_alg']}")
        print(f"  Validation:  {info['validation_state']}")
        return

    print(f"Signing {args.input}...")
    result = sign_video(args.input, args.output, args.title, args.project)

    print(f"\n✅ Signed successfully!")
    print(f"   Original:   {result['original_mb']:.1f} MB")
    print(f"   Signed:     {result['signed_mb']:.1f} MB")
    print(f"   Overhead:   +{result['overhead_kb']:.0f} KB")
    print(f"   Output:     {result['output']}")

    # Auto-verify
    print(f"\nVerifying...")
    info = verify_video(result["output"])
    print(f"   Title:      {info['title']}")
    print(f"   Generator:  {info['generator']}")
    print(f"   Assertions: {info['assertions']}")
    print(f"   Validation: {info['validation_state']}")

    if "untrusted" in str(info["validation_state"]).lower():
        print(f"\n⚠️  Test certificate detected. Use production CA cert for official content.")


if __name__ == "__main__":
    main()
