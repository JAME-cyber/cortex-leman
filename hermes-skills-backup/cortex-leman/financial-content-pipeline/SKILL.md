---
name: financial-content-pipeline
description: Produire du contenu financier IA (podcasts multi-voix, clips verticaux, briefs) sur des valeurs cotées Euronext. Pipeline complet - edge-tts multi-voix, visuels Grok Imagine via kie.ai, guardrail AMF anti-conseil, assemblage ffmpeg. Palette dark navy/or/vert. Français par défaut.
tags: [content, podcast, clips, finance, amf, edge-tts, ffmpeg, grok-imagine, kie-ai]
---

# Financial Content Pipeline (L'EFFET COMPOSÉ)

Produire du contenu financier (podcasts, clips YouTube Shorts, briefs) sur des valeurs cotées Euronext via pipeline IA, avec conformité AMF (Code monétaire et financier L541-1).

## Quand l'utiliser

- Podcasts IA multi-voix (hôte + analyste)
- Clips verticaux 9:16 (Shorts YouTube) sur des actions cotées
- Briefs éditoriaux finance
- Analyse de contenu tierce (podcasts, tweets, articles) pour extraction/vérification de chiffres — applicable aux deux volets du projet
- Toute production de contenu finance FR où une IA génère du discours sur des titres cotés

## Périmètre du projet (~/crypto-project)

Le projet contient **deux volets** utilisant le même pipeline + guardrail AMF :

1. **L'EFFET COMPOSÉ** — chaîne YouTube clips 9:16 sur infrastructure physique cotée Euronext (OVHcloud, ASML, Soitec) + macro IA/énergie/semi-conducteurs. C'est le volet principal et le plus actif.
2. **Volet crypto actif** — BTC/ETH/onchain (non-coté, mais suivi analytique).

⚠️ **Ne pas assumer qu'une URL est "hors périmètre" juste parce qu'elle n'est pas Euronext.** Le volet crypto est légitime. Si un tweet/article crypto arrive en bare URL, faire l'analyse (le guardrail AMF couvre aussi la crypto — adapter les sources citées). Confirmer avec Thierry en cas de doute plutôt que de skip par défaut.

## Quand NE PAS l'utiliser

- Audit RGPD-IA (→ skill `le-gardien-des-normes`)
- Veille réglementaire (→ skill `le-gardien-des-normes`)
- Vidéos techniques non-finance (→ skill `faceless-explainer-video`)

## Stack technique

| Couche | Outil | Notes |
|---|---|---|
| Script | edge-tts direct ou LLM avec guardrail | ATTENTION : API chat kie.ai NON disponible sur compte basic — écrire le script directement |
| TTS hôte | edge-tts `fr-FR-HenriNeural` +5-10% | Cohérence marque |
| TTS analyste | edge-tts `fr-FR-DeniseNeural` +5% | Voix féminine claire (EloiseNeural = plus jeune, VivienneMultilingual = plus grave) |
| Visuels IA | Grok Imagine via kie.ai `grok-imagine/text-to-image` | $0.02/6 images, 9:16 natif. Voir `references/kie-ai-api-quirks.md` |
| Montage | ffmpeg | Ken Burns via `zoompan` + `preset=ultrafast` (validé video8 juil. 2026) |
| BGM | Stellardrone -22dB sous voix | `/home/tars/crypto-project/audio/bgm_stellardrone.mp3` |
| Assemblage | Python + ffmpeg concat | |
| **Fetch sources** | `scripts/fetch_source.py` (curl_cffi `chrome131`) | Passe Cloudflare sur IEA/Euronext. Cache disque 7j. Voir `references/antibot-scraping.md` |

## Conformité AMF — OBLIGATOIRE

**Article L541-1 du Code monétaire et financier** : le conseil en investissement est une activité réglementée. Pour produire du contenu finance sans agrément AMF, on active l'exemption "commentaire économique" via 4 conditions cumulatives.

### ❌ Formulations INTERDITES (basculent en conseil illégal)

- "Vous devriez acheter / vendre / conserver"
- "C'est le bon moment pour entrer / sortir"
- "Le titre est sous-évalué / surévalué" (sans source)
- Prix cible sans attribution explicite
- "Opportunité", "bon plan", "gagnant", "pari sûr"
- Toute recommandation personnalisée ou implicite

### ✅ Formulations AUTORISÉES (commentaire économique)

- Faits sourcés : "ASML affiche 30% de croissance en 2024"
- Citation explicite : "Le consensus analyste vise X€ selon Bloomberg"
- Questionnement : "Comment expliques-tu cette décote ?"
- Analyse comparative : "OVH se trade à 12x contre 35x pour AWS"
- Contexte historique : "Le secteur a connu 3 cycles"

### Règle d'or

Toute affirmation chiffrée ou valorisation doit être sourcée. Si pas de source, on pose une question au lieu d'affirmer.

### Disclaimer obligatoire (lu en intro par l'hôte)

> "Cet épisode est fourni à titre informatif et pédagogique uniquement. Il ne constitue pas un conseil en investissement, ni une recommandation d'achat ou de vente. Consultez un conseil financier agréé avant toute décision."

Voir `references/amf-guardrail-analyste.md` pour le system prompt complet de l'analyste IA (persona + guardrail intégré).

## Pipeline podcast (2 voix, ~2-5 min)

### 1. Script

Format Markdown avec balisage `**[HOST]**` et `**[CLAIRE]**`. Structure recommandée :

```
## [INTRO — DISCLAIMER]
**[HOST]** [disclaimer AMF + accroche]

## [ÉPISODE]
**[HOST]** [hook chiffré]
**[CLAIRE]** [challenge factuel sourcé]
**[HOST]** [réponse argumentée]
... (8-12 échanges)

## [OUTRO]
**[HOST]** [synthèse + teaser prochain épisode]
```

Template complet : `templates/podcast_script_template.md`

### 2. Génération audio

edge-tts génère un MP3 par ligne, puis concat. Script réutilisable : `scripts/build_podcast.py` (2 voix + BGM).

```python
VOICE_HOST = "fr-FR-HenriNeural"     # +5% (plus posé que clips)
VOICE_CLAIRE = "fr-FR-DeniseNeural"  # voix féminine claire
```

### 3. Assemblage

- Concat voice clips → `voice_full.mp3`
- BGM ducked -22dB (volume=0.08) looped + fades 2s
- Mix amix → MP3 final 192k

## Pipeline clips verticaux (Shorts 9:16)

### Durée cible : 45-60s par défaut, jusqu'à 90s si la matière le justifie

Format court par défaut (45-60s) pour le scroll. Un clip plus long (jusqu'à 90s) est acceptable **uniquement** si la chaîne de raisonnement ne peut pas être comprimée sans perte (ex: "Le Maillon Invisible" Trumpf → ASML → Chine nécessite les 3 maillons). Décision de jugement : si le script dépasse 60s, **prévenir l'utilisateur avant production** et confirmer le trade-off (longueur vs angle à couper). Ne pas silently produire 90s sur une cible 50s.

### Variante A — Hybride (Grok + slides), ~45-50s

Structure validée (inspirée Shorts financiers qui marchent) :

```
0-5s    INTRO signature marque (bumper)
5-14s   VISUEL GROK plein écran (hook visuel, pan animé)
14-45s  SLIDES HTML (data, chiffres, pédagogie)
45-50s  VISUEL GROK plein écran (CTA, pan reverse)
```

**Raison** : le visuel IA sert d'accroche scroll, les slides gardent leur rôle pédagogique. Évite la compétition visuelle (3 couches).

**Quand l'utiliser** : clips orientés acteur/société (OVHcloud, ASML) où un visuel fort aide au scroll-stop.

### Variantes de clips — ce qui EST et N'EST PAS optionnel

⚠️ **Intro signature + sous-titres = OBLIGATOIRES dans TOUTES les variantes.** La distinction entre Variantes A/B/C porte **uniquement sur l'usage des visuels IA**, pas sur l'intro ou les subs. Ne jamais produire un clip "slides-only" en omettant intro + subs — c'est un oubli signalé par Thierry (clip Trumpf V1, 2026-07-19 : "Il manque l'intro signature et les images grok" + "Et les sous titre").

| Élément | Variante A (Hybride) | Variante B (Slides-only) | Variante C (Composite broll) |
|---|---|---|---|
| Intro signature 5s | ✅ OBLIGATOIRE | ✅ OBLIGATOIRE | ✅ OBLIGATOIRE |
| Sous-titres burn-in | ✅ OBLIGATOIRE | ✅ OBLIGATOIRE | ✅ OBLIGATOIRE |
| BGM | ✅ | ✅ | ✅ |
| Visuel Grok plein écran (hook/CTA) | ✅ | ❌ | ❌ |
| Slides HTML | section pédagogique | ✅ 100% | ✅ avec background Grok |

### Variante A — Hybride (Grok plein écran + slides), ~45-50s

```
0-5s    INTRO signature marque (bumper)
5-14s   VISUEL GROK plein écran (hook visuel, pan animé)
14-45s  SLIDES HTML (data, chiffres, pédagogie)
45-50s  VISUEL GROK plein écran (CTA, pan reverse)
```

**Quand l'utiliser** : clips orientés acteur/société (OVHcloud, ASML) où un visuel fort aide au scroll-stop.

### Variante B — Slides-only (100% HTML), ~50-90s

Aucune image IA, uniquement des slides HTML 9:16 rendues via Playwright + Ken Burns doux ffmpeg. Intro + subs + BGM quand même.

```
INTRO 5s + 6-8 sections de slides HTML (1080x1920) + BGM + subs burn-in
```

**Quand l'utiliser** : clips pédagogiques (chaînes de valeur, comparaisons chiffrées) où le message est dans la donnée, pas dans l'esthétique.

### Variante C — Composite broll (Grok en background + overlay texte), ~50-90s

Hybride validé (clip Trumpf V2, 2026-07-19) : images Grok utilisées comme **backgrounds** pour certaines slides clés, avec overlay texte HTML par-dessus (gradient navy semi-transparent + contenu). Combine l'accroche visuelle du Grok avec la lisibilité des slides.

```
INTRO 5s
+ slides navy simples (hook, conclusion, disclaimer)
+ slides composites (broll Grok + overlay) pour les sections narratives clés
+ BGM + subs burn-in
```

**Quand l'utiliser** : clips où 2-3 moments clés bénéficient d'un visuel fort (clean room, chaîne de valeur, carte géo) sans sacrifier la lisibilité. Évite la compétition visuelle des 3 couches (Variante A) tout en cassant la monotonie du 100% slides.

**Technique composite** (voir `~/crypto-project/CHANNEL/video4/gen_broll_slides.py`) :

### Variante D — B-roll plein écran + caption semi-transparent (IMMERSIVE), ~75-110s

⚠️ **Préférence Tars validée 2026-07-21** (projet Sankofa) : pour le contenu narratif/historique, les slides opaques sont **rejetées** — le b-roll doit être **plein écran derrière le texte**, pas masqué. Le format slides-only (Variante B) marche pour la data finance, mais pour l'immersion narrative (personnages, actions, décors) il faut du visuel qui reste **visible**.

```
Chaque beat = une illustration d'action différente (b-roll plein écran + Ken Burns lent)
+ caption PNG semi-transparent en bas (gradient anthracite → transparent vers le haut)
+ texte doré/ambre sur la zone sombre du bas
```

**Différences clés vs Variante C** :
- Variante C : b-roll en background **d'une slide HTML** (overlay couvre ~60% de l'écran)
- Variante D : b-roll **plein écran**, caption couvre seulement le **bottom third** (~480px sur 1920)

