# End Card / CTA Completeness — Verification Against Source Documents

## Problem

End cards and CTA segments are frequently incomplete compared to the official flyer/brief. This session (juil. 2026) revealed:
- **Age range** ("4 à 12 ans") missing
- **Prices** (85 CHF / 55 CHF) missing
- **Horaires** (8h30-13h30 / 13h30-18h30) missing
- **Sibling discount** (-10%) missing
- **Email typo**: `cultureensaveurs@gmail.com` (with S) on video vs `cultureensaveur@gmail.com` (no S) on official flyer — error propagated across 16 script occurrences

## Root Cause

End cards are designed from memory/approximation rather than systematically transcribing every data element from the official document. Email typos propagate because the wrong value gets hardcoded in the card builder script, then copy-pasted across all future build scripts.

## Prevention: Flyer → End Card Checklist

Before building ANY end card or CTA, extract ALL data elements from the official source document (flyer, brochure, questionnaire) and verify each one:

| Element | Source check | Common omission |
|---------|-------------|-----------------|
| Organization name | ✅ Usually present | — |
| Logo (official file) | ✅ Usually present | Agent draws replacement instead |
| Dates (exact format) | ⚠️ Check format + **YEAR** | "10-14 août" vs "du 10 au 14 août" — **year hardcoded as 2025 when it should be 2026** (3/6 videos affected, juil 2026) |
| Location (full address) | ⚠️ Check wording | "Petit-Lancy" vs full "Maison de Quartier du Plateau, Petit-Lancy" |
| Age range | ❌ FREQUENTLY OMITTED | "4 à 12 ans" |
| Prices (all tiers) | ❌ FREQUENTLY OMITTED | Full day, half-day, all options |
| Discounts | ❌ FREQUENTLY OMITTED | Sibling, early-bird, group |
| Horaires | ❌ FREQUENTLY OMITTED | Morning/afternoon start/end times |
| Phone (exact format) | ⚠️ Check +41 vs 0xx | CH formatting inconsistency |
| Email (EXACT spelling) | ❌ TYPO RISK | Extra/missing letter (S at end) |
| Social media handles | ❌ FREQUENTLY OMITTED | Instagram, Facebook |
| Tagline / slogan | ✅ Usually present | — |
| QR code | ❌ OMITTED | Requires flyer image asset |
| Website / registration URL | ❌ OMITTED | If separate from email |

## Verification Protocol (Post-Build)

After generating the end card image/video:

1. **Extract a clean full-resolution frame** at the end card timestamp:
```bash
ffmpeg -y -ss 99 -i video_final.mp4 -vframes 1 -q:v 1 /tmp/endcard_check.png
```

2. **Run Qwen VL vision check** reading ALL text:
```bash
python3 scripts/vision_check.py /tmp/endcard_check.png \
  "Read EVERY piece of text on this end card. List all elements. Check: dates, location, age, prices, horaires, phone, email (exact spelling), tagline, logo."
```

3. **Cross-reference** each element against the flyer checklist above.

4. **Email-specific check**: compare letter-by-letter. A single extra/missing letter renders the contact useless. If the email appears in multiple build scripts, fix ALL occurrences (grep first):
```bash
grep -r "cultureensaveurs" scripts/  # Find all occurrences of the typo
```

## Layout Pattern (Culture en Saveur, juil. 2026)

Validated end card layout (1080×1920 vertical):

```
┌─────────────────────────┐
│ [Logo officiel 420×420] │  y=120-540
│                         │
│   ÉVEIL AUX SAVEURS     │  y=560, PFAIR 44px, TERRA
│      AFRICAINES         │
│                         │
│ ATELIERS · 4 À 12 ANS   │  y=620, POPPINS 30px, OCHRE
│ ─────────────────────── │  y=680, separator OCHRE
│   10 – 14 août 2026     │  y=710, PFAIR 50px, TERRA
│ MQP · Petit-Lancy       │  y=780, POPPINS_REG 28px, CACAO
│ ┌─────────────────────┐ │  y=850-970, schedule box
│ │ Matin: 8h30-13h30   │ │    bg: warm beige, text: CREAM
│ │ Après-midi: 13h30-18h30│ │
│ └─────────────────────┘ │
│ ┌─────────────────────┐ │  y=1000-1160, price box
│ │ JOURNÉE    ½ JOURNÉE│ │    outline: TERRA 3px
│ │  85 CHF     55 CHF  │ │
│ │ −10% 2e enfant       │ │  y=1118, GREEN
│ └─────────────────────┘ │
│ ┌─────────────────────┐ │  y=1210-1300, CTA button
│ │ RÉSERVEZ LA PLACE   │ │    bg: TERRA, text: CREAM
│ └─────────────────────┘ │
│  +41 76 756 22 82       │  y=1360, contact
│  cultureensaveur@...    │  
│  @cultureensaveurs      │  y=1405, social
│                         │
│ ▓▓▓ DÉCOUVRIR · ▓▓▓▓▓▓ │  y=1820-1920, tagline bar
│ ▓▓▓ INSPIRER · ▓▓▓▓▓▓▓ │    bg: TERRA, text: CREAM
└─────────────────────────┘
```

Reference script: `~/culture-en-saveur/scripts/rebuild_endcard.py`
