#!/usr/bin/env python3
"""Sélectionne le meilleur background parmi 6 variants Grok pour un acteur.
Score = contraste - pénalité luminosité (lum idéal = 70 pour thumbnails brightness 0.95).

Usage:
  python3 score_bg_candidates.py <actor_name>
  python3 score_bg_candidates.py ovhcloud

Affiche top 3 + verdict (TOP/OK/SKIP). Le user fait le choix final visuel.
"""
import sys
from pathlib import Path
from PIL import Image, ImageStat


def score_thumbnail_candidate(path: str) -> tuple[float, float, float]:
    """Retourne (lum, contraste, score). Score plus élevé = meilleur candidat."""
    img = Image.open(path).convert("RGB")
    s = ImageStat.Stat(img)
    r, g, b = s.mean
    lum = 0.299*r + 0.587*g + 0.114*b
    contrast = sum(s.stddev) / 3
    # Idéal: lum ~70 (pour thumbnail brightness 0.95 + gradient overlay)
    lum_pen = abs(lum - 70) * 0.5
    return lum, contrast, contrast - lum_pen


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 score_bg_candidates.py <actor>")
        print("Exemple: python3 score_bg_candidates.py ovhcloud")
        sys.exit(1)

    actor = sys.argv[1].lower()
    base = Path("/home/tars/crypto-project/CHANNEL/video3/grok_assets")
    results = []
    for i in range(1, 7):
        p = base / f"{actor}_split_v{i}.jpg"
        if not p.exists():
            continue
        lum, contr, score = score_thumbnail_candidate(str(p))
        results.append((i, lum, contr, score))

    if not results:
        print(f"❌ Aucun variant trouvé pour '{actor}' dans {base}")
        sys.exit(1)

    results.sort(key=lambda x: x[3], reverse=True)
    print(f"{'Variant':<12} {'Lum':>5} {'Contr':>6} {'Score':>6}  Verdict")
    print("-" * 50)
    for i, lum, contr, score in results:
        verdict = "🟢 TOP" if score > 55 else ("🟡 OK" if score > 40 else "🔴 SKIP")
        print(f"{actor}_v{i}.jpg  {lum:>5.0f} {contr:>6.0f} {score:>6.0f}  {verdict}")

    print(f"\n→ Retenir v{results[0][0]} (ou v{results[1][0]} en backup).")
    print("  Générer un side-by-side des top 3 et laisser le user valider visuellement.")


if __name__ == "__main__":
    main()