**Architecture à 2 couches** (plus robuste que le composite HTML) :
1. **B-roll plein écran** → video segment (Ken Burns slow zoom, libx264 CRF 20)
2. **Caption PNG transparente** (Playwright capture) → overlay ffmpeg `[0:v][1:v]overlay=0:0`

```python
# Caption HTML (transparent bg, gradient sombre en bas seulement)
.caption-bar {
    position: absolute; bottom: 0; left: 0; right: 0;
    background: linear-gradient(to top,
        rgba(26,26,26,0.97) 0%,
        rgba(26,26,26,0.92) 55%,
        rgba(26,26,26,0) 100%);
    padding: 100px 60px 70px 60px;
    min-height: 520px;
}
```

⚠️ **PIÈGE CRITIQUE — Playwright `omit_background=True` OBLIGATOIRE pour les captions overlay** (validé 2026-07-21, projet Sankofa). Sans ce flag, Playwright capture les PNG avec un **fond blanc opaque par défaut** qui masque **totalement** le b-roll en arrière-plan. Symptôme : l'utilisateur voit "un fond blanc" au lieu des illustrations.

```python
# ❌ MAUVAIS — fond blanc opaque, b-roll invisible
page.screenshot(path=str(out_png))

# ✅ CORRECT — fond transparent (RGBA), b-roll visible derrière
page.screenshot(path=str(out_png), omit_background=True)
```

**Double condition** : `omit_background=True` dans l'appel Playwright **ET** `html { background: transparent }` dans le CSS (sinon le `<html>` reste blanc même avec le flag). Le `body` doit aussi être `background: transparent`. Les captions fullscreen (CTA, hooks) gardent un fond propre → NE PAS utiliser `omit_background` pour celles-là.

