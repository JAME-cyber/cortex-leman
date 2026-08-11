# TEMPLATE — Script clip vertical 9:16 (~50s)

> Reproduire avec modifications. Remplacer `[ACTEUR]`, `[ANGLE]`, sources, prompts visuels.
> Référence complète (script ASML validé) : `~/crypto-project/CHANNEL/clip_asml_taiwan_script.md`

---

# SCRIPT CLIP 9:16 — « [ACTEUR] : [ANGLE en 6-8 mots] »

> Format : Short vertical 9:16, ~50s · Voix-off unique (HenriNeural +10%)
> Acteur : **[ACTEUR]** ([place cotation, éligibilité PEA])
> Base factuelle : [Source 1] + [Source 2] + [Source corporate]
> Conformité : AMF L541-1 — commentaire économique, pas de conseil.
> Cours de référence : vérifier au jour J avant publication.

---

## [0:00 — BUMPER MARQUE]
*Intro signature L'EFFET COMPOSÉ — 5s, pad navy 9:16, logo doré animé.*
*Aucune narration — la signature porte.*

## [0:05 — HOOK VISUEL] *(9s)*

> *À l'écran : visuel Grok plein écran — [description]. Overlay texte doré : « [phrase choc sourcée, 5-8 mots] »*

**[VOIX-OFF]**

[2-3 phrases d'accroche. Premier mot = hook. Dernier = tension narrative. Toujours sourcé.]

## [0:14 — DATA 1] *(8s)*

> *Slide HTML navy — chiffre or géant : « [CHIFFRE] » · sous-titre : « [contexte] » · source : [Source]*

**[VOIX-OFF]**

[1-2 phrases reprenant le chiffre à l'oral, formulation différente de l'écran pour ne pas paraphraser.]

## [0:22 — DATA 2] *(10s)*

> *Slide HTML — [description visuelle]. Compteur : « [donnée] » · source : [Source]*

**[VOIX-OFF]**

[Phrase pivot qui crée la tension. "Mais voilà le piège…" / "Ce que personne ne dit…"]

## [0:32 — DATA 3] *(8s)*

> *Slide HTML — [schéma ou comparaison]. source : [Source]*

**[VOIX-OFF]**

[1 phrase élargissant au contexte géo/secteur. Terminer par le verbe d'action implicite.]

## [0:40 — CADRE ANALYTIQUE] *(7s)*

> *Slide HTML — framing or sur navy : « [INSIGHT ONE-LINER] » · mention discrète : « commentaire économique, pas un conseil »*

**[VOIX-OFF]**

[Synthèse en 1 phrase qui pose le cadre sans recommander. "C'est ça : [X] — et en même temps, [Y]."]

## [0:47 — CTA] *(3s)*

> *Visuel Grok plein écran — logo chaîne + texte : « L'EFFET COMPOSÉ — infra physique, cotée, décortiquée » · pan reverse.*

**[VOIX-OFF]**

L'infrastructure physique, cotée en bourse, décortiquée fait. Abonne-toi.

---

## 📋 Notes production (à compléter)

- **TTS** : `fr-FR-HenriNeural` +10%, débit par défaut. `phonetic_normalize()` sur tous les sigles du script (voir `references/edge-tts-pronunciation.md`). Tester prononciation des mots techniques au cas par cas.
- **Durée narration** : ~110 mots à ~145 wpm = ~45s de voix (5s bumper + 45s body + CTA).
- **Visuels Grok** : 2 prompts à générer (hook + CTA), 6 variants chacun via `grok_imagine_split.py`, même numéro de variant que la série en cours pour cohérence.
- **Slides HTML** : 3 slides (Data 1/2/3) + 1 framing. Palette `#04102B` / `#D2B257` / `#36D478`. Police : Inter Bold pour chiffres, Inter Regular pour labels.
- **BGM** : `audio/bgm_stellardrone.mp3` -24dB sous voix, fondu 2s entrée/sortie.
- **Assemblage** : `scripts/build_clips_template.py` — bumper(5s) + body(42s) + signature(3.5s), via `filter_complex` (PAS demuxer concat).

## 📚 Sources à citer en description YouTube

1. **[Source 1]** — [titre/auteur/date] — [URL]
2. **[Source 2]** — [titre/date] — [URL]
3. **Disclaimer long AMF** : "Ce contenu est fourni à titre informatif et pédagogique uniquement. Il ne constitue pas un conseil en investissement, ni une recommandation d'achat ou de vente. Consultez un conseil financier agréé avant toute décision."

## ⚠️ Points de vigilance AMF

- Vérifier qu'aucune phrase ne contient : acheter / vendre / opportunité / sous-évalué / surévalué / bon moment / pari sûr.
- Toute assertion chiffrée doit avoir une source au-dessous, pas "selon moi".
- Le cadre "infrastructure stratégique + otage/tension" = description factuelle, pas recommandation.
- Si le clip est un clip de **contexte stratégique** (pas de valuation), le dire explicitement en notes production — les autres clips de la série peuvent couvrir les chiffres financiers.
