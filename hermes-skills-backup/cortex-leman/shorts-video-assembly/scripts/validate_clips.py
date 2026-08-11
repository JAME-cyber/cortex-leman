#!/usr/bin/env python3
"""
GARDERAIL PIPELINE VIDÉO — À exécuter AVANT tout build.
Bloque si: clips insuffisants, loops détectés, ratio overuse, clips manquants.
Usage: python3 scripts/validate_clips.py <build_script.py>
Exit 0 = OK, Exit 1 = BLOQUÉ.
"""
import re, sys, json, subprocess
from pathlib import Path
from collections import Counter

# Ajuster BASE au projet vidéo courant
BASE = Path(sys.argv[1]).resolve().parent.parent if len(sys.argv) > 1 else Path.cwd()

def get_clip_duration(path):
    r = subprocess.run([
        "ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(path)
    ], capture_output=True, text=True)
    try:
        return float(json.loads(r.stdout)["format"]["duration"])
    except:
        return 0

def validate_build(script_path):
    errors = []
    warnings = []
    
    code = Path(script_path).read_text()
    
    # 1. Extraire les clips source (exclure seg/tmp/output/intro/cta/concat)
    clip_refs = re.findall(r'["\']([^"\']*\.mp4)["\']', code)
    source_clips = [
        c for c in clip_refs
        if not any(x in c for x in ['seg', 'tmp', 'concat', 'output', 'intro', 'cta', 'video_concat'])
    ]
    
    # 2. Détecter loops (même clip utilisé >1x dans les références source)
    counts = Counter(source_clips)
    for clip, count in counts.items():
        if count > 1:
            errors.append(f"LOOP: {clip} utilisé {count}x dans les références source")
    
    # 3. Ratio overuse (segments stretch > clips uniques)
    stretch_calls = code.count("stretch_video(")
    unique_clips = len(set(source_clips))
    if unique_clips > 0 and stretch_calls > unique_clips:
        errors.append(f"OVERUSE: {stretch_calls} segments stretch pour {unique_clips} clips uniques")
    
    # 4. Vérifier que les clips existent physiquement
    for clip in set(source_clips):
        full_path = Path(clip) if Path(clip).is_absolute() else BASE / clip
        if not full_path.exists():
            # Try relative to assets/videos/
            for alt_base in [BASE / "assets" / "book_series" / "videos",
                            BASE / "assets" / "videos",
                            BASE / "assets"]:
                alt = alt_base / Path(clip).name
                if alt.exists():
                    break
            else:
                errors.append(f"MISSING: {clip} introuvable")
    
    return errors, warnings

def main():
    if len(sys.argv) < 2:
        print("Usage: validate_clips.py <build_script.py>")
        print("Exit 0 = OK, Exit 1 = BLOQUÉ (clips insuffisants/loopés/manquants)")
        sys.exit(1)
    
    script = sys.argv[1]
    print(f"\n🔧 GUARDRAIL — Validation {Path(script).name}")
    print("=" * 50)
    
    errors, warnings = validate_build(script)
    
    if errors:
        print(f"\n🚨 BLOQUÉ — {len(errors)} erreur(s):")
        for e in errors:
            print(f"   ❌ {e}")
        print("\n⚠️ Le build a été arrêté pour éviter le gaspillage de crédits.")
        print("   Action: générer les clips manquants ou corriger les références.")
        sys.exit(1)
    else:
        print("\n✅ TOUS LES CHECKS PASSÉS — Build autorisé")
        if warnings:
            for w in warnings:
                print(f"   ⚠️ {w}")
        sys.exit(0)

if __name__ == "__main__":
    main()