**Diagnostic en 30s** (quand l'utilisateur signale "fond blanc" ou images manquantes) : mesurer la luminance du segment composé vs le b-roll source via PIL :
```python
from PIL import Image, ImageStat
# B-roll source (devrait être sombre : ~40-90)
src = Image.open("broll/02_tapis_scene.png"); s = ImageStat.Stat(src.convert("RGB"))
print(f"Source brightness: {sum(s.mean)/3:.1f}")
# Frame extraite du segment final (devrait être similaire, pas >200)
ffmpeg -ss 1 -frames:v 1 ...  # extraire 1 frame
seg = Image.open("debug_frame.png"); s2 = ImageStat.Stat(seg.convert("RGB"))
print(f"Segment brightness: {sum(s2.mean)/3:.1f}")
# Si segment > 200 mais source < 100 → caption PNG opaque, fix omit_background
```

**S'applique à TOUT overlay PNG capturé via Playwright** (Variante D captions, thumbnails si overlay, tout PNG destiné à `ffmpeg overlay` sur un visuel de fond).

**Pourquoi pas composite HTML inline ?** Le composite HTML (slide avec `<img>` bg + overlay CSS) échoue souvent sur les filtres ffmpeg complexes (`gblur`, `brightness` sur 1080×1920). L'approche 2-couches (video segment + overlay PNG) est plus prévisible et debuggable. Si le composite échoue, le fallback est un still statique — acceptable pour un premier render.

**Prompt engineering b-roll narratif** (Seedream 5.0 Pro) : chaque beat décrit une **action spécifique** du personnage, pas un portrait générique. Ex Nzinga : "negotiation scene" / "on horseback charging" / "young princess training with spear" / "elderly woman signing treaty at 74". Plus l'action est spécifique, meilleure l'immersion. Voir `references/kie-ai-seedream-image-api.md`.

**Quand l'utiliser** : contenu narratif (histoire, biographie, storytelling) où l'immersion visuelle prime sur la densité de data. Pas adapté aux scorecards/chiffres (la lisibilité souffre).

### Variante E — Vidéo B-roll (clips IA au lieu d'images statiques), ~60-110s

⚠️ **Évolution naturelle de la Variante D** (validé 2026-07-22, projet Sankofa/african-heroes) : remplacer les images statiques + Ken Burns par des **clips vidéo IA** (Seedance 2.0 Fast, Veo 3.1). Le b-roll n'est plus une image fixe animée — c'est de la vraie vidéo cinématique.

```
Chaque beat = un clip vidéo IA différent (5s, scale→1080x1920)
+ caption PNG semi-transparent en HAUT (gradient anthracite → transparent vers le bas)
+ sous-titres ASS en BAS (MarginV=120)
+ BGM + watermark + outro signature
```

**Architecture** : identique à Variante D (2 couches : b-roll plein écran + caption overlay PNG transparent), sauf que le b-roll est une **vidéo** au lieu d'une **image**.

**Différences techniques clés vs Variante D** :
- **Scale** : Seedance sort 496×864 (9:16 natif). Scale simple `scale=1080:1920:flags=lanczos` — pas de crop, l'aspect ratio matche déjà
- **Freeze frame (PAS loop)** : les clips font 5s, les beats TTS font 5-20s. Si TTS > clip : utiliser `tpad=stop_mode=clone:stop_duration=N` (fige la dernière frame) — **JAMAIS `-stream_loop`** qui crée des boucles visibles (validé 2026-07-22, user correction « on pourrait pas faire en qu'il n'y ait pas de boucle »). Si TTS ≤ clip : `-t dur` (trim)
- **Pas de Ken Burns** : la vidéo IA a déjà son propre mouvement (caméra, action). Ajouter un crop animé par-dessus = double motion désorientant
- **Caption en HAUT, pas en BAS** (préférence Tars validée Sankofa) : le gradient sombre va du top vers le milieu, laissant le bas libre pour les sous-titres ASS

**Optimisation CPU multi-passes (CRITIQUE sur CPU lent type P8700)** :

⚠️ Le build vidéo à 3 passes par segment (scale → overlay caption → final encode) prend **>10 min sur CPU lent**. Sans optimisation, un foreground timeout de 600s est dépassé. Trois règles :

1. **`preset=ultrafast` pour TOUTES les passes intermédiaires** (segment vidéo, overlay caption). Garder `preset=medium crf=20` UNIQUEMENT pour l'assemblage final (subs+BGM+watermark). Les intermédiaires sont ré-encodés de toute façon au pass final — la qualité intermédiaire n'a pas d'impact sur l'output final.
2. **Cache de segments agressif** : avant de construire un segment, vérifier `seg_NN.mp4` existe ET `ffprobe duration ≥ dur - 0.2`. Si oui, skip. Permet de reprendre un build interrompu sans tout re-render.
3. **`background=true` + `notify_on_complete=true` OBLIGATOIRE** pour le build complet. Ne jamais lancer en foreground — le timeout de 600s sera dépassé sur CPU lent.

**Fallback image** : si pas de clip vidéo pour un beat (ex: archive, statue, carte), fallback sur image statique + Ken Burns (Variante D pattern). Le script doit gérer les deux sources dans la même boucle.

**Dual-mode build (vidéo + images)** : pour produire deux versions de la même vidéo (une avec clips Seedance, une avec images Seedream + Ken Burns), il suffit de basculer les `"video": "clip.mp4"` → `"video": None, "image": "image.png"` dans `BEATS_CONFIG`. Les captions, TTS, subs, BGM, watermark et outro sont identiques — seul le b-roll change. Ne pas dupliquer le script : un seul `build_v3.py` avec un flag ou deux configs. Utiliser des noms de sortie distincts (`nzinga_v3.mp4` vs `nzinga_v3_images.mp4`) pour ne pas écraser.

⚠️ **CRITIQUE — `get_dur` doit gérer les fichiers corrompus** (validé 2026-07-22) : quand un build en background est interrompu (timeout, kill manuel, ou crash), les segments en cours d'encodage restent sur disque avec un `moov atom not found` — `ffprobe` retourne une string vide, et `float("")` lève `ValueError`, faisant crasher tout le build au prochain lancement. Solution :

```python
def get_dur(path):
    r = subprocess.run(["ffprobe", ...], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except (ValueError, AttributeError):
        return -1.0   # sentinel: corrupt/missing file

# Cache check avec cleanup défensif :
if seg.exists():
    if get_dur(str(seg)) >= dur - 0.2:
        # cached, skip
    else:
        seg.unlink()  # corrupt — delete and rebuild
```

⚠️ **Compression Telegram <50MB** (validé 2026-07-22) : la vidéo finale 1080×1920 ~114s fait ~67MB, au-dessus de la limite TG de 50MB. Recipe de compression reproductible (perte visuelle minime, ~35MB output) :

```bash
ffmpeg -y -i input.mp4 \
  -c:v libx264 -preset fast -crf 26 \
  -maxrate 3200k -bufsize 6400k \
  -c:a aac -b:a 128k \
  -pix_fmt yuv420p -movflags +faststart \
  output_tg.mp4
```

Le `+faststart` est important pour le streaming TG (moov atom au début). CRF 26 avec maxrate 3200k donne un bon compromis qualité/taille pour du 9:16 narrative. Pour des vidéos plus longues (>2min), augmenter CRF à 28 ou réduire maxrate à 2500k.

Recipe complète (scale/loop/trim, cache, CPU opt, fallback) : `references/video-broll-assembly-recipe.md`
Template générateur : `templates/build_v3_video_broll.py`

**Quand l'utiliser** : projets narratifs avec budget vidéo IA (Sankofa/african-heroes, biographies historiques). Coût : ~77.5 crédits/clip Seedance 480p → ~465 crédits pour 6 clips. Pour LEC (finance), préférer Ken Burns statique (Variante D) — le coût vidéo IA n'est pas justifié pour des datacenters/GPU.

⚠️ **PITFALL — Ne pas réutiliser le même clip pour deux beats consécutifs** (validé 2026-07-22, user correction). Si deux beats successifs utilisent le même clip vidéo (ex: `02_tapis_scene.mp4` pour beat 01 ET beat 02), le freeze frame amplifie la répétition : le spectateur voit la même scène figée deux fois de suite. **Règle : un clip = un beat.** Si on n'a pas de clip distinct pour un beat, utiliser le fallback image (Ken Burns) plutôt que de dupliquer. Le coût de génération d'un clip supplémentaire (77.5 cr) est justifié par l'élimination de la répétition visuelle.

⚠️ **PITFALL — Prompt engineering pour l'exactitude historique des clips vidéo IA** (validé 2026-07-22, projet Sankofa, 4 itérations sur le clip beat 01). Les modèles vidéo IA (Seedance 2.0 Fast) génèrent des visuels **génériques et souvent anachroniques** par défaut. Sans contraintes explicites dans le prompt, ils produisent :
- **Tenues européennes médiévales** au lieu de vêtements africains traditionnels (générateurbiaisé vers l'iconographie européenne)
- **Positions/sujets inversés** : Nzinga sur un trône au lieu d'assise par terre, gouverneur debout au lieu d'installé sur le trône d'or usurpé
- **Anachronismes vestimentaires** : armures du Moyen-Âge au lieu d'attitudes nobles 1620s

**Règle de prompt engineering historique** : chaque prompt vidéo doit spécifier **4 dimensions obligatoires** :

1. **Époque exacte** (décennie, pas siècle vague) : "17th century 1620s" pas "medieval"
2. **Tenues précises** par personnage : "Mbundu royal garments, cowrie shell jewelry" + "1620s Portuguese noble attire" (pas "armor")
3. **Position spatiale** de chaque personnage : "Queen Nzinga sits HUMBLY ON THE BARE FLOOR" + "Portuguese governor sits ABOVE on a golden throne"
4. **Élément narratif clé** : "The throne does not belong to him" / "usurped royal throne"

**Anti-pattern** : un prompt court générique ("Queen Nzinga meeting Portuguese governor") produit invariablement un visuel inexact. Le coût de régénération (77.5 cr/clip) rend l'itération coûteuse — mieux vaut sur-spécifier le prompt la première fois.

**Validation utilisateur obligatoire** : sur modèle sans vision (GLM-5.2), il est impossible d'évaluer visuellement le clip généré. **Toujours livrer le clip via `MEDIA:` et attendre validation utilisateur avant de l'intégrer au build.** Ne pas autoproclamer un clip "bon" — l'agent ne peut pas le voir.

**Échelle d'itération observée** (clip Nzinga beat 01, 2026-07-22) :
| Tentative | Prompt | Coût | Résultat |
|---|---|---|---|
| 1 | "sitting on bare floor, looking up at governor" (court) | 77.5 cr | Tenue médiévale ❌ |
| 2 | "Portuguese governor on golden throne, Nzinga standing" | 77.5 cr | Nzinga debout (❌ position) + timeout |
| 3 | "Nzinga sits HUMBLY ON THE FLOOR, governor ABOVE on throne" | 77.5 cr | En cours... |

Total coût d'itération : 155+ cr pour un seul clip. **Moralité : sur-spécifier dès le premier prompt.**
```html
<img class='bg' src='file://{grok_image}'>           <!-- Grok 720x1280 scaled -->
<div class='overlay'>...texte HTML...</div>           <!-- gradient + contenu -->
```

⚠️ **CSS tuning — itérer (validé 2026-07-19, clip Trumpf V2, 2 itérations)** : trois paliers testés, du plus sombre au plus clair :

| Palier | `.bg` filter | `.overlay` gradient (top→mid→bot) | Luminance centre | Verdict Tars |
|---|---|---|---|---|
| Initial (V2) | `brightness(0.35)` | `0.85 → 0.40 → 0.85` | 31.8 | ❌ « on ne voit pas la photo, background sombre » |
| Corrigé 1 | `brightness(0.55) saturate(1.1)` | `0.75 → 0.15 → 0.75` | 40.3 (+27%) | ❌ « plus claire » (pas assez) |
| **Corrigé 2 (base)** | **`brightness(0.65) saturate(1.15)`** | **`0.65 → 0.10 → 0.65`** | **44.7 (+41%)** | ✅ validé |

**Valeurs de base par défaut** (clip Trumpf V2 final livré) :
```css
.bg{filter:brightness(0.65) saturate(1.15)}
.overlay{background:linear-gradient(180deg,
  rgba(4,16,43,0.65) 0%,rgba(4,16,43,0.10) 40%,rgba(4,16,43,0.65) 100%)}
```

**Principe de tuning** : le gradient garde le **top et le bottom à ≥0.65** (kicker en haut, stats/disclaimer en bas restent lisibles sur fond sombre) tandis que le **centre descend à 0.10** (la photo transparaît derrière le titre et le corps). Jouer sur les deux leviers ensemble : `brightness` contrôle la clarté de la photo, l'`overlay` mid-point contrôle la lisibilité du texte central. Ne pas monter `brightness` au-dessus de 0.75 sans monter aussi l'overlay mid (sinon le titre perd en contraste).

⚠️ **Validation visuelle sur modèle sans vision** (GLM-5.2/zai = error 1210 sur toute image) : `vision_analyze` et `browser_vision` échouent systématiquement. Workaround validé : **mesure quantitative Pillow + side-by-side livré au user**.
```python
from PIL import Image, ImageStat
img = Image.open("slide.png").convert("RGB")
w,h = img.size
center = img.crop((int(w*0.1),int(h*0.35),int(w*0.9),int(h*0.65)))
s = ImageStat.Stat(center)
lum = 0.299*s.mean[0]+0.587*s.mean[1]+0.114*s.mean[2]   # luminance perçue
contrast = s.stddev[0]                                     # contraste = photo présente vs fond plat
```
Puis générer un side-by-side avant/après (Playwright capture des deux variantes + `PIL.Image.paste` dans un montage 1080×960) et le livrer via `MEDIA:` pour validation humaine. La décision finale appartient toujours à Tars — ne jamais autoproclamer une slide « bonne » sans validation visuelle externe quand le modèle actif n'a pas la vision.

⚠️ **Faux positif stddev sur slides dark navy** (validé 2026-07-22, clip HuggingFace). Le seuil `stddev ≥ 90` est calibré pour des **photos broll**. Sur des slides HTML à fond navy (#04102B), le stddev global tombe à **25-30 même quand le texte est parfaitement net** — le fond sombre occupe >80% de la frame et écrase la variance.

**Diagnostic correct pour slides dark navy** :
```python
from PIL import Image
import numpy as np

img = np.array(Image.open("frame.png").convert("L"))

# 1. Scanner toutes les lignes pour trouver les bandes de texte
for y in range(0, 1920, 5):
    row = img[y, 100:1000]
    contrast = int(row.max()) - int(row.min())
    if contrast > 100:  # texte détecté

# 2. Edge sharpness autour du pixel le plus brillant
max_y, max_x = np.unravel_index(np.argmax(img), img.shape)
grad = np.diff(img[max_y-2:max_y+3, ...].astype(float), axis=0)
sharpness = np.abs(grad).max()  # >30 = SHARP
```

| Métrique | Seuil slides dark navy | Seuil broll photo |
|---|---|---|
| stddev global (PIL ImageStat) | **N/A** (fond sombre domine, 25-30 normal) | ≥ 90 |
| Contrast par ligne texte | ≥ 150 = texte lisible | — |
| Gradient edge sharpness | ≥ 30 = SHARP | — |

**Règle** : sur slides LEC navy, **ignorer le stddev global** et mesurer le contrast par ligne + edge sharpness sur les bandes de texte détectées. Un stddev global de 25 avec contrast 253 et edge sharpness 194 = texte parfaitement net.

**Template réutilisable** : `~/crypto-project/CHANNEL/video4/` contient les scripts paramétrables :
- `gen_tts.py` — dict `SECTIONS` (name → texte), rate +10%
- `gen_slides.py` — slides navy simples (CSS LEC 1080×1920)
- `gen_broll_slides.py` — slides composites (Grok + overlay) — nécessite images dans `slides/`
- `capture_slides.py` — Playwright PNG
- `gen_subs.py` — SRT + ASS avec offset intro (5.5s)
- `assemble.py` — V1 sans intro (à éviter)
- `assemble_v2.py` — V2 final avec intro + broll + subs burn-in

Pour un nouveau clip : copier `video4/` → `videoN/`, éditer `SECTIONS` + les `page()` HTML, générer les Grok via `grok_imagine.py <actor>`, lancer en séquence.

### Génération visuels IA

```bash
python scripts/grok_imagine_split.py ovhcloud  # génère 6 variants 9:16
```

Coût : $0.02/acteur (6 images). Toujours demander à l'utilisateur de choisir le variant retenu avant production.

### Ken Burns effect (zoompan — VALIDÉ avec preset=ultrafast)

⚠️ **Mis à jour 2026-07-24** : le pitfall original disait "zoompan trop lent, utiliser scale+crop". **Ceci est partiellement faux.** Le test real-world video8 EU Chips (Lenovo R500, Core 2 Duo) montre que `zoompan` fonctionne parfaitement (~10s/segment pour 20s de slide) **à condition d'utiliser `preset=ultrafast`**. Le problème venait du `preset=medium`/`preset=fast`, pas de `zoompan` lui-même.

**Pattern validé (video8, juil. 2026)** — zoompan sur slide statique 1080×1920 :
```python
# Pre-scale à 2x la résolution cible (nécessaire pour qualité zoompan)
filt = (f"scale=2160:3840:force_original_aspect_ratio=increase,"
        f"crop=2160:3840,"
        f"zoompan=z='min(zoom+{zoom_inc:.6f},1.04)':d={frames}:s=1080x1920:fps={FPS},"
        f"format=yuv420p")
# CRITIQUE: preset=ultrafast (sinon timeout CPU)
run(["ffmpeg", "-y", "-loop", "1", "-i", slide, "-i", au,
     "-vf", filt, "-t", str(D),
     "-c:v", "libx264", "-preset", "ultrafast", ...])
```

**Quand utiliser scale+crop au lieu de zoompan** :
- Images haute résolution (>2K) pré-scalées → zoompan génère des fichiers intermédiaires énormes (pitfall #17 du podcast skill)
- Slides parfaitement statiques où aucun mouvement n'ajoute de valeur
- CPU extrêmement limité (P8700 ou inférieur) sur batches >6 segments

**Règle de thumb** : `zoompan` + `preset=ultrafast` = OK pour slides LEC. `zoompan` + `preset=medium` = timeout garanti sur CPU lent. Le preset fait toute la différence.

Référence complète : `references/kie-ai-api-quirks.md`

## Pipeline podcast long-form bear case (LE CONTRE-POINT)

Série récurrente de podcasts **bear case** (16:9 horizontal, ~8-12 min, mono voix HenriNeural +0%) qui démonte la thèse bull présentée dans les Shorts. Chaque valeur couverte en bull case (OVHcloud, ASML...) obtient son épisode LE CONTRE-POINT.

### Différenciateur commercial + conformité

- **Concurrent** (Grand Angle Nova) ne produit que du bull case → bear case = avantage commercial
- **Conformité AMF L541-1 supérieure** : présentation équilibrée (bull + bear) = bien meilleur cadre défensif que bull case seul
- **Moat éditorial rare** : critères falsifiables publics — l'auditeur peut vérifier dans 6/12/24 mois si le contre-point tient

### Structure narrative (7 sections, ~1500 mots)

```
01_cold_open    [0:00]  Hook + disclaimer AMF renforcé
02_rappel       [0:45]  Rappel thèse bull en 3 piliers
03_angle1       [2:15]  Angle d'attaque 1
04_angle2       [4:30]  Angle d'attaque 2
05_angle3       [7:00]  Angle d'attaque 3
06_changement   [9:00]  Critères falsifiables (MOAT rare en finance FR)
07_verdict      [10:30] Verdict nuancé + outro MiFID II
```

### Spec techniques (vs Shorts)

| Paramètre | Shorts 9:16 | LE CONTRE-POINT 16:9 |
|---|---|---|
| Format | 1080×1920 vertical | 1920×1080 horizontal |
| Voix rate | +10% | **+0%** (posé, soutenabilité 8+ min) |
| BGM | -24 dB | **-28 dB** (discret, ne fatigue pas sur la durée) |
| Visuel | broll + slides | **slide statique unique** (la parole est le contenu) |
| Intro/outro signature | ✅ obligatoire | ❌ non (disclaimer AMF renforcé intégré au script) |
| Sous-titres | taille 42, par 4 mots | **❌ NON — pas de subs burn-in** |

⚠️ **Sous-titres OFF pour podcasts long-form** (préférence Tars validée 2026-07-19). Le podcast s'écoute, la slide statique reste lisible à l'œil nu. Les subs burn-in ralentissent inutilement le render (filtre ASS = 10x plus lent) et polluent le visuel minimaliste. Implémenter via un flag `SUBS_ENABLED = False` au début du générateur, et un branchement conditionnel du `-vf` :

```python
SUBS_ENABLED = False  # Podcast = écoute, pas lecture visuelle
...
vf = f"ass={ass_path},format=yuv420p" if SUBS_ENABLED else "format=yuv420p"
```

Les Shorts 9:16 gardent leurs subs (scroll mobile muet) — la distinction porte sur le format, pas sur le contenu.

### Conformité AMF/MiFID II — RENFORCÉE vs Shorts

Le bear case est plus exposé réglementairement que le bull case (implicite : "vendez"). Double disclaimer obligatoire :

- **Disclaimer intro** (~15s lu) : *"Avertissement : ce contenu est fourni à titre informatif..."* + mention positions déclarées en fin
- **Disclosure outro** (~10s lu) : *"L'auteur peut détenir, avoir détenu, ou envisager de détenir des positions... MiFID II..."*
- **Slide statique** : disclaimer visible en permanence (bas, opacity 0.4)

### Render long-form — attention au CPU

⚠️ **DEUX pièges CPU sur le render long-form (validé 2026-07-19)** :

**1. Burn-in ASS sur slide statique = ~15-20 min CPU.** Le filtre `ass=` re-encode chaque frame (15k+ frames pour 8 min à 30fps) même si l'image est statique. Sur le épisode pilote LE CONTRE-POINT (8.5 min), le render V1 avec subs a pris ~15 min. Solution : **désactiver les subs** pour le long-form (voir section spec table ci-dessus — `SUBS_ENABLED = False`).

**2. Slide statique 30fps = 15x trop de frames.** Même sans subs, encoder 15k frames d'une image fixe est gaspilleur. Solution validée : **2 fps** pour la slide statique. Le rendu passe de 15 min à **~60s**, qualité visuelle identique (image fixe = pas de motion à 30fps pour préserver).

```python
# AVANT (lent) :
"-loop","1","-framerate","30","-t",dur,"-i",slide_png,
"-c:v","libx264","-preset","medium","-crf","22","-r","30",

# APRÈS (rapide, qualité identique pour image fixe) :
"-loop","1","-framerate","2","-t",dur,"-i",slide_png,
"-c:v","libx264","-preset","ultrafast","-crf","23","-r","2",
```

YouTube accepte les vidéos à 2 fps sans problème pour un format podcast statique. Lancer **toujours** en `background=true` avec `notify_on_complete=true`, puis poll — ne pas bloquer la session principale.

### Recipe complète + template

- `references/le-point-contre-longform-recipe.md` — Recipe détaillée : positionnement éditorial, structure, conformité AMF renforcée, decisions de design validées (mono vs multi-voix, nom série, format visuel), honest gaps
- `templates/le_contre_point_template.py` — Générateur paramétrable (éditer `TITLE`, `EPISODE_NUM`, `TOPIC`, `SECTIONS`, lancer). 7 sections pré-structurées avec placeholders + disclaimers AMF/MiFII pré-rédigés.

### ⚡ Workflow copy-patch-render (MÉTHODE PAR DÉFAUT pour épisodes successifs)

⚠️ **Plus rapide que le template** : une fois le pilote épisode 1 produit et validé via le template ci-dessus, **les épisodes suivants se produisent par copy-patch du précédent** (~3 min/épisode, render compris). Validé en série (Ep 2 ASML + Ep 3 Soitec produits en une session, 2026-07-19).

**Procédure** (5 patches, tous dans `gen_podcast.py`) :

1. `cp epNN_<slug>/gen_podcast.py epNN+1_<new_slug>/gen_podcast.py`
2. Patcher 5 localisations :
   - `BASE = Path(".../epNN_<slug>")` → `.../epNN+1_<new_slug>"`
   - `<div class='episode'>Épisode N</div>` → `Épisode N+1`
   - `<div class='topic'>OLDSLUG — Le bear case</div>` → `NEWSLUG — Le bear case`
   - `print("  LE CONTRE-POINT — Épisode N : OLDSLUG")` → `Épisode N+1 : NEWSLUG`
   - `OUT = BASE / "le_contre_point_epNN_<slug>.mp4"` → `epNN+1_<new_slug>"`
   - **SECTIONS block** : remplacer le dict entier (cold_open → verdict). Les disclaimers intro/outro et le teaser outro sont des placeholders stables — ne réécrire que le contenu analytique.
3. Render en background : `python3 gen_podcast.py` (60s à 2fps, preset ultrafast).
4. Thumbnail en parallèle : `python3 thumbnails/gen_thumbnail.py <NN+1> <ticker> <company> <tagline> <bg.jpg>` (5s).
5. Écrire `YOUTUBE_UPLOAD.md` (voir section suivante).

Helper automatisant la copie + listant les 5 patches : `scripts/new_le_contre_point_episode.sh <ep_num> <slug>`.

**Quand utiliser copy-patch vs template** :
- Template : pilote (épisode 1) ou nouveau format dérivé (nouvelle série, nouveau style)
- Copy-patch : tous les épisodes suivants d'une série dont le pilote est validé

**Cas particulier : pas de clip bull case existant** (ex: Soitec n'avait pas de Short bull dédié). Reconstituer la thèse bull à partir du positionnement public de l'entreprise (rapport annuel, communiqués, présentations investisseurs), rédiger le bear case original, et **mentionner la reconstruction dans le `YOUTUBE_UPLOAD.md`** (section "Note de transparence"). Pas de désavantage crédibilité — l'auditeur reçoit l'info honnêtement.

### Package d'upload YouTube standard (`YOUTUBE_UPLOAD.md`)

Chaque épisode doit livrer un `YOUTUBE_UPLOAD.md` dans son dossier, prêt pour upload manuel ou automatisé. Structure :

```markdown
# LE CONTRE-POINT — Épisode N : <Company>
## Titre (SEO, ≤100 char, emot si pertinent)
## Description (accroche + résumé 3 angles + disclaimer AMF + mention conformité MiFID II / L541-1)
## Chapitres (format `00:00` avec timestamps alignés sur les 7 sections)
## Tags (ticker, entreprise, thématiques, série)
## Catégorie (Éducation / Finance)
## Paramètres vidéo (visibilité, public, langue, sous-titres FR via subs.srt)
## Fichiers à uploader (vidéo .mp4 + thumbnail .png + .srt)
```

Les chapitres doivent être **alignés sur les durations réelles** du `audio/durations.json` post-render (somme cumulée des sections). Ne pas estimer. Exemples validés : `CHANNEL/le_contre_point/ep0[1-3]_*/YOUTUBE_UPLOAD.md`.

## Pipeline thumbnails YouTube (LE CONTRE-POINT long-form + Shorts)

Les thumbnails sont le **#1 driver de CTR** sur YouTube — plus importants que le titre.

**Priorité long-form d'abord** (CTR critique sur feed desktop/TV). Mais les **Shorts méritent aussi un thumbnail custom** (validé 2026-07-19, 7 thumbs Shorts produites en un batch) : peu d'impact sur le feed mobile (frame auto), mais un réel effet "chaîne pro" quand un visiteur arrive sur la channel page (desktop + mobile). À produire en série avec le même template, pas clip par clip.

### Stack

| Couche | Outil | Pourquoi |
|---|---|---|
| Layout/typo | **HTML/CSS + Playwright capture** (1280×720) | Template-driven, reproductible, typo nette. Standard chaînes YT automatisées |
| Pré-traitement photo | **Pillow ImageStat** | Sélection objective du meilleur bg (luminance + contraste), pas de guesswork |
| Éviter | Canva / Photoshop / Photopea | Pas scriptable, pas reproductible à l'échelle (8+ épisodes) |

### Sélection photo de fond (PIL, pas de vision)

⚠️ Sur modèle sans vision (GLM-5.2/zai), on ne peut pas *voir* une photo pour la juger. Workaround validé : **scorer les 6 variants Grok par luminance + contraste objectives**, générer un comparatif side-by-side, livrer au user pour validation finale.

```python
from PIL import Image, ImageStat
def score_thumbnail_candidate(path):
    img = Image.open(path).convert("RGB")
    s = ImageStat.Stat(img)
    r,g,b = s.mean
    lum = 0.299*r + 0.587*g + 0.114*b
    contrast = sum(s.stddev) / 3
    # Idéal: lum 50-90 (overlay sombre sera ajouté), contraste élevé
    lum_pen = abs(lum - 70) * 0.5
    return contrast - lum_pen
# Score = trier décroissant, top 3 = candidats à comparer visuellement
```

### ⚠️ Tuning brightness background (LEÇON CLÉ 2026-07-19)

Tars a rejeté d'emblée le premier batch de thumbnails LE CONTRE-POINT (« le background est trop sombre »). Trois itérations ont convergé sur un base validée. **Ne jamais repartir de brightness <0.8 sur un thumbnail** — la photo doit rester visible.

| Palier | `brightness()` photo | Overlay | Lum centre | Verdict Tars |
|---|---|---|---|---|
| ❌ Trop sombre (V1 initiale) | `0.45` | **Uniforme 0.85** (tue la photo partout) | ~30 | « le background est trop sombre » |
| 🟡 B2 équilibré | `0.65` | Gradient directionnel | 34 | OK mais moins bon que B1 |
| ✅ **B1 validé (BASE)** | **`0.95` + `saturate(1.15)`** | **Gradient directionnel top 0.30 → bottom 0.75** | 49 | « Ok la première » |

**Deux leviers, à régler ensemble :**
1. `filter: brightness()` sur la photo — garder ≥0.8 sur thumbnails (≠ broll clips body où 0.65 marche car le texte occupe moins)
2. **Gradient directionnel** (pas d'overlay uniforme !) — sombre **uniquement là où le texte est** (bottom), clair là où la photo doit transparaître (top/centre)

```css
.bg  { filter: brightness(0.95) saturate(1.15); }
.overlay {
  background: linear-gradient(180deg,
    rgba(10,22,40,0.30) 0%,    /* top clair = photo visible */
    rgba(10,22,40,0.15) 35%,
    rgba(10,22,40,0.50) 65%,
    rgba(10,22,40,0.75) 100%); /* bottom sombre = texte lisible */
}
.title {
  text-shadow: 0 4px 24px rgba(0,0,0,0.95), 0 2px 4px rgba(0,0,0,0.8); /* double shadow */
}
.content { filter: drop-shadow(0 4px 12px rgba(0,0,0,0.6)); }
```

**Hard rule** : si un thumbnail paraît « sombre » au user, la cause est presque toujours l'**overlay uniforme** + un `brightness` bas. Monter `brightness` seul ne suffit pas si l'overlay reste uniforme — il faut passer à un **gradient directionnel**. (Voir aussi `references/clip-composite-variant-c-recipe.md` pour le tuning équivalent sur les broll clips body, palier différent car contexte différent.)

### Structure thumbnail LE CONTRE-POINT (template validé)

```
┌─────────────────────────────────────┐
│ [LE CONTRE-POINT]        Épisode 01 │  ← topbar navy→transparent
│                                     │
│                          ┌────────┐ │
│                          │   3    │ │  ← badge or "3 RISQUES" (top-right)
│   (photo bg sombre)      │ RISQUES│ │
│                          └────────┘ │
│                                     │
│ ▌OVH.PA▐                           │  ← ticker boxed gold
│ OVHCLOUD                            │  ← titre 108px bold
│ Ce qu'on ne vous dit pas            │  ← subtitle 42px
│                              [LOGO] │  ← logo coin
└─────────────────────────────────────┘
```

### 3 variants de tagline (test A/B/C, livrer les 3 au user)

| Variant | Tagline | Psychologie |
|---|---|---|
| V1 Minimaliste | "Le bear case" | Sérieux, premium, cible avertie |
| V2 3 risques (reco) | "Ce qu'on ne vous dit pas" + badge "3" | Promise claire, curiosité, large audience |
| V3 Curiosité | "Ce qui peut mal tourner" + flèche rouge baissière | Urgence, signal fort |

**Reco par défaut : V2** — la promise "3 risques" structure l'attente (l'auditeur sait quoi écouter), le badge or casse le sombre et attire l'œil sur mobile. V3 (flèche rouge) est cliché finance FR, à éviter.

### Pipeline par épisode (~30s de production)

1. Choisir la photo bg : scorer les 6 variants Grok par PIL, top 3 candidats
2. Générer les 3 variants de tagline en parallèle (même bg, 3 taglines)
3. Livrer les 3 PNG au user via `MEDIA:` → il choisit
4. Copier le retenu en `thumb_epNN_officiel.png`

Template réutilisable : `templates/gen_thumbnail_template.py` (paramétrable : `TICKER`, `TITLE`, `EPISODE_NUM`, `SUBTITLE`, `BG_PATH`).

### Thumbnails Shorts 9:16 (L'EFFET COMPOSÉ)

Branding **différent** du long-form (pas LE CONTRE-POINT) :
- Topbar « **L'EFFET COMPOSÉ** » (or) au lieu de « LE CONTRE-POINT »
- Badge or « CLIP A/B/C/D » ou « SHORT » en top-right (au lieu de la risk-box « 3 RISQUES »)
- Tagline en **or** (#d4a017), plus énergique que le blanc long-form
- Format **1080×1920** (vertical), pas 1280×720

Mêmes principes techniques que le long-form : brightness 0.95 + gradient directionnel + double text-shadow.

**Production en batch** (validé 2026-07-19) : un seul script génère les 7 thumbnails Shorts (clips A-D OVHcloud + TRUMPF + ASML + portfolio) en ~20s. Pré-sélectionner le meilleur bg par acteur via PIL (`contrast - abs(lum-70)*0.3`), puis capturer.

Template : `templates/gen_thumbnail_short_template.py`.

### Transcription YouTube (.srt) — GRATUITE via le TTS existant

Le `.srt` est un **sous-produit gratuit** de notre pipeline edge-tts : on connaît les timestamps exacts de chaque section parce qu'on génère l'audio nous-mêmes. **Ne jamais passer Whisper sur un clip qu'on a produit** — ce serait un stepdown (erreurs STT + perte de l'exactitude du texte source).

```python
# durations.json = {section_name: {duration, words, path}}
# → génère subs.srt avec offset intro (Shorts) ou continu (podcast)
```

**Upload YouTube** : uploader le `.srt` comme piste FR dans YouTube Studio → SEO (mots-clés indexés) + auto-traduction 100+ langues + chapters auto (YT crée les chapitres depuis le SRT) + accessibilité malentendants. Le `.srt` est déjà au format YouTube standard (voir `CHANNEL/le_contre_point/ep01_ovhcloud/audio/subs.srt` — 120 entrées, format `HH:MM:SS,mmm --> HH:MM:SS,mmm`).

**Package upload** par vidéo (fichier `YOUTUBE_UPLOAD.md`) : titre SEO, description avec disclaimer AMF, chapitres, tags, fichier vidéo + thumbnail + .srt à attacher.

## Palette & branding (L'EFFET COMPOSÉ)

| Couleur | Hex | Usage |
|---|---|---|
| Navy | `#04102B` | Fond principal |
| Vert | `#36D478` | Croissance, positif |
| Or | `#D2B257` | Accent, divider, CTA |
| Rouge | `#FF6B6C` | Alertes, négatif |

**Branding** : Toujours vérifier `/home/tars/crypto-project/branding/` avant de recréer un asset. Intro existante `intro_720p.mp4` (16:9 → à convertir en 9:16 par padding, pas par blur-fill ni SVG recreate).

## Pièges connus

### ffmpeg drawtext + emojis → "Filter not found" (VALIDÉ 2026-07-24)

⚠️ **Les emojis dans `drawtext` font crasher ffmpeg avec l'erreur "Filter not found"** (filtre `subtitles`/`ass` ou `drawtext` entier rejeté). La police DejaVu Sans Bold ne contient pas les glyphs emoji → ffmpeg parse error → tout le `filter_complex` échoue.

**Symptôme** : `Error parsing global options: Filter not found` avec un filter_complex par ailleurs valide.

**Fix** : retirer TOUS les emojis du texte `drawtext`. Remplacer par des équivalents texte :
- `✈️` → rien (le texte suffit)
- `👨‍👩‍👧‍👦` → retirer ou remplacer par "(famille)"
- `📞` → "Tel:" ou retirer
- `🇪🇬` → retirer (les drapeaux emoji ne passent JAMAIS)

**Règle** : `drawtext` ffmpeg n'est PAS UTF-16. Seuls les caractères latins + accents sont sûrs. Les emojis vont dans les slides HTML/Playwright (qui supportent UTF-8 nativement), jamais dans `drawtext` ffmpeg.

### API kie.ai

- ❌ `createTask` ne marche QUE pour image/vidéo. Les chat models nécessitent `/openai/v1/chat/completions` + accès compte séparé (souvent indisponible sur compte basic).
- ❌ Ne pas perdre 15 min à explorer les chat models si le compte n'a que des crédits image/vidéo. Écrire le script directement.
- ✅ Format image working : `{"model": "grok-imagine/text-to-image", "input": {"prompt": "...", "aspect_ratio": "9:16", "quality": "standard"}}`

### edge-tts

- ❌ `fr-FR-JennyNeural` n'existe pas (erreur `NoAudioReceived`).
- ✅ Voix FR féminines valides : `VivienneMultilingualNeural`, `DeniseNeural`, `EloiseNeural`.
- ⚠️ edge-tts 7.x : `WordBoundary` cassé → sous-titres proportionnels, pas mot par mot.
- ⚠️ **asyncio.run(tts) vs asyncio.run(tts())** : passer la fonction elle-même au lieu de la coroutine lève `ValueError: a coroutine was expected, got <function tts>`. Toujours **appeler** : `asyncio.run(tts())`. Piège réel (commis sur `gen_outro.py` 2026-07-19).

### ⚠️ Two-venv trap (Playwright vs edge-tts) — OBSOLÈTE, voir mise à jour 2026-07-21

⚠️ **La section ci-dessous décrit un état antérieur (avant 2026-07-21) et n'est plus fiable.** Les chemins de venv ont changé. La procédure de diagnostic reste valide mais les chemins exacts doivent être re-dérivés dynamiquement.

**État actuel (2026-07-21)** : le Python actif (`python3`) pointe vers `/home/tars/.hermes/hermes-agent/venv/bin/python3` (Python 3.11). Playwright n'y est **pas** installé par défaut. edge-tts y est.

**Procédure de diagnostic (toujours valide)** :

| Dépendance | Venv |
|---|---|
| `edge_tts`, `ffmpeg` (via subprocess) | `~/crypto-project/.venv/bin/python` |
| `playwright`, `edge_tts` (les deux) | `~/.venv/bin/python` |

**Règle pratique (mise à jour 2026-07-21)** : le venv actif est `/home/tars/.hermes/hermes-agent/venv/` (Python 3.11). Il n'a pas de `pip` module. Pour installer une dépendance manquante (ex: playwright), utiliser **`uv pip`** :

```bash
uv pip install playwright --python /home/tars/.hermes/hermes-agent/venv/bin/python3
```

**Diagnostic rapide** (si `ModuleNotFoundError: No module named 'playwright'`) :
```bash
ls -d /home/tars/.venv* 2>/dev/null
for v in /home/tars/.venv*/bin/python; do echo "=== $v ==="; $v -c "import playwright, edge_tts; print('both OK')" 2>&1 | head -1; done
```
Ne pas `pip install playwright` dans le venv projet — c'est déjà installé ailleurs, l'installer à nouveau duplique les dépendances Chromium (~300 MB).

### Prononciation sigles FR (OVH, ASML, ANSSI...)

⚠️ **edge-tts n'écorche PAS tous les sigles.** L'assumption « toujours normaliser » est fausse : ANSSI et FISA sont **mieux laissés bruts** (validé Thierry 2026-07-18, après test 4 variants). Ne jamais normaliser sans test comparatif préalable.

Quand un sigle est effectivement écorché, appliquer `phonetic_normalize()` avant `Communicate()`. Deux stratégies selon le contexte :

| Stratégie | Pattern | Usage |
|---|---|---|
| **Phonétique d'un bloc** | `Ovéache Cloud` | Phrase connectée (discours fluide) — ✅ validé OVH |
| **Points espacés** | `A. W. S.` | Sigle isolé ou énuméré (scorecard, liste) |
| **Brut** (pas de map) | `ANSSI`, `FISA` | Prononciation native edge-tts parfois MEILLEURE que toute substitution |

⚠️ **Les points espacés (`O. V. H. Cloud`) créent des pauses excessives en phrase connectée** — edge-tts interprète chaque point comme une fin de phrase. Thierry a rejeté cette variante pour OVH (2026-07-18) : préférer la phonétique `Ovéache Cloud` pour le discours fluide.

```python
PHONETIC_MAP = {
    "OVHcloud": "Ovéache Cloud",   # ✅ flow naturel
    "OVH":      "Ovéache",
    "Soitec":   "Soitèce",          # phonétique nom de marque
    "ASML":     "A. S. M. L.",     # points espacés — re-tester si usage en phrase
    "AWS":      "A. W. S.",
    "GCP":      "G. C. P.",
    "GPU":      "G. P. U.",
    "PEA":      "P. E. A.",
    # ANSSI, FISA → BRUTS (native edge-tts validée meilleure que toute substitution, 2026-07-18)
}
def phonetic_normalize(text):
    for orig, phon in PHONETIC_MAP.items():  # OVHcloud AVANT OVH (ordre!)
        text = text.replace(orig, phon)
    return text
```

⚠️ **Procédure avant tout ajout** : générer 8-12 variants orthographiques du sigle (mot brut, points, sans points, phonétique, traits, espaces), produire un MP3 comparatif par variante, faire écouter 3-4 samples au user, attendre verdict. **Tester en phrase connectée** (pas seulement en citation isolée — les pauses ne se manifestent qu'en discours fluide). Pattern détaillé + map validée : `references/edge-tts-pronunciation.md`.

### Disponibilité réelle des providers TTS (état 2026-07)

edge-tts est le **seul** TTS fonctionnel actuellement. Avant d'explorer un autre provider, vérifier d'abord :

| Provider | État | Raison |
|---|---|---|
| **edge-tts** | ✅ Actif | Gratuit, pas de clé |
| **ElevenLabs** | ⚠️ Configuré mais quota instable | `tts_engine.py` utilise George (voice_id `JBFqnCBsd6RMkjVDRZzb`, `eleven_multilingual_v2`). Clé `ELEVENLABS_API_KEY` présente dans `.env`. Fallback automatique vers edge-tts si quota dépassé (ApiError). Vérifier le quota avant une session de production |
| xAI TTS | ❌ 403 "Team not authorized" | Plan xAI sans Voice — tous endpoints `/v1/audio/speech` bloqués |
| Gemini TTS | ❌ 403 | `GEMINI_API_KEY` vide dans `.env` |
| OpenAI TTS | ❌ | Clé absente |
| Mistral TTS | ❌ | Clé absente |

**Diagnostic rapide** quand un TTS échoue : (1) `GET /v1/models` pour voir si des modèles `tts`/`voice`/`speech` apparaissent, (2) si 403 → problème de plan/team (pas la clé), (3) si clé vide dans `.env` → ajouter avant de tester.

Si l'utilisateur affirme qu'une clé/capacité existe : vérifier via `GET /v1/models` et un test endpoint **avant** de conclure. Ne pas supposer que l'utilisateur a tort, mais ne pas supposer non plus que la capacité est active — tester.

⚠️ **MCP / wrappers ne contournent pas un 403 provider** : un 403 "Team not authorized" vient du serveur xAI/Gemini/etc. MCP (Apify, natif, SDK) ne fait que relayer l'appel — il hérite de la même restriction. Ne pas perdre de temps à explorer MCP comme solution à un blocage de plan/provider.

⚠️ **Apify `fayoussef/bulk-text-to-speech` = wrapper edge-tts** : cet Actor expose les voix Azure (`fr-FR-HenriNeural`, `fr-FR-DeniseNeural`, etc.) via MCP, mais c'est **littéralement edge-tts emballé** (mêmes voix, même moteur). Payant ($0.03/épisode) pour un résultat identique au edge-tts gratuit. Ne pas utiliser pour remplacer edge-tts — utile seulement si on veut le SRT généré en bonus et qu'on est déjà sur Apify.

Pour activer un TTS premium : ElevenLabs ($5/mois, voix FR excellentes) ou activer le plan Voice xAI sur le compte existant.

### Visuels IA (Grok Imagine)

- ⚠️ Le modèle ne respecte pas toujours `#04102B` littéral. Tollerance acceptable.
- ✅ Toujours générer 6 variants et laisser l'utilisateur choisir. Cohérence série = même numéro de variant pour tous les acteurs (ex: tous v1).

### ⚠️⚠️ xAI Imagine DIRECT vs kie.ai — ne JAMAIS utiliser xAI direct pour les images

**Piège financier majeur** (validé 2026-07-18) : l'endpoint xAI direct `/v1/images/generations` fonctionne avec la clé `XAI_API_KEY`, mais facture **$2/image** (modèle `grok-imagine-image`) contre **$0.003/image** via le proxy kie.ai — soit **~100x plus cher pour le MÊME moteur Grok Imagine**. Le modèle quality (`grok-imagine-image-quality`) monte à $5/image.

| Provider | Coût/image | 12 visuels (série 3 acteurs) | Latence |
|---|---|---|---|
| **kie.ai** (proxy, compte existant) | $0.003 | **$0.04** | ~30s |
| xAI direct (`grok-imagine-image`) | $2.00 | $24 | ~6s |
| xAI quality (`grok-imagine-image-quality`) | $5.00 | $60 | ~6s |

**Règle : toujours kie.ai pour les images.** La clé xAI directe sert pour le **chat** (`grok-4.20-reasoning`) — pas pour Imagine.

**Quirks API xAI direct** (si jamais on doit l'utiliser) :
- ❌ `response_format: "url"` → retourne une URL `imgen.x.ai` qui **403 au download** même avec bearer auth.
- ✅ `response_format: "b64_json"` → retourne l'image en base64, téléchargeable.
- ❌ Model `grok-2-image` → 404 (n'existe pas). Le bon nom est `grok-imagine-image`.
- Coût lu dans `response.usage.cost_in_usd_ticks` (diviser par 1e8 pour USD).

Recipe API complète + transcript de test : `references/xai-imagine-direct.md`.

### Intro 16:9 → 9:16

- ❌ Blur-fill = superposition visuelle gênante (deux frames qui se battent).
- ❌ Recréation SVG totale = perte de l'effet cinématique i2v original.
- ✅ Padding solid navy (#04102B) + overlay texte doré animé via ProRes 4444.

### Branding : INTRO + OUTRO SIGNATURE sur chaque clip (OBLIGATOIRE)

Chaque clip de la série DOIT ouvrir par l'**intro signature 5s** et fermer par l'**outro signature 10.8s** (abonnement + disclaimer AMF). Thierry a signalé l'oubli de branding sur Clips B/C/D (2026-07-18) — c'est non-négociable pour la cohérence de marque.

| Segment | Rôle | Source |
|---|---|---|
| Intro 5s | Bumper marque (logo doré animé) | `CHANNEL/video3/clips/intro_9x16.mp4` |
| Body 45-90s | Contenu (slides + broll + voix + subs + BGM) | produit par le pipeline |
| **Outro 10.8s** | CTA "Abonne-toi →" + tagline + pills acteurs + **disclaimer AMF** (texte + voix) | `CHANNEL/branding/outro_signature/outro_signature.mp4` |

**L'outro signature est réutilisable** — il standardise le disclaimer AMF sur tous les clips. Il porte :
- Logo "L'EFFET COMPOSÉ" + pills des 4 acteurs (OVHcloud/ASML/TRUMPF/Soitec)
- CTA doré "Abonne-toi →"
- Voix HenriNeural +10% : *"Abonne-toi à L'Effet Composé. Une nouvelle enquête chaque semaine... Ce contenu est strictement informatif et ne constitue pas un conseil en investissement."*
- BGM Stellardrone -24dB

**Production de l'outro** (en cas de modif) : `CHANNEL/branding/outro_signature/gen_outro.py` (Playwright slide + edge-tts + ffmpeg Ken Burns + BGM). Script référence copiable : `scripts/gen_outro.py`.

**Règle** : les sous-titres et le BGM ne s'appliquent qu'au **body**. L'intro et l'outro sont assemblés en dernier via concat (voir section suivante). Pour les clips existants qui n'ont pas l'outro, on peut l'append a posteriori via le demuxer concat (même codec H.264/AAC, `bitstream_mp4toannexb` auto).

### ⚠️ Anti-doublon CTA "Abonne-toi" (validé 2026-07-19, clips ASML + OVHcloud D)

Quand l'outro signature porte déjà le CTA *"Abonne-toi à L'Effet Composé..."*, le **body ne doit JAMAIS** contenir lui-même une ligne "Abonne-toi" en dernière section. Sinon on entend "Abonne-toi" deux fois en séquence (body CTA → outro CTA), ce qui crée une désynchronisation perçue : la voix dit "Abonne-toi" pendant qu'on est encore sur le visuel du body, puis l'outro redit la même chose.

| Pattern body | Compatibilité outro ? |
|---|---|
| Teaser "prochain clip" / "la scorecard dans le prochain épisode" | ✅ OK (pas de CTA direct) |
| Framing analytique final ("c'est ça : infrastructure stratégique + otage géo") | ✅ OK (fin sur le sens, outro porte le CTA) |
| **"Abonne-toi pour le prochain acteur"** | ❌ **DOUBLON** — retirer cette section du body avant assemblage |

**Si un script existant contient une section `06_cta` avec "Abonne-toi"** : soit la tronquer du body (`trim` ffmpeg à la durée cumulée des sections précédentes), soit la réécrire en teaser/framing sans le mot "Abonne-toi". L'outro porte seul le CTA — c'est la signature standardisée.

**Reconstruction des clips OVHcloud (2026-07-19)** : la série originale A/B/C/D utilisait le pattern "A/B/C teasent le suivant, D clôture avec Abonne-toi". Après ajout de l'outro signature, D devient redondant → tous les 4 ont été reconstruits depuis `tmp_clips/clipX/body_final.mp4` (body PUR, sans la vieille `signature_3.5s.mp4` baked) + intro + outro signature. Durée cible reconstruite : ~60-68s.

### ⚠️ Anti-double-signature : vérifier le body source avant append

Avant d'append l'outro signature sur un clip existant, **vérifier que le body ne contient pas DÉJÀ une signature/CTA baked**. Les clips produits par `build_clips.py` (série OVHcloud V1) avaient `signature_3p5s.mp4` concaténée en fin de body via le step 6/6 du script original. Ajouter l'outro par-dessus produit 14.3s de closing (3.5 + 10.8) — redondance visuelle et audio.

**Diagnostic** : `ffprobe` le body source. Si sa durée ≈ intro + narration + 3.4s, la signature est baked. Reconstruire depuis le body pur (`tmp_clips/clipX/body_final.mp4`, AVANT le step 6/6) plutôt que de concaténer par-dessus le FINAL.

### ⚠️ Single-source-of-truth pour l'ORDER des sections (anti-drift naming)

Dans un générateur de clip (TTS + slides + segments + subs), la liste ordonnée des sections (`["01_hook","02_data1",...,"06_synthese"]`) apparaît typiquement à **3 endroits** : `build_segments()`, `concat_video_audio()`, et `gen_subs()`. Si l'une des trois drift (ex: `06_syn` dans deux endroits, `06_synthese` dans le troisième), le slide est **silencieusement skippé** à la capture (le script affiche `⚠️ manquant` mais continue) et le sous-titre de cette section se désynchronise.

**Piège réel (2026-07-19, clip portfolio)** : `gen_portfolio.py` avait un dict `VOIX` avec clé `06_syn` mais la fonction `html_synthese()` produisait `06_synthese.html`. Les 3 listes `order` utilisaient `06_syn` → le slide `06_synthese.png` existait bien mais n'était jamais référencé. Le clip a été produit sans la slide de synthèse (63s au lieu de 71s attendus).

**Règle** : définir `ORDER` comme **constante module-level unique** et dériver toute itération de cette constante. Ne jamais réécrire la liste en dur dans chaque fonction.

```python
ORDER = ["01_hook", "02_ovh", "03_asml", "04_trp", "05_soi", "06_synthese"]

def build_segments(durations):
    for key in ORDER:  # ← une seule source de vérité
        ...

def gen_subs(durations, out_path):
    for key in ORDER:
        ...
```

**Vérification** : après `capture_slides()`, asserted que chaque `ORDER[i]` a un `.png` correspondant. Un `⚠️ manquant` dans le log = bug de cohérence naming, pas un fichier absent.

### ⚠️ Vérification post-concat : durée attendue vs réelle (OBLIGATOIRE)

Après chaque concat (intro+body, body+outro, ou tout assemblage multi-segments), **vérifier la durée finale contre la somme attendue**. Un delta > 0.5s indique un problème (bitstream mal aligné, segment corrompu, double-append involontaire).

```python
expected = intro_dur + body_dur + outro_dur
actual = ffprobe_duration(out)
assert abs(expected - actual) < 0.5, f"Delta {actual-expected:.1f}s — concat suspect"
```

**Piège réel (2026-07-19)** : le premier append d'outro sur les OVHcloud a produit `clipA_with_outro.mp4` = 76.7s au lieu de 61.3s attendus (+15.3s fantômes). Le concat demuxer avait mal aligné les bitstream. La vérification post-concat aurait catché immédiatement.

### ⚠️ Assemblage final : deux méthodes selon le segment

**Cas 1 — Prépend INTRO** : utiliser `filter_complex` avec `concat=n=N:v=1:a=1`, PAS le demuxer concat. L'audio AAC de l'intro contient souvent des frames défectueuses (erreurs « NaN/+Inf », « Invalid data », exit 234) qui font échouer le demuxer. Le body en mono (TTS edge-tts) concaténé avec une intro stéréo produit aussi une corruption « 26 channels » lors du mix BGM en aval.

Chaque segment d'entrée doit être normalisé en amont :
- **SAR** : `setsar=1` obligatoire si l'intro a un SAR non-1 (sinon erreur `Input link in0:v0 parameters ... do not match`). Le clip Trumpf V2 (2026-07-19) a buté exactement là.
- **Scale/pad** : 1080×1920 + pad navy
- **fps** : unifier (24 ou 30)
- **Audio** : `aformat=channel_layouts=stereo,aresample=44100` après le concat pour normaliser mono→stereo

Pattern complet (2 segments intro+body, validé Trumpf V2) :
```
-filter_complex
"[0:v]setsar=1[v0];[1:v]setsar=1[v1];
 [v0][0:a][v1][1:a]concat=n=2:v=1:a=1[outv][outa];
 [outa]aformat=channel_layouts=stereo,aresample=44100[afix]"
-map [outv] -map [afix]
```

**Cas 2 — Append OUTRO SIGNATURE** : le demuxer concat FONCTIONNE (validé 2026-07-19, clip Trumpf v2 + outro). Le clip corps et l'outro sont tous deux H.264/AAC 1080×1920 30fps produits par le même pipeline, donc ffmpeg auto-inserte `h264_mp4toannexb` et copie proprement :
```
ffmpeg -y -f concat -safe 0 -i list.txt -c copy out.mp4
# list.txt:
# file 'clip_body.mp4'
# file '/abs/path/outro_signature.mp4'
```

Règle pratique : **`filter_complex` pour l'intro, `concat demuxer` pour l'outro.** Voir `scripts/build_clips_template.py` step 6/6 pour la version complète.

### ⚠️ Sous-titres : offset pour intro

Les sous-titres ASS/SRT doivent être **décalés** de la durée de l'intro (5.5s par défaut) pour rester synchronisés avec le body. Sans offset, les subs apparaissent pendant l'intro.

Pattern validé (`gen_subs.py`) :
```python
INTRO_DUR = 5.5  # doit matcher la durée réelle de l'intro (ffprobe)
entries.append((s + INTRO_DUR, e + INTRO_DUR, l))  # ajouter l'offset à chaque timestamp
```

Le burn-in se fait sur le fichier **final** (après concat intro+body+signature+BGM), pas sur le body seul :
```
ffmpeg -i final.mp4 -vf "ass=subs.ass" -c:v libx264 -preset medium -crf 20 ... out.mp4
```

## Workflow standard

1. **Brief** : confirmer acteur(s), angle narratif, durée cible
2. **FACT-CHECK (si source tierce)** : si le brief s'appuie sur un podcast/article externe, exécuter la passe de vérification **AVANT** de rédiger le script (voir `references/factcheck-workflow.md`). Règle absolue : **aucun chiffre issu d'un podcast n'entre dans un clip sans source externe vérifiée** — un seul chiffre faux en commentaire = crédibilité zéro. Banque de sources déjà vérifiées + chiffres corrigés : `references/sources-factcheck-bank.md` (consulter avant de relancer une recherche).
3. **Assets IA** : générer 6 variants/acteur via `grok_imagine_split.py`, faire choisir 1
4. **Script** : rédiger en respectant le guardrail AMF. Format clip 9:16 → `templates/clip_script_template.md`. Format podcast → `templates/podcast_script_template.md`.
5. **Audio** : `build_podcast.py` (podcast) ou TTS beats (clips)
6. **Visuels** : pan animé ffmpeg (pas zoompan) pour les hooks/CTA
7. **Slides HTML** : section pédagogique milieu
8. **Assemblage** : concat + BGM + sous-titres sur le **body** seul, PUIS (a) prépend intro 5s via `filter_complex` (PAS le demuxer concat, voir pièges), (b) append outro signature 10.8s via le demuxer concat (même codec, OK). Pour les clips verticaux en série, utiliser `scripts/build_clips_template.py` (généralisé : éditer le dict `CLIPS`, créer les slides HTML, lancer `python3 build_clips_template.py B C D`). **Vérification post-concat OBLIGATOIRE** : comparer durée finale vs somme attendue (delta < 0.5s).
9. **Validation AMF** : relire en vérifiant aucune formulation "conseil". Vérifier aussi l'**absence de doublon CTA** : si l'outro signature porte "Abonne-toi", le body ne doit pas contenir ce mot (voir section anti-doublon ci-dessus).
10. **Livrable** : MP4 1080×1920 ou MP3 192k

### ⚠️ Délegation subagent : ne pas déléguer un clip complet à un seul leaf

La production d'un clip complet (TTS + slides + capture Playwright + concat intro + burn-in subs + BGM + concat outro) prend **>10 min** en CPU (le burn-in ASS `preset medium crf 20` sur ~50s de 1080×1920 consomme 3-4 min à lui seul). Un subagent leaf avec timeout 10 min timeout à l'étape finale (validé 2026-07-19 : subagent ASML a fait 36 appels API, 90% du travail, puis timeout pendant le concat outro — il a fallu reprendre le render à la main).

**Règle** : soit produire le clip en session principale (les renders longs tournent en `background=true` avec `notify_on_complete`), soit découper la délégation en 2 sous-tâches : (1) subagent génère assets + body_assembled.mp4, (2) session principale fait le concat intro+outro final. Ne pas demander à un subagent leaf de produire le `.mp4` final seul.

## IA vidéo B-roll (Veo 3.1, Seedance, Kling via kie.ai)

⚠️ **Règle de classe : IA vidéo = B-ROLL UNIQUEMENT, jamais sur slides textuelles.**

kie.ai expose des modèles **text-to-video / image-to-video** avec la même clé `KIE_API_KEY` déjà configurée. Modèles pertinents pour LEC : **Veo 3.1 / Veo 3.1 Fast** (Google, photoréaliste), **Seedance 2.0 Fast** (ByteDance, cinématique — testé en production 2026-07-22), **Kling 2.5 Turbo**. La clé est active et le solde est lisible via `GET /api/v1/chat/credit` (retourne un float).

**Pourquoi B-roll uniquement** : les modèles vidéo actuels hallucinent le texte (caractères déformés, mots inventés, scorecards illisibles). La valeur ajoutée LEC (script bear, scorecard, analyse chiffrée) serait détruite si on remplaçait les slides HTML par du texte généré en vidéo. L'IA vidéo sert à remplacer les segments Ken Burns / b-roll ambiance (datacenters, GPU racks, clean rooms) — pas le contenu pédagogique.

**Séparation des pipelines** : si on expérimente, construire un pipeline **parallèle** qui ne touche pas au pipeline principal. Remplacer uniquement les b-rolls existants, jamais les slides. **Test minimal** : 3 clips Veo 3.1 Fast 1080p sur un short existant (ex: video2 CoreWeave), comparer côte à côte avant d'industrialiser. Coût : ~$0.325/clip 1080p Fast → **~$1.63 / short** (5 clips).

Catalogue complet, grille tarifaire détaillée, règle d'usage et pattern API : `references/kie-ai-video-models.md`.

## Génération musique via Kie.ai Suno API

Suno V4.5+ est accessible via la même clé `KIE_AI_API_KEY` que les images/vidéos — pas besoin de compte Suno séparé. Modèle slug : `ai-music-api/generate`. Endpoint : `createTask` + polling `recordInfo` (PAS `/api/v1/generate` qui exige un webhook).

**Coût** : 12 crédits/request (~$0.06), retourne 2 variations.

### Reference-Track Prompting (méthode validée)

Quand l'utilisateur envoie un lien YouTube comme référence de style :
1. `yt-dlp --dump-json --no-download <URL>` → extraire artiste, genre, mood
2. Traduire en champ `tags` Suno : `"modern african pop, afro-pop dance beat, <artist> style, sunny warm synths, 120 bpm"`
3. Les références tracks produisent des résultats **bien supérieurs** aux descriptions de genre abstraites

### Multi-Country Cultural Blend

Pour du contenu multi-pays, nommer des instruments spécifiques de chaque culture : makossa (Cameroun), oud (Somalie), darbuka/ney (Égypte), kalimba, highlife guitar...

### Itération

L'utilisateur peut rejeter un batch (trop ambient, trop générique). Relancer avec tags ajustés — coût marginal (~$0.06/request).

Pattern API complet, pièges (422 errors, `instrumental` vs `make_instrumental`, `resultJson` parsing), recipe reference-track : `references/kie-suno-music-api.md`

## Fichiers de référence

- `references/kie-ai-seedream-image-api.md` — API Seedream 5.0 Pro (kie.ai) : endpoints createTask/recordInfo, pattern async, quirks (timeouts, resultJson parsing), comparaison vs Grok Imagine
- `references/video-broll-assembly-recipe.md` — Variante E (vidéo B-roll IA) : scale+loop/trim clips Seedance/Veo, cache segments, optimisation CPU multi-passes, caption en HAUT, fallback image
- `references/kie-ai-video-models.md` — Catalogue modèles vidéo kie.ai (Veo 3.1, Seedance, Kling), pricing exact par mode/résolution, règle B-roll-only, pattern API async
- `references/amf-guardrail-analyste.md` — System prompt complet analyste IA "Claire" avec guardrail AMF
- `references/kie-ai-api-quirks.md` — Endpoints kie.ai, formats payload, Ken Burns sans zoompan, voix edge-tts valides
- `references/edge-tts-pronunciation.md` — Prononciation sigles FR (OVH, ASML...), map phonétique + recipe de test comparatif
- `references/xai-imagine-direct.md` — API xAI Imagine direct (`grok-imagine-image`), pricing vs kie.ai, quirks `b64_json`/model name
- `references/factcheck-workflow.md` — Passe de vérification factuelle pour sources tierces (podcasts, articles) : 4 étapes, sources autoritaires de référence, pattern de correction
- `references/sources-factcheck-bank.md` — Banque cumulative de sources vérifiées + chiffres corrigés (consulter avant toute recherche)
- `references/market-data-analysis.md` — Analyse quantitative d'actifs (BTC/ETH/indices/actions) sur données Yahoo gratuites : CAGR, Sharpe, drawdown, vol, corrélation, simulation portfolio. Réutilisable pour volet crypto ET fact-check de claims chiffrés dans les clips
- `references/antibot-scraping.md` — Récupérer du contenu sur sources finance protégées (Cloudflare IEA, etc.) via `scripts/fetch_source.py` (curl_cffi). Comparatif vs stealth-browser-mcp, limites, quand curl_cffi ne suffit pas
- `references/digitimes-paywall-workaround.md` — DigiTimes premium paywall bloquant `fetch_source.py`. Stratégie de contournement : extraire mots-clés du title/meta, enrichir via Apify `rag_web_browser` (web_search nécessite Firecrawl), scorer sur sources ouvertes complémentaires. Validé clip Trumpf 2026-07-19
- `references/clip-composite-variant-c-recipe.md` — Recipe complet Variante C (broll Grok + overlay texte) : 7 étapes, fixes cascade concat intro+body (SAR/mono/AAC), CSS composite, structure slides. Reproduire pour tout nouveau clip composite
- `references/le-point-contre-longform-recipe.md` — Recipe podcast long-form bear case LE CONTRE-POINT (16:9, 8-12 min) : positionnement éditorial, structure 7 sections, conformité AMF/MiFID II renforcée (double disclaimer), decisions design validées (mono voix, slide statique), honest gaps
- `references/groq-whisper-transcription.md` — Transcription audio rapide via API Groq `whisper-large-v3-turbo` (11s pour 10 min d'audio vs >10 min Whisper local). Pattern complet yt-dlp → split → API. Extraction de signal mineur depuis transcription. Alternatives testées et rejetées
- `references/promo-video-recipe.md` — Recipe vidéo promo client (non-finance) : structure narrative 7 scènes, TTS segmenté, visuels Seedream parallèle, assemblage ffmpeg filter_complex une passe, CTA design. Sans contraintes AMF
- `references/kie-suno-music-api.md` — API Suno via Kie.ai (modèle `ai-music-api/generate`) : endpoints, format request, pièges (422, instrumental requis), reference-track prompting via yt-dlp, multi-country cultural blend
- `templates/podcast_script_template.md` — Template script podcast 2-voix avec structure et disclaimer
- `templates/clip_script_template.md` — Template script clip vertical 9:16 (~50s) : timing par section, structure bumper/body/signature, notes production, AMF check
- `templates/gen_portfolio_template.py` — Template générateur clip portfolio multi-acteurs (N acteurs en un clip, photos Grok en bg + Ken Burns alterné). Pattern ORDER constante unique anti-drift. Validé clip portfolio L'EFFET COMPOSÉ 2026-07-19 (71.4s, 4 acteurs)
- `templates/le_contre_point_template.py` — Template générateur podcast long-form bear case LE CONTRE-POINT (16:9, ~8-12 min, mono HenriNeural +0%, 7 sections pré-structurées). Voir section "Pipeline podcast long-form bear case" + `references/le-point-contre-longform-recipe.md`
- `templates/gen_thumbnail_template.py` — Template générateur thumbnails YouTube 1280×720 long-form LE CONTRE-POINT (3 variants : minimaliste / 3-risques reco / curiosité flèche). Sélection auto du meilleur bg photo via PIL ImageStat. Voir section "Pipeline thumbnails YouTube"
- `templates/gen_thumbnail_short_template.py` — Template générateur thumbnails Shorts 9:16 (1080×1920) L'EFFET COMPOSÉ (branding distinct : topbar L'EFFET COMPOSÉ + badge CLIP X, tagline or). Mode single + mode batch (7 thumbs en ~20s). Voir section "Thumbnails Shorts 9:16"
- `templates/build_v3_video_broll.py` — Générateur montage 9:16 Variante E (vidéo B-roll IA + caption overlay). Scale 496→1080, loop/trim, cache segments, caption HAUT, subs BAS, BGM, watermark, outro. Lancer en background
- `scripts/build_podcast.py` — Générateur podcast complet (TTS 2 voix + BGM + mix)
- `scripts/build_clips_template.py` — Générateur clips verticaux 9:16 (TTS + slides Playwright + Ken Burns + subs ASS + BGM). Généralisé depuis le build OVHcloud B/C/D
- `templates/assemble_shorts_9x16.py` — Assemblage Shorts 9:16 end-to-end en un script (capture Playwright + Ken Burns + subs SRT→ASS + BGM + concat intro/body/outro). Validé video8 EU Chips juil. 2026. Plus complet que `build_clips_template.py` : gère les 3 segments (intro+body+outro) en une seule passe `filter_complex` avec normalisation SAR/fps/audio. Utiliser par défaut pour les nouveaux clips slides-only
- `scripts/grok_imagine_split.py` — Générateur 6 variants split-screen vertical
- `scripts/gen_outro.py` — Générateur outro signature réutilisable (10.8s, CTA abonnement + disclaimer AMF texte+voix). Produit `branding/outro_signature/outro_signature.mp4` à append sur chaque clip via le demuxer concat
- `scripts/score_bg_candidates.py` — Sélection objective du meilleur background parmi 6 variants Grok (PIL ImageStat : luminance + contraste). Score = `contrast - abs(lum-70)*0.5`. Affiche top 3 + verdict TOP/OK/SKIP. Lancer avant tout thumbnail batch pour pré-sélectionner les bgs

## Évolution

- Si une nouvelle voix FR edge-tts est découverte, l'ajouter à la liste des voix valides ci-dessus
- Si l'API kie.ai chat devient disponible (test `gpt-5-6-luna` via `/openai/v1/chat/completions`), automatiser la génération de script LLM avec guardrail
- Pour étendre à d'autres secteurs (crypto, immobilier coté), le guardrail AMF reste applicable — adapter seulement les sources citées

## Frontière scout vs framework macro

**Le scout log n'est pas un référentiel de cadres de pensée.** Les vidéos/podcasts de macro commentators (Raoul Pal "Everything Code", thèses liquidité/debasement, narratives macro globales) sont du **storytelling**, pas des signaux analysables. Test: "Est-ce que je peux faire un clip 9:16 avec un hook chiffré sourcé sur ce contenu?" → si NON (pas d'entreprise, pas de chiffre unique sourçable, pas d'angle clip), c'est un **framework macro**, pas un signal scout. Logger ces contenus dans le scout log le bruite et dévalue les seuils de capitalisation (≥3 GO pour podcast).

**Bonne pratique validée 2026-07-23** : si une thèse macro a de la valeur pour le podcast long-form, la référencer dans un fichier `podcast/macro_frameworks.md` (matière première intellectuelle pour Claire l'analyste IA), pas dans le scout log. Le scout reste réservé aux signaux entreprise/secteur/événement avec potentiel de clip immédiat.
