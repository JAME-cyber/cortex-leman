# Marketing Funnel — Analyser et appliquer un funnel narratif

## Problème

Les vidéos promotionnelles ont souvent une structure plate : Contenu → Prix → Outro. Cette structure informe mais n'engage pas. Les vidéos professionnelles (ex: Club Med, Airbnb) utilisent un **funnel narratif** qui guide l'émotion du spectateur de la curiosité à l'action.

## Le funnel en 4 phases (Hook → Build → Climax → CTA)

Pattern décodé d'une pub Club Med (73s, 19M vues), validé et appliqué à Culture en Saveur (juil. 2026) :

| Phase | % vidéo | Rôle | Technique |
|-------|---------|------|-----------|
| **Hook** | ~14% | Capter l'attention | Question rhétorique sur fond uni : *"Et si vos enfants..."* |
| **Build** | ~55% | Prouver la promesse | Cuts rapides (2-5s), 1 bénéfice = 1 plan = 1 mot-clé |
| **Climax** | ~14% | Créer l'émotion | Shots plus longs (3-5s), groupe/famille, bascule rationnel→émotionnel |
| **CTA** | ~17% | Convertir | VO prix + dates + lieu, sur l'outro brand (sunset/silhouettes) |

**Schéma mental :** Question → Preuve → Émotion → Invitation

## Méthode : analyser un funnel depuis une vidéo de référence

### 1. Télécharger + extraire contact sheet

```bash
yt-dlp -f "best[height<=720]" -o "/tmp/ref_analysis.mp4" \
  --extractor-args "youtube:player_client=android" "URL"

# Contact sheet (1 frame / 2s)
ffmpeg -y -i /tmp/ref_analysis.mp4 \
  -vf "fps=0.5,scale=640:480,tile=COLSxROWS" \
  -frames:v 1 -update 1 /tmp/ref_contact.jpg
```

### 2. Analyser via vision model

GLM-5.2 n'a pas de vision native → utiliser Qwen 2.5 VL 72B via OpenRouter (voir `cta-unification.md` § "Vision analysis workaround").

**Prompt d'analyse** (6 axes) :
1. Phase breakdown (timestamps exacts par phase)
2. Emotional arc (curiosité → excitement → satisfaction)
3. Editing rhythm (vitesse des cuts, variations)
4. Persuasion techniques par phase
5. Brand reveal / CTA mechanics
6. Color/lighting evolution

### 3. Adapter au projet cible

Mapper chaque phase aux assets disponibles :

```
Hook:     Question + stinger/logo          → PIL card + stinger
Build:    1 activité par clip IA (5s)      → Seedance clips existants
Climax:   Clip le plus émotionnel, plus long → dernier clip en slow-mo léger
CTA:      VO prix + sunset outro           → pas de card séparée (voir § Redondance)
```

## Architecture technique : batch funnel builder

Un seul script Python construit toutes les vidéos d'une campagne avec le même funnel. Config dict par vidéo, shared build pipeline.

```python
# Structure du config dict
VIDEOS = {
    "T1_cuisine": {
        "clips_dir": Path("assets/seedance_t1"),
        "clips": ["egypt.mp4", "cameroon.mp4", "somalia.mp4"],
        "hook_lines": [
            {"t": "Et si vos enfants"},
            {"t": "voyageaient par la"},
            {"t": "CUISINE", "hl": True},  # hl = highlight (SAFFRON)
            {"t": "cet été ?"},
        ],
        "vo": [
            ("hook_vo", "Et si vos enfants voyageaient par la cuisine cet été ?"),
            ("build_egypt", "Égypte. Le koshari, riz, lentilles et pois chiches."),
            ("build_cameroon", "Cameroun. Le ndolé, feuilles vertes et arachides."),
            ("build_somalia", "Somalie. Le canjeero, ce pain plat si moelleux."),
            ("climax_vo", "Trois pays, trois saveurs, un seul voyage."),
            ("cta_vo", "Réservez ! Du 10 au 14 août, à Petit-Lancy. 85 CHF la semaine."),
        ],
        "sub_text": {  # ASS-formatted subtitles with \N line breaks
            "hook_vo": r"Et si vos enfants\N voyageaient par la cuisine\N cet été ?",
            # ... one per VO segment
        },
    },
    # ... plus de vidéos
}
```

**Pipeline commun (par vidéo) :**
1. Générer VO (edge-tts fr-CH-ArianeNeural)
2. Stinger (3.5s) → Hook card (PIL zoom) → Build clips (slow-mo si besoin) → Climax clip → Sunset ping-pong
3. Concat vidéo
4. Audio : stinger seul (0-3.5s) → musique delayed (3.7s+) → VO delayed (3.9s+)
5. Subtitles ASS
6. Final mux + compression TG

## VO rewrite : du narratif au punchy

La VO originale (longue, descriptive) doit être **réécrite en style funnel** pour le Build :

| Avant (narratif) | Après (funnel punchy) |
|------------------|-----------------------|
| "Le mercredi, ils découvrent l'art du henné. Des motifs qui racontent des histoires, une tradition millénaire à toucher du bout des doigts." | "Henné. Des motifs qui racontent des histoires." |
| "Le vendredi, place aux rythmes du Cameroun. Tambours, musique et énergie collective." | "Tambours. L'énergie collective du Cameroun." |

**Règle : 1 mot-clé + 1 phrase courte par activité.** Le détail va dans les sous-titres.

## ⚠ Redondance CTA : ne pas doubler le pricing

**Session juil. 2026 (CES T4 funnel)** : La vidéo avait un CTA pricing card ET un sunset outro avec VO annonçant les prix. L'utilisateur a corrigé : *"Il faut enlever le dernier clip de prix car on le voit déjà précédemment"*.

**Règle :** Si la VO CTA annonce les prix verbalement sur le sunset outro, **ne pas** avoir une pricing card visuelle séparée avant. Le sunset sert de CTA visuel, la VO porte l'information tarifaire.

Exception : si la vidéo n'a pas de VO CTA (silence sur le sunset), alors une pricing card reste nécessaire.

## ⚠ Séparation audio stinger / content

**Problème** : Le stinger (3.5s) a son propre audio (jingle de marque). Si la musique et la VO démarrent à 0s, elles chevauchent le stinger → son brouillé.

**User feedback (juil. 2026)** : *"Faudrait bien séparer le son entre notre signature intro et le début des vidéos car les sons se chevauchent."*

**Fix : retards via adelay dans le filter_complex audio**

```python
# Stinger audio joue à volume plein (0-3.5s)
f"[0:a]volume=1.0[a_sting];"
# VO démarre 200ms après le stinger (respiration)
f"[1:a]volume=2.5,adelay=200|200[a_vo];"
# Musique démarre à 3.7s (après le stinger complet)
f"[2:a]volume=0.12,atrim=0:{video_dur:.1f},adelay=3700|3700,"
f"afade=t=out:st={video_dur-2.0:.1f}:d=2.0[a_mus];"
f"[a_sting][a_vo][a_mus]amix=inputs=3:duration=longest:normalize=0[aout]"
```

**Timeline audio résultante :**
- 0-3.5s : Stinger seul (jingle signature)
- 3.5-3.7s : Silence (200ms respiration)
- 3.7s+ : Musique afroswing démarre
- 3.9s+ : VO démarre (après le stinger + petit gap)

**Note :** `adelay=X|X` pour stéréo (left|right). La valeur est en millisecondes.

## ⚠ Anti-redondance : chaque build = un clip DIFFÉRENT qui matche le contenu

**User feedback (juil. 2026, 3 corrections en une session)** :
1. T3 Nil : 3× le même clip `le_nil.mp4` → *"c'est trop redondant à corriger"*. Fix : `le_nil` + `t3_nature` + `t3_ecology` (clips dédiés dans `seedance_t3_v2/`).
2. Catering : clips génériques Afrique → *"on avait d'autre clip situé à Genève pas en Afrique"*. Fix : `kiosk_chef_gva.mp4` + `kiosk_order_gva.mp4` (versions Geneva).
3. Programme : clip parents manquant → *"il manque le clip avec les parents"*. Fix : `prog_proud.mp4` (climax émotionnel).

**Règle absolue :** Avant de builder, faire l'inventaire de TOUS les clips disponibles :

```bash
find assets/ -name "*.mp4" | sort
# Pour chaque vidéo, checker les dossiers seedance_* et book_series/videos/
```

Puis mapper chaque clip au contenu VO correspondant. Si un seul clip existe pour N segments, utiliser `clip_trims` (start/mid/end) pour extraire des portions temporellement distinctes. Mais **toujours privilégier des clips différents** quand ils existent.

**Patterns de config pour gérer les cas :**

```python
# Cas 1 : clips différents par segment (standard)
"clips": ["egypt.mp4", "cameroon.mp4", "somalia.mp4"],

# Cas 2 : 1 seul clip, N segments → trim à différents timestamps
"clips": ["le_nil.mp4", "le_nil.mp4", "le_nil.mp4"],
"clip_trims": [None, "mid", "end"],  # extract start/middle/end portions

# Cas 3 : clip climax différent des build clips
"clips": ["egypt.mp4", "cameroon.mp4", "somalia.mp4", "prog_proud.mp4"],
"clips_ext": {3: BASE/"assets/seedance_programme/prog_proud.mp4"},  # index → climax
```

## ⚠ Sunset ping-pong 3-segments quand VO CTA > clip sunset

**Problème** : Le sunset clip fait 4.2s mais la VO CTA peut durer 9-10s. La vidéo coupe avant la fin de la VO.

**Fix : ping-pong en 3 segments (fwd + rev + fwd), trimé à la durée voulue.**

```python
sunset_needed = cta_vo_dur + 1.5  # VO + breathing room

# 1. Scale sunset au format
# 2. Créer version reverse
# 3. Concat: forward + reverse + forward, trim à sunset_needed
pp_list = ["sunset_scaled.mp4", "sunset_rev.mp4", "sunset_scaled.mp4"]
# 4.2 + 4.2 + 4.2 = 12.6s disponibles, trim à ~10.9s
```

**Ne pas utiliser de slow-mo sur le sunset** (factor >2 = trop visible). Le ping-pong donne un effet de respiration naturel.

## ⚠ Hook pacing : contexte AVANT question (pas d'entrée trop rapide)

**User feedback (juil. 2026, CES v5)** : *« nous entrons trop vite après sur la vidéo »*. La question d'accroche seule (*« Et si vos enfants voyageaient par la cuisine ? »*) ne suffit pas — le spectateur ignore qui parle.

**Fix : préfixer le hook VO par 1 phrase de contexte.**

```
AVANT (3.5s) : "Et si vos enfants voyageaient par la cuisine cet été ?"
APRÈS (8.2s) : "L'association Culture en Saveur propose des ateliers cuisine et découverte.
                Et si vos enfants voyageaient par la cuisine cet été ?"
```

**Règle :** Si la vidéo promeut une association/marque/organisme, le hook VO commence par qui + quoi (1 phrase) AVANT la question rhétorique. La hook card reste visuellement inchangée (titre + question), c'est la VO qui porte le contexte. Durée hook : ~8-9s (au lieu de ~3.5s), ce qui donne aussi plus de temps de lecture sur la card.

**⚠ Formulation : utiliser "vous propose" (pas "propose").** L'utilisateur a corrigé explicitement : *« à la place de 'l'atelier culture en saveurs propose...' plutôt 'l'atelier culture en saveurs vous propose...' »*. Le "vous" adresse directement le spectateur — plus engageant, moins institutionnel. Cette correction de registre s'applique à toute la VO marketing CES (et probablement à d'autres clients : toujours privilégier le tutoiement/vouvoiement direct).

**⚠ Correction de registre après feedback client (itération textuelle).** Cette session a eu 3 passes sur le hook VO en succession rapide :

1. v1 : *"Et si vos enfants voyageaient par la cuisine cet été ?"* (3.5s — trop court, pas de contexte)
2. v2 : *"L'association Culture en Saveur propose des ateliers cuisine et découverte. Et si..."* (8.2s — bon contexte, formulation impersonnelle)
3. v3 : *"L'association Culture en Saveur vous propose des ateliers cuisine et découverte. Et si..."* (8.3s — adresse directe)

**Leçon :** Les corrections textuelles du client sont quasi-gratuites (patch + re-render) mais chaque correction = un re-build complet. Regrouper les feedbacks textuels en une seule passe avant de relancer les builds (ici 3 builds séquentiels auraient pu être 1 si on avait attendu tous les retours).

## ⚠ Brand identity compliance : charte graphique sur TOUS les éléments

**User feedback (juil. 2026, CES v5)** : Les hook cards utilisaient Montserrat + fond sombre. La charte `brand_identity.md` demande Playfair Display (titres) + Poppins (corps) + fond Crème + logo + dates + contact.

**Checklist avant tout build :**

1. Lire `research/brand_identity.md` (ou équivalent) si présent
2. Hook card : fond charte (ex: Crème `#F5E8D3`), pas couleur sombre par défaut
3. Fonts : Playfair Display pour titres, Poppins pour corps/sous-titres
4. Logo : centré en haut de la hook card (PNG avec transparence)
5. Infos pratiques : dates + lieu + contact (email, tél, social) visibles sur la hook card
6. Tagline brand en bas (ex: *« DÉCOUVRIR · INSPIRER · TRANSMETTRE »*)
7. Sous-titres ASS : changer Fontname dans le Style pour matcher (ex: `Poppins SemiBold`)

**⚠ Validation fonts (pitfall récurrent) :** Les variants d'une même police peuvent être corrompus (download raté = fichier HTML au lieu de TTF). Toujours valider :

```bash
cd assets/fonts && for f in *.ttf; do echo -n "$f: "; file "$f" | cut -d: -f2; done
```

Si un variant est corrompu (ex: `PlayfairDisplay-Bold.ttf` = HTML), fallback vers le variant Variable (`PlayfairDisplay-Variable.ttf`) qui contient toutes les graisses.

**⚠ PIL API (Pillow ≥ 9.1) :** `Image.LANCZOS` est déprécié → `Image.Resampling.LANCZOS`. Idem pour `ANTIALIAS`. Les anciens scripts qui utilisent `Image.LANCZOS` plantent silencieusement ou au runtime.

## Résultats mesurés (CES v5_funnel, juil. 2026 — avec brand identity + hook context)

4 vidéos avec charte complète (logo, Playfair, Poppins, dates, contact) + hook contextué :

| Vidéo | Durée | Hook | Taille TG |
|-------|-------|------|-----------|
| T1 Cuisine | 45.9s | 8.7s | 5.2MB |
| T2 Visio | 46.1s | 8.8s | 5.3MB |
| T4 Traditions | 50.0s | 8.5s | 7.1MB |
| Programme | 45.4s | 9.1s | 6.2MB |

Toutes 45-50s (vs 35-45s v4), hook ~8-9s (vs ~3.5s v4) grâce au contexte asso. Scripts : `build_funnel_all.py` + `build_t4_funnel.py`.

## ⚠ Récupération d'anciens clips : ne pas toujours remplacer par du neuf

**User feedback (juil. 2026, CES T1)** : *« Pour la vidéo première vidéo le clip de la crêpe de somalie nous avions un bon clip »*. Le clip Phase 3 (nouveau, généré) avait remplacé l'ancien clip Somalie. L'utilisateur a préféré l'ancien (`seedance_t1_v2/t1_somalia.mp4`).

**Règle :** Les nouveaux clips générés ne sont pas automatiquement meilleurs que les clips existants validés par le client. Avant de remplacer un clip approuvé :

1. Inventorier les versions existantes : `find assets/ -name "*somalia*" -name "*.mp4"`
2. Conserver les clips approuvés par défaut (sauf instruction explicite de remplacement)
3. Les nouveaux clips vont dans un dossier séparé (`phase3/integrated/`) — le remplacement n'est pas automatique

**⚠ Correction de registre : "vous propose" (pas "propose")**

**User feedback (juil. 2026, CES v6)** : *« à la place de 'l'atelier culture en saveurs propose...' plutôt 'l'atelier culture en saveurs vous propose...' »*.

Le "vous" adresse directement le spectateur — plus engageant, moins institutionnel. Correction appliquée sur les 6 vidéos en `replace_all=true` sur les 2 scripts (`build_funnel_all.py` + `build_t4_funnel.py`).

## ⚠ draw_bg(draw) écrase le fond charte — HOOK CARDS UNIQUES vs build_funnel_all

**Pitfall (juil. 2026, CES T4)** : Le script `build_t4_funnel.py` appelait `draw_bg(draw)` APRÈS `Image.new('RGB', (W, H), CREAM)`. Cette fonction repeint le fond pixel par pixel en couleur sombre `(38, 30, 27)`, **écrasant complètement** le fond crème de la charte. La hook card T4 avait donc un fond sombre au lieu du crème.

**Fix :** Dans `build_t4_funnel.py`, retirer l'appel `draw_bg(draw)` de la hook card. La fonction `draw_bg` est un vestige du design pre-charte (fond sombre Montserrat). `build_funnel_all.py` ne l'appelle pas — `build_t4_funnel.py` oui, car il a été construit séparément.

**Règle générale :** Quand deux scripts de build co-existent (`build_funnel_all.py` + `build_t4_funnel.py`), appliquer la charte sur les DEUX. Ne pas supposer que les corrections sur l'un se propagent à l'autre.

## ⚠ ASS Fontname : utiliser le nom de famille, pas le nom du variant

**Pitfall (juil. 2026, CES T4)** : Les sous-titres ASS de `build_t4_funnel.py` utilisaient `Fontname: Poppins SemiBold`. ffmpeg/libass n'a pas pu résoudre ce nom correctement — il fallait le nom de famille générique `Poppins` avec le flag `Bold=-1` dans le Style.

**Fix :**
```diff
- Style: Default,Poppins SemiBold,38,...
+ Style: Default,Poppins,38,...,-1,0,0,0,...
```

Le flag `Bold=-1` (le 8e champ après Fontname) active le gras. `Poppins SemiBold` comme Fontname peut échouer silencieusement — le sous-titre s'affiche dans une police fallback (sans-serif générique), ce qui ne saute pas aux yeux immédiatement mais casse la charte typographique.

**Validation :**
```bash
fc-list | grep -i "poppins"
# Doit afficher: "Poppins:style=Regular", "Poppins:style=Bold", etc.
# Si "Poppins SemiBold" apparaît comme nom alternatif, c'est OK mais
# ne pas l'utiliser comme Fontname ASS — utiliser "Poppins" + Bold=-1.
```

**Règle :** Pour les sous-titres ASS, toujours utiliser le nom de famille de police (`Poppins`, `Playfair Display`) + flags Bold/Italic dans le Style. Ne jamais mettre un nom de variant (`Poppins SemiBold`, `Playfair Display Bold`) comme Fontname.

## ⚠ Régénération de clips sur feedback client : workflow éprouvé

**Séquence validée (juil. 2026, CES T1 Somalie + T4 Tambours)** :

1. **Vérifier le solde kie.ai** : `GET /api/v1/chat/credit`
2. **Créer un script dédié** (`gen_somalia_v3.py`, `gen_tambours_v2.py`) avec le prompt modifié
3. **Submit + poll via `recordInfo`** (endpoint correct, `state` field pas `status`)
4. **Télécharger directement** depuis `resultUrls[0]` (fonctionne sans l'API download-url)
5. **Backup l'ancien clip** (`t1_somalia_v2_backup.mp4`) avant remplacement
6. **Valider visuellement** avec le client (envoyer le clip brut `/tmp/xxx_raw.mp4`)
7. **Rebuild la vidéo** seulement après validation client

**Coût typique par clip régénéré : 205cr (Seedance 2.0, 720p, 5s).**

**Ne JAMAIS rebuilder la vidéo complète avant validation visuelle du clip brut.** Le client peut vouloir une 3e itération (ex: cette session — Somalie v1 → v2 → v3 → v4, 3 générations × 205cr = 615cr). Chaque génération est une passe séparée.

## ⚠ Migration de scripts standalone vers le master funnel builder

**Scénario récurrent** : Les premières vidéos d'une campagne sont construites avec des scripts standalone (`build_teaser_clean.py`, `build_t1_v2.py`, etc.) qui ont leur propre intro, VO voice, musique, et structure. Quand la campagne évolue vers un funnel builder unifié (`build_funnel_all.py`), ces vidéos legacy accumulent de la dette technique : voix différentes, stingers manquants, formats audio incohérents.

**Session août 2026 (CES Teaser)** : L'utilisateur a demandé de remplacer l'intro du Teaser par le nouveau (avec stinger), la nouvelle musique et la VO. Le Teaser utilisait `fr-FR-DeniseNeural` (ancienne voix aiguë), `intro_steam_spice.mp4` (intro custom), et `ces_v2_main.mp3` sans stinger audio. Les autres vidéos (T1-T4, Programme) utilisaient le funnel builder avec stinger + VO `fr-CH-ArianeNeural` + audio stinger séparé.

**Fix : ajouter une config entry au master builder plutôt que patcher le script standalone.**

```python
# AVANT : 5+ scripts standalone avec pipelines divergents
scripts/build_teaser_clean.py    # DeniseNeural, intro_steam, ces_v2_main
scripts/build_t1_v2.py           # HenriNeural, autre intro
scripts/build_funnel_all.py      # ArianeNeural, stinger, funnel ← LE STANDARD

# APRÈS : tout dans build_funnel_all.py
VIDEOS = {
    "T1_cuisine": { ... },  # déjà là
    "T2_visio": { ... },    # déjà là
    # ...
    "teaser": {             # ← NOUVELLE ENTRY
        "clips_dir": BASE / "assets",
        "clips": ["seedance_new/v1_00.mp4", "seedance_new/v1_01.mp4", "seedance_catering/catering_hero.mp4"],
        "hook_lines": [{"t": "Et si vos enfants"}, {"t": "découvraient"}, {"t": "L'AFRIQUE", "hl": True}, {"t": "cet été ?"}],
        "vo": [
            ("hook_vo", "L'association Culture en Saveur vous propose..."),
            ("build_1", "..."), ("build_2", "..."), ("build_3", "..."),
            ("climax_vo", "..."), ("cta_vo", "..."),
        ],
        "sub_text": { ... },
    },
}
# Lancer : python3 scripts/build_funnel_all.py teaser
```

**Avantages de la migration vers le master builder :**
- Hérite automatiquement : stinger, VO voice standard (ArianeNeural), musique, séparation audio stinger/content, sous-titres ASS, hook card brand-compliant, sunset CTA
- Cohérence garantie avec le reste de la campagne (même voix, même stinger, même timing audio)
- Un seul script à maintenir pour toute la campagne

**Quand NE PAS migrer :**
- La vidéo a une structure fondamentalement différente (ex: long-form 16:9, pas de funnel)
- La vidéo utilise des assets incompatibles avec le funnel builder (ex: pas de clips, images fixes uniquement)
- La migration casserait du contenu validé par le client (ex: intro custom approuvée)

**Checklist de migration :**
1. Inventorier les assets utilisés par le script standalone (`grep -E "\.mp4|\.mp3|\.png" scripts/build_old.py`)
2. Mapper chaque asset vers le config dict du master builder
3. Vérifier que le nombre de clips ≥ nombre de build segments VO
4. Si clips < segments, utiliser `clip_trims` (start/mid/end) ou réduire les segments VO
5. Builder via `python3 scripts/build_funnel_all.py <video_id>`
6. Valider durée (la migration peut changer la durée — le funnel ajoute stinger 3.5s + hook ~8s + sunset ~8s)

## ⚠ Migration : préserver TOUS les clips de la version originale

**Session août 2026 (CES Teaser)** : Lors de la migration du Teaser de `build_teaser_clean.py` vers le master funnel builder, seulement 3 clips ont été migrés sur les ~8 originaux. L'utilisateur a corrigé : *« Non il manque des clips »*. Les clips oubliés : cooking Égypte/Cameroun/Somalie, 3 posters papercraft (pays), catering hero.

**Cause racine :** Le script standalone utilisait une structure narrative différente (séquence libre de clips) sans mapping 1:1 avec les segments VO du funnel builder. En copiant seulement les 3 premiers clips de la liste, tout le contenu mid-video a été perdu.

**Règle : Avant toute migration, faire l'inventaire COMPLET des clips de la version originale.**

```bash
# 1. Extraire TOUS les clips référencés dans l'ancien script
grep -oP "['\"][^'\"]*\.(?:mp4|png)['\"]" scripts/build_teaser_clean.py | sort -u

# 2. Lister tous les clips disponibles dans les dossiers assets
find assets/ -name "*.mp4" | sort
find renders/ -name "*.mp4" | sort

# 3. Construire un mapping table : chaque clip original → position dans le funnel
```

**Checklist de migration (complémentaire à la checklist existante) :**
1. Compter les clips dans l'original vs la nouvelle config → doivent matcher
2. Si l'original a des éléments non-clip (posters papercraft en .png → les pré-rendrer en .mp4 avec zoompan avant de les câbler)
3. Pré-rendre les assets statiques : `ffmpeg -loop 1 -i poster.png -t 2.5 -vf "zoompan=...,drawtext=..."` → clip utilisable dans le funnel
4. Valider avec l'utilisateur AVANT de rebuilder que tous les clips sont présents dans la config

**Pitfall :** Les scripts standalone peuvent référencer des clips via des boucles ou des listes dynamiques. Faire une exécution sèche (`python3 -c "import ast; ..."`) ou lire le script en entier pour ne rien rater.

## ⚠ Couverture exhaustive des aspects de l'événement (quality gate)

**Session août 2026 (CES Teaser, 2 corrections en une session)** : L'utilisateur a signalé des clips manquants à DEUX reprises :
1. *« Non il manque des clips »* → cooking Égypte/Cameroun/Somalie + 3 posters papercraft + catering oubliés lors de la migration
2. *« on a oublié un clip celui des activités »* → clips henné + tambours (`assets/seedance_t4/`) oubliés

**Cause racine :** Le teaser promo doit couvrir TOUS les aspects de l'événement, pas seulement la cuisine. Les aspects sont : cuisine (par pays), activités/traditions (henné, tambours, contes), catering, visioconférence orphelinat.

**Quality gate : vérifier la couverture par aspect avant tout build de teaser/promo.**

```bash
# Inventaire par catégorie de contenu
echo "=== CUISINE ===" && find assets/ -name "*cuisine*" -o -name "*cook*" | grep "\.mp4$"
echo "=== ACTIVITÉS ===" && find assets/ -name "*henn*" -o -name "*tambour*" -o -name "*conte*" -o -name "*music*" | grep "\.mp4$"
echo "=== CATERING ===" && find assets/ -name "*cater*" | grep "\.mp4$"
echo "=== VISIO ===" && find assets/ -name "*visio*" -o -name "*orphelinat*" | grep "\.mp4$"
echo "=== POSTERS ===" && find assets/ renders/ -name "*poster*" | grep -E "\.(png|mp4)$"
```

Chaque aspect doit avoir ≥1 clip dans la config. Si un aspect n'a pas de clip, demander à l'utilisateur avant de builder (ne pas assumer que c'est volontaire).

## ⚠ Pre-render d'images statiques (PNG → MP4 avec zoompan) pour le funnel builder

**Technique (août 2026, CES Teaser)** : Les posters papercraft (.png) doivent être convertis en clips vidéo pour être utilisables dans le funnel builder. Le pattern ffmpeg :

```bash
ffmpeg -y -loop 1 -i "poster_egypte.png" -t 2.5 \
  -vf "scale=1440:2560:force_original_aspect_ratio=increase,crop=1440:2560,\
zoompan=z='min(zoom+0.001,1.08)':d=75:s=720x1280:fps=30,\
drawtext=fontfile='PlayfairDisplay-Variable.ttf':text='ÉGYPTE':fontsize=56:fontcolor=0xF5E8D3:x=(w-text_w)/2:y=h*0.12:borderw=3:bordercolor=0x000000,\
drawtext=fontfile='Poppins-Regular.ttf':text='Hawawshi · Falafel':fontsize=30:fontcolor=0xD88A22:x=(w-text_w)/2:y=h*0.85:borderw=2:bordercolor=0x000000" \
  -c:v libx264 -crf 20 -pix_fmt yuv420p -r 30 -an "poster_egypte.mp4"
```

**Points clés :**
- `d=75` = durée en frames (75 frames @ 30fps = 2.5s)
- `zoompan z='min(zoom+0.001,1.08)'` = zoom progressif très léger (1.0→1.08 sur 2.5s)
- `scale` avant `crop` : upscale puis crop au format exact (1440:2560 → crop 720x1280)
- `drawtext` x2 : nom du pays (Playfair, grand) + plats emblématiques (Poppins, petit, ocre)
- Colors en hex `0xRRGGBB` (sans alpha), pas `#RRGGBB`
- Output `-an` (pas d'audio — le funnel builder ajoute l'audio)

**Stocker les pre-renders dans `renders/<video_id>/`** pour ne pas polluer `assets/`.

## ⚠ `clips_dir: BASE` pour builds multi-répertoires

**Pattern (août 2026, CES Teaser)** : Quand une vidéo combine des clips de plusieurs dossiers (`assets/seedance_new/`, `assets/book_series/videos/`, `renders/teaser_funnel/`, `assets/seedance_t4/`, `assets/seedance_catering/`), définir `clips_dir` au niveau du projet et utiliser des chemins relatifs complets :

```python
"teaser": {
    "clips_dir": BASE,  # ← pas BASE / "assets"
    "clips": [
        "assets/seedance_new/v1_00.mp4",              # sous-dossier 1
        "assets/book_series/videos/cuisine_egypt.mp4", # sous-dossier 2
        "renders/teaser_funnel/poster_egypte.mp4",     # renders (pre-rendered PNG)
        "assets/seedance_t4/t4_henna_children.mp4",    # sous-dossier 3 (activités)
        "assets/seedance_catering/catering_hero.mp4",  # sous-dossier 4
    ],
},
```

**Règle :** Si >2 dossiers source, `clips_dir: BASE` + chemins relatifs complets. Si 1 dossier, `clips_dir: BASE / "subdir"` + noms de fichiers seuls.

## ⚄ Ajout d'un clip au config-dict builder : 4 points synchronisés

**Complément à la section "5 points" ci-dessus** (qui s'applique à `build_t4_funnel.py`). Pour `build_funnel_all.py` (config dict), l'ajout est plus simple — **4 points** :

1. **`clips[]`** — Ajouter le chemin du clip
2. **`clip_trims[]`** — Ajouter le trim (`"start"`, `"mid"`, `None`) aligné avec `clips[]`
3. **`vo[]`** — Ajouter le tuple `("build_N", "texte VO...")`
4. **`sub_text{}`** — Ajouter l'entrée `"build_N": r"texte\Nsous-titre"`

```python
# AVANT (8 clips, build_1 à build_7 + climax)
"clips": [..., "catering_hero.mp4"],
"clip_trims": [..., "mid"],
"vo": [..., ("build_7", "Trois pays..."), ("climax_vo", "...")],
"sub_text": {..., "build_7": "...", "climax_vo": "..."},

# APRÈS (10 clips, ajout activités avant catering)
"clips": [..., "t4_henna_children.mp4", "t4_tambours.mp4", "catering_hero.mp4"],
"clip_trims": [..., "start", "start", "mid"],
"vo": [
    ..., 
    ("build_7", "Trois pays, mille saveurs, une seule aventure."),
    ("build_8", "Mais aussi le henné, les contes et les tambours."),   # ← NOUVEAU
    ("build_9", "Des activités manuelles et créatives, pour chaque enfant."),  # ← NOUVEAU
    ("climax_vo", "Et même le street food, préparé avec passion par nos chefs."),
],
"sub_text": {
    ...,
    "build_8": r"Le henné, les contes\N les tambours",       # ← NOUVEAU
    "build_9": r"Des activités créatives\N pour chaque enfant",  # ← NOUVEAU
    "climax_vo": r"Street food\N préparé avec passion",
},
```

**Validation :** Le nombre d'entrées dans `clips[]` doit matcher le nombre d'entrées dans `clip_trims[]`, et le nombre de segments `build_N` dans `vo[]` doit matcher les entrées `build_N` dans `sub_text{}`.

## ⚠ Synchronisation VO ↔ clips : 1 segment VO = 1 clip sémantiquement cohérent

**Session août 2026 (CES Teaser)** : Après migration des clips manquants, la VO était désynchronisée du visuel. La VO disait *« L'Égypte. Le Cameroun. La Somalie. »* pendant qu'un seul clip de cuisine égyptienne défilait. Puis *« Street food africain »* pendant la cuisine somalienne. L'utilisateur a corrigé : *« J'ai l'impression que le texte n'est pas synchronisé avec les clips »*.

**Cause racine :** Les segments VO décrivaient 3 pays en une seule phrase, mais chaque pays a son propre clip de cuisine + son poster papercraft. Le contenu visuel et le contenu vocal ne racontaient pas la même histoire au même moment.

**Règle absolue : Chaque segment VO doit décrire ce qui est VISIBLE à l'écran à ce moment précis.**

| ❌ MAUVAIS (désynchronisé) | ✅ BON (synchro 1:1) |
|---|---|
| Clip: Égypte cooking | Clip: Égypte cooking |
| VO: "L'Égypte. Le Cameroun. La Somalie." | VO: "L'Égypte. Le pays des pharaons." |

**Méthode de vérification de synchronisation :**

```
Pour chaque segment i de la timeline :
  1. Quel clip est affiché pendant ce segment ?
  2. Que dit la VO pendant ce segment ?
  3. Le contenu visuel correspond-il au contenu vocal ?
     → Si non : restructurer les VO ou réordonner les clips
```

**Quand restructurer les VO pour matcher les clips :**

```python
# Pattern : alterner clip cooking + clip poster par pays
"clips": [
    "cooking_closeup.mp4",       # build_1: "La cuisine, mains dans la pâte"
    "cuisine_egypt.mp4",         # build_2: "L'Égypte, le pays des pharaons"
    "poster_egypte.mp4",         # build_3: "Des saveurs qui voyagent"
    "cuisine_cameroon.mp4",      # build_4: "Le Cameroun, le ndolé et les beignets"
    "poster_cameroun.mp4",       # build_5: "Les couleurs de l'Afrique centrale"
    "cuisine_somalia.mp4",       # build_6: "La Somalie, le canjeero"
    "poster_somalie.mp4",        # build_7: "Trois pays, mille saveurs"
    "catering_hero.mp4",         # climax: "Street food préparé avec passion"
],
```

**Contrainte temporelle :** Le clip doit toujours être ≥ à la durée de sa VO. Si VO > clip, le builder applique du slow-mo (jusqu'à un facteur visible ~1.5x). Au-delà, ajouter du matériel ou raccourcir la VO.

**Validation post-build :** Toujours vérifier la timeline de build (le script affiche les durées par segment). Si une VO parle d'un pays X pendant un clip de pays Y, la synchro est cassée.

## ⚠ Feedback client = AUDIT AVANT ACTION (pas de rebuild aveugle)

**Session août 2026 (CES feedback Linda v2)** : Face à un retour client massif (12 points de feedback sur 10 vidéos), le premier réflexe a été de tout re-builder. L'utilisateur a corrigé : *« Souvent c'est juste un clip à changer pas toute la video »* et *« vérifier ce qui est déjà fait »*.

**Cause racine :** Le feedback client liste TOUT, y compris ce qui a déjà été corrigé dans des sessions précédentes. Ne pas filtrer = travail redondant + frustration utilisateur.

**Règle absolue : AVANT de toucher au code, faire un audit d'état.**

```bash
# 1. Textes déjà corrigés ?
grep -r "Petit-Lancy" scripts/build_funnel_all.py | grep -c "au Petit-Lancy"  # vs "à Petit-Lancy"

# 2. Musique déjà changée ?
grep -r "afroswing\|ces_v2_main" scripts/build_funnel_all.py

# 3. Clips déjà régénérés ? (check timestamps)
ls -lt assets/seedance_*/  | head -20

# 4. Sortie déjà rebuildée ?
ls -lt output/v4_funnel/*.mp4

# 5. Quels clips existent par catégorie ?
echo "=== CUISINE ===" && find assets -name "*cuisine*" -name "*.mp4" | sort
echo "=== ACTIVITÉS ===" && find assets -name "*henn*" -o -name "*tambour*" -o -name "*conte*" | grep ".mp4"
```

Puis trier le feedback en 3 buckets :

| Bucket | Action | Exemple |
|--------|--------|---------|
| ✅ **Déjà fait** | Ignorer (informer l'utilisateur) | "au Petit-Lancy", musique, V4 supprimée |
| 🔧 **Code seul** | Patch config + rebuild | Supprimer clip en loop, fusionner vidéos, raccourcir segment |
| 🎬 **Nouveau clip requis** | Écrire prompt + générer via kie.ai | Refaire visio, henné, contes avec nouveaux critères |

**Ne jamais rebuilder une vidéo complète pour un changement d'un seul clip.** Le config dict permet de changer 1 entrée dans `clips[]` + `vo[]` + `sub_text{}` et relancer le build ciblé.

## ⚠ Correction chirurgicale : 1 clip à la fois

**Session août 2026 (CES feedback Linda v2)** : L'utilisateur a explicitement corrigé l'approche *« Souvent c'est juste un clip à changer pas toute la video »*.

**Méthode chirurgicale :**

1. Identifier EXACTEMENT quel clip pose problème (par vidéo, par timestamp)
2. Chercher un clip de remplacement EXISTANT avant d'en générer un nouveau
3. Patcher 1 entrée dans le config dict
4. Rebuilder UNE vidéo : `python3 scripts/build_funnel_all.py <video_id>`
5. Valider avec l'utilisateur avant de passer au clip suivant

**Ne pas :**
- Rebuilder toutes les vidéos d'un coup
- Réécrire toute la VO quand seul 1 segment change
- Régénérer des clips qui existent déjà en valide

**Pattern de réutilisation :** Les clips validés dans le teaser (V1) peuvent être réutilisés dans d'autres vidéos. Le teaser est la "bibliothèque canonique" des clips approuvés.

## ⚠ Détection de clips en double (loop invisible)

**Session août 2026 (CES T2 Visio)** : T2 utilisait le MÊME clip deux fois (`scene_2_visio_cameroon_orphanage_video_c.mp4` en position 1 ET 2 avec trims différents). Résultat : loop visible, l'utilisateur a signalé *« on a un clip en loop »*.

**Détection automatique avant build :**

```bash
# Vérifier les doublons dans la config
python3 -c "
import ast, sys
with open('scripts/build_funnel_all.py') as f:
    tree = ast.parse(f.read())
# Chercher les listes 'clips' et vérifier les doublons
"
```

Ou plus simple — vérifier visuellement la config :

```python
clips = ["a.mp4", "a.mp4", "b.mp4"]  # ← DOUBLON détecté
assert len(clips) == len(set(clips)), f"Duplicate clips: {[c for c in clips if clips.count(c)>1]}"
```

**Règle :** Si un clip doit apparaître 2 fois (volontaire, ex: trim start vs end), le documenter explicitement dans le commentaire. Sinon, chaque entrée de `clips[]` doit pointer vers un clip DIFFÉRENT.

## ⚠ Fusion de vidéos : merger N configs en une seule

**Session août 2026 (CES feedback Linda)** : Linda a demandé de fusionner T2 (visio) + T3 (Nil) en une seule vidéo "activités". Plutôt que de supprimer les configs T2 et T3, créer une NOUVELLE config qui combine les meilleurs clips des deux.

**Pattern de fusion :**

```python
# AVANT : 2 vidéos séparées
"T2_visio": { "clips": ["visio_classroom", "inclusion_cooking", "visio_boy"] },
"T3_nil": { "clips": ["le_nil", "t3_nature", "t3_ecology"] },

# APRÈS : 1 vidéo fusionnée
"activites": {
    "clips": [
        "visio_classroom",      # de T2
        "inclusion_cooking",    # de T2
        "le_nil",              # de T3 (meilleur clip seulement)
        "t4_henna_children",   # de T4 (ajout)
        "t4_tambours",         # de T4 (ajout)
        "t4_rhone",            # de T4 (ajout)
        "t4_contes",           # de T4 (ajout)
    ],
    # VO adaptée : 1 segment par activité
    "vo": [
        ("hook_vo", "Bien plus que de la cuisine..."),
        ("build_visio", "Visioconférence..."),
        ("build_inclusion", "Inclusion..."),
        ("build_nil", "Le Nil..."),
        # ... un build_N par clip
    ],
},
```

**Règles de fusion :**
1. Garder les configs originales (T2, T3) — ne pas les supprimer, au cas où le client change d'avis
2. Sélectionner le MEILLEUR clip par activité (pas tous les clips)
3. Réécrire la VO pour la nouvelle structure (1 segment = 1 activité)
4. L'ordre des clips suit une logique narrative : interactif (visio) → découverte (Nil) → créatif (henné/musique) → nature (Rhône) → culture (contes)

## ⚠ Ajout d'un clip à un build existant : 5 points de modification synchronisés

**Scenario (juil. 2026, CES T4)** : Le client signale qu'un clip manque (*« on avait aussi un clip le thé aux épices qui manque ici »*). Un clip existait déjà (`scene_4_storytelling_somali_tales_clip2.mp4`) mais n'était pas câblé dans le build.

**5 points à modifier dans le build script quand on ajoute un segment :**

1. **`build_configs`** — Ajouter le tuple `(name, clip_path, vo_name)`
2. **`VO_SEGMENTS`** — Ajouter le tuple `("build_contes2", "Thé aux épices...")`
3. **`SUB_TEXT`** — Ajouter l'entrée `"build_contes2": r"Thé aux épices\N regards émerveillés"`
4. **`vo_order`** (liste audio) — Ajouter `"build_contes2"` à la bonne position
5. **Timing loop** — Ajouter `"build_contes2"` à la liste `for vo_name in [...]`

**Pitfall : oublier un seul point casse la timeline.** Si `vo_order` ou la timing loop n'est pas mise à jour, la VO et les sous-titres se désynchronisent silencieusement (le clip vidéo apparaît mais sans audio ni sous-titre).

**Règle :** Faire un `search_files` pour le nom du nouveau segment dans le script avant de rebuilder pour vérifier qu'il apparaît bien 5 fois (build_configs + VO_SEGMENTS + SUB_TEXT + vo_order + timing loop).

**Inventaire des clips disponibles avant ajout :** Toujours faire `find assets/ -name "*.mp4" | sort` pour découvrir les clips existants non câblés (ex: `clip1` + `clip2` d'une même scène Phase 3, où seul `clip1` était utilisé).

## ⚠ Suppression/réduction de segments : 4 points synchronisés (inverse de l'ajout)

**Session août 2026 (CES Catering)** : L'utilisateur a demandé de réduire le kiosque catering de 4 plats à 3 (supprimer les Frites). Un seul changement de contenu, mais 4 zones du script doivent rester cohérentes.

**Les 4 points à modifier (script standalone type `build_catering_v3.py`) :**

1. **`VO_SEGMENTS[]`** — Retirer le tuple du segment supprimé (ex: `("cat_v3_01", "Au kiosk...")`)
2. **`SUB_TEXT{}`** — Retirer la clé correspondante (`"cat_v3_01": r"..."`)
3. **`segments[]` (timeline)** — Retirer l'entrée ET re-mapper les références `durations["cat_v3_XX"]` des segments restants (les clés doivent pointer vers des VO existantes)
4. **Data arrays** (`plats[]`, `clips[]`, etc.) — Retirer l'entrée de données visuelles (ex: Frites)

**Pitfall : les clés `durations["..."]` référencent les noms dans `VO_SEGMENTS`.** Quand on retire `cat_v3_01` de `VO_SEGMENTS`, `durations["cat_v3_01"]` n'existe plus → `KeyError` silencieux ou timeline cassée. Les segments restants qui référençaient `cat_v3_01` doivent être re-mappés vers une clé existante.

```python
# AVANT (4 plats, 4 segments VO cat_v3_00 à cat_v3_03)
segments = [
    ("menu_00", durations["cat_v3_00"] + BUFFER, "menu"),
    ("menu_01", durations["cat_v3_01"] + BUFFER, "menu"),  # ← supprimé
    ("menu_02", durations["cat_v3_02"] + BUFFER, "menu"),
    ("menu_03", durations["cat_v3_03"] + BUFFER, "menu"),  # ← re-mappé vers cat_v3_02
]

# APRÈS (3 plats, 3 segments VO cat_v3_00, cat_v3_02, cat_v3_03)
segments = [
    ("menu_00", durations["cat_v3_00"] + BUFFER, "menu"),
    ("menu_01", durations["cat_v3_02"] + BUFFER, "menu"),  # ← re-mappé
    ("menu_02", durations["cat_v3_03"] + BUFFER, "menu"),  # ← re-mappé
]
```

**Règle :** La timeline `segments[]` référence `durations["key"]` qui provient du `ffprobe` des fichiers VO générés depuis `VO_SEGMENTS`. Le chaînage est : `VO_SEGMENTS` → `gen_vo()` → `durations{}` → `segments[]` → concat vidéo + subtitles. Casser un maillon = désynchronisation.

**Validation post-patch :** Après les modifications, vérifier que chaque clé référencée dans `segments[]` existe dans `durations{}` (donc dans `VO_SEGMENTS`). Un simple `grep -oP 'durations\["\K[^"]+' build_script.py | sort -u` doit matcher exactement les clés de `VO_SEGMENTS`.

**⚠ Pitfall : cascade d'indices hardcoded après suppression de segment (6 points, pas 4).** La suppression d'un segment décale toute la liste `segments[]`. Tout index codé en dur doit être mis à jour. Session août 2026 (CES Catering, 4→3 plats) : 2 build failures avant de tous les attraper.

Les 6 points à synchroniser (les 4 originaux + 2 nouveaux) :

1. **`VO_SEGMENTS[]`** — retirer le tuple
2. **`SUB_TEXT{}`** — retirer la clé
3. **`segments[]` (timeline)** — retirer l'entrée ET re-mapper les `durations["cat_v3_XX"]`
4. **Data arrays** (`plats[]`) — retirer l'entrée visuelle
5. **⭐ Slice ranges dans les loops** — `segments[4:8]` devient `segments[4:7]` (la fin du slice doit exclure le CTA qui a maintenant un index plus bas)
6. **⭐ Références d'index fixes** — `segments[8][1]` pour le CTA devient `segments[7][1]` (l'index décale de 1 pour chaque segment retiré)

```python
# AVANT (8 segments, indices 0-7, CTA à index 8)
segments = [
    ("intro", ...),      # [0]
    ("steam", ...),      # [1]
    ("kiosk_chef", ...), # [2]
    ("kiosk_order", ...),# [3]
    ("menu_00", ...),    # [4]
    ("menu_01", ...),    # [5]  ← SUPPRIMÉ
    ("menu_02", ...),    # [6]  ← devient [5]
    ("cta", ...),        # [7]  ← devient [6]... MAIS attendu à [8] ailleurs
]

# APRÈS (7 segments, indices 0-6, CTA à index 7)
# Code cassé si non mis à jour :
for i, ... in enumerate(segments[4:8]):  # ❌ IndexError (8 n'existe plus)
seg_cta = prep_image_zoom("cta", ..., segments[8][1])  # ❌ IndexError

# Code corrigé :
for i, ... in enumerate(segments[4:7]):  # ✅
seg_cta = prep_image_zoom("cta", ..., segments[7][1])  # ✅
```

**Règle : Après toute suppression de segment, faire un `grep -n "segments\[" build_script.py` et vérifier que CHAQUE index hardcoded pointe vers le bon segment post-suppression.** Les slices `segments[N:M]` sont particulièrement piégeux car le `M` doit aussi être décrémenté.

**Alternative robuste : éviter les indices hardcoded.** Utiliser des lookups par nom au lieu d'index :

```python
# FRAGILE (indices hardcoded)
seg_cta = prep_image_zoom("cta", ..., segments[8][1])

# ROBUSTE (lookup par nom)
cta_seg = next(s for s in segments if s[0] == "cta")
seg_cta = prep_image_zoom("cta", ..., cta_seg[1])
```

## ⚠ Vérifier l'identité d'un clip AVANT suppression (anti-méprise)

**Session août 2026 (CES Catering)** : L'utilisateur a dit *« Ok delete le troisième clip »*. J'ai supprimé le kiosk_kids (4e segment de la timeline). L'utilisateur a corrigé : *« Non mais le troisième clip c'est pas le kiosque c'est le logo de culture en saveur tu t'es trompé »*. Le vrai 3e clip était `intro_steam_spice.mp4` (segment steam/logo).

**Cause racine :** Numérotation ambiguë. L'utilisateur compte les clips visuels visibles (1=chef, 2=kids, 3=steam/logo) mais la timeline interne inclut le stinger et la hook card (qui ne sont pas des "clips" pour l'utilisateur). De plus, l'utilisateur peut numéroter depuis 1 (humain) ou depuis 0 (code).

**Règle absolue : AVANT de supprimer un segment sur instruction verbale, EXTRAIRE des frames et CONFIRMER visuellement.**

```bash
# Extraire 1 frame au milieu de chaque clip pour identification
for t in 1.0 4.5 7.0 12.0 17.0; do
  ffmpeg -y -ss $t -i output/video.mp4 -frames:v 1 /tmp/clip_id_${t}s.jpg
done
```

Ou si la vidéo finale n'existe pas encore, extraire des frames des clips source :

```bash
for f in assets/seedance_catering/*.mp4; do
  ffmpeg -y -ss 1.0 -i "$f" -frames:v 1 "/tmp/src_$(basename $f .mp4).jpg"
done
```

**Envoyer les frames à l'utilisateur et demander :** *« Je supprime lequel ? »* — pas de supposition. Coût d'une vérification : 5 secondes. Coût d'un mauvais build : 2-3 minutes + frustration.

## ⚠ Extraction de photos produit depuis clips existants (gratuit, cohérent)

**Session août 2026 (CES Catering)** : Besoin d'illustrer les cartes menu avec des photos de plats (Hawawshi, Falafels, Beignets). Au lieu de générer de nouvelles images (coût crédits), extraction de frames depuis le clip kiosk_chef_v2 qui montre déjà les plats.

**Technique :**

```bash
# Le clip chef fait un dolly right : 0s=plat1, 2.5s=plat2, 4s=plat3
mkdir -p assets/food_frames
ffmpeg -y -ss 0.5 -i assets/seedance_catering/kiosk_chef_v2.mp4 -frames:v 1 assets/food_frames/hawawshi_raw.png
ffmpeg -y -ss 2.0 -i assets/seedance_catering/kiosk_chef_v2.mp4 -frames:v 1 assets/food_frames/falafel_raw.png
ffmpeg -y -ss 3.5 -i assets/seedance_catering/kiosk_chef_v2.mp4 -frames:v 1 assets/food_frames/beignet_raw.png
```

**Puis PIL pour transformer en cercle avec bordure brand :**

```python
# Crop to square (center)
side = min(fw, fh)
food = food.crop(((fw-side)//2, (fh-side)//2, (fw-side)//2+side, (fh-side)//2+side))
food = food.resize((280, 280), Image.Resampling.LANCZOS)
# Circular mask
mask = Image.new('L', (280, 280), 0)
ImageDraw.Draw(mask).ellipse([0, 0, 279, 279], fill=255)
# Border ring (terracotta)
draw.ellipse([W//2-148, 280-148, W//2+148, 280+148], fill=(163,57,43))
img.paste(food, (W//2-140, 280-140), mask)
```

**Avantages :** (1) Gratuit (pas de crédits), (2) Style cohérent avec le clip source, (3) Le plat correspond visuellement à ce que le spectateur a déjà vu. **Inconvénient :** Les timestamps d'extraction doivent être calibrés sur le mouvement de caméra du clip (dolly, pan, etc.) — si le clip est statique, n'importe quel timestamp donne la même image.

**⚠ Positionnement des photos sur la carte menu : BAS préféré au HAUT.** L'utilisateur a explicitement corrigé : *« On peut disposer plutôt les photos en bas plutôt qu'en haut »*. Placement initial à `ring_cy = 280` (haut de l'écran, au-dessus de la carte) → corrigé à `ring_cy = 1350` (sous la carte menu). Le layout préféré : nom du plat + description + origine + prix dans la carte (haut/centre), photo en cercle en bas. Vérifier que la photo ne chevauche pas le cercle de prix (`card_y + 420` ≈ y=900 pour une carte à `card_y=480`).

## ⚠ Correction de luminosité de clips IA avec ffmpeg eq (dark clip fix)

**Session août 2026 (CES Catering)** : Le clip kiosk_kids_v2 généré par Seedance était trop sombre par rapport aux autres vidéos. Correction avec le filtre `eq` de ffmpeg.

```bash
ffmpeg -y -i assets/seedance_catering/kiosk_kids_v2.mp4 \
  -vf "eq=gamma=1.3:brightness=0.08:saturation=1.15" \
  -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p -an \
  assets/seedance_catering/kiosk_kids_v2_bright.mp4
```

**Paramètres empiriques (août 2026) :**
- `gamma=1.3` : éclaircit les zones sombres sans brûler les hautes lumières
- `brightness=0.08` : lift global modéré
- `saturation=1.15` : compense la désaturation du gamma boost

**Règle :** Les clips générés par IA peuvent avoir des niveaux d'exposition incohérents entre générations. Faire une passe de correction colorimétrique sur CHAQUE clip avant intégration, surtout si l'utilisateur signale une incohérence visuelle entre clips. Ne pas hésiter à ajuster clip par clip.

## ⚠ Démarrage musique différé à un segment spécifique (pas seulement après stinger)

**Session août 2026 (CES Catering)** : La musique démarrait dès le début (0s). L'utilisateur a demandé qu'elle démarre au 2e clip (kiosk_chef), créant un effet d'entrée progressive — silence sur stinger + intro, puis la musique arrive avec l'action.

**Pattern : `adelay` sur la piste musique dans le filter_complex final.**

```python
# Calculer le délai = somme des durées des segments AVANT le point de départ
# Ex: musique au kiosk_chef = stinger(3.5s) + intro(8.8s) = 12.3s
music_delay_ms = int((stinger_dur + segments[1][1]) * 1000)

# Dans le filter_complex :
f"[2:a]volume=0.12,adelay={music_delay_ms}|{music_delay_ms},afade=t=out:st={total_dur-1.5}:d=1.5[music];"
```

**Différence avec la séparation stinger/content existante :** La technique précédente sépare juste le stinger (3.5s) du reste. Ici, la musique peut être retardée à N'IMPORTE QUEL point de la timeline — après l'intro, après le 1er clip, etc. L'effet narratif : silence = tension/attention, musique = relâchement/énergie.

**Attention :** Si la musique démarre tard, sa durée totale est plus courte. Vérifier que `total_dur - music_delay > musique_source_dur` ou ajouter un loop sur la musique.

## ⚠ Stinger `-an` obligatoire dans concat (sinon concat cassé)

**Session août 2026 (CES Catering)** : Le stinger (`signature_ces_stingered.mp4`) a été ajouté au script standalone catering. La commande de prep utilisait `-c:a aac -b:a 128k` (audio conservé), alors que TOUS les autres segments étaient préparés avec `-an` (pas d'audio). Résultat : le concat demuxer ffmpeg a produit une vidéo où le stinger ne s'affichait pas correctement.

**Fix :** Le stinger doit être préparé avec `-an` comme tous les autres segments vidéo. L'audio du stinger est géré séparément dans l'étape de mixage audio final (via `adelay` ou piste dédiée), pas dans le segment vidéo lui-même.

```python
# ❌ CASSÉ : stinger avec audio dans un concat de segments -an
run(['ffmpeg', '-y', '-i', str(stinger),
     '-vf', f'scale=1080:1920:...,fps={FPS}',
     '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
     '-c:a', 'aac', '-b:a', '128k',  # ← PROBLÈME
     '-pix_fmt', 'yuv420p', '-r', str(FPS), str(seg_stinger)], "stinger")

# ✅ CORRECT : stinger sans audio (consistance avec autres segments)
run(['ffmpeg', '-y', '-i', str(stinger),
     '-vf', f'scale=1080:1920:...,fps={FPS}',
     '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
     '-an',  # ← ALIGNÉ avec les autres segments
     '-pix_fmt', 'yuv420p', '-r', str(FPS), str(seg_stinger)], "stinger")
```

**Règle :** Dans un concat demuxer ffmpeg (`-f concat -safe 0`), TOUS les segments doivent avoir le même format audio (tous `-an` ou tous avec audio). Ne pas mixer. Le mixage audio se fait dans une étape séparée (`filter_complex` avec `amix`).

**⚠ Pattern de restauration audio stinger dans un script standalone (3 étapes).** Le stinger doit être `-an` dans le concat vidéo, mais son audio (jingle de marque) DOIT être audible dans le rendu final. Dans le master funnel builder, l'audio stinger est déjà géré via une piste dédiée dans le `filter_complex`. Dans un script standalone, il faut l'ajouter manuellement :

```python
# ÉTAPE 1 : Extraire l'audio du stinger source (avant le -an du prep)
stinger_audio = TMP / 'stinger_audio.aac'
run(['ffmpeg', '-y', '-i', str(stinger),
     '-vn', '-c:a', 'aac', '-b:a', '128k', str(stinger_audio)], "stinger_audio")

# ÉTAPE 2 : Ajouter comme input supplémentaire dans le build final
run([
    'ffmpeg', '-y',
    '-i', str(video),           # [0:v] vidéo concaténée
    '-i', str(vo_full),         # [1:a] voix off
    '-i', str(music),           # [2:a] musique
    '-i', str(stinger_audio),   # [3:a] ← audio stinger extrait
    ...

# ÉTAPE 3 : Inclure dans le filter_complex amix avec fade-out
f"[3:a]volume=1.0,afade=t=out:st={stinger_dur-0.3}:d=0.3[stin];"  # fade court en fin de stinger
f"[1:a]adelay={vo_delay_ms}|{vo_delay_ms},volume=2.5[vo];"
f"[2:a]volume=0.12,adelay={music_delay_ms}|{music_delay_ms},...[music];"
f"[stin][vo][music]amix=inputs=3:duration=longest:dropout_transition=0:normalize=0[aout]"
```

**Key points :**
- L'audio stinger joue à t=0 (pas de `adelay` — il est nativement au début du fichier extrait)
- Le `afade=t=out:st={stinger_dur-0.3}:d=0.3` évite un cut brutal à la fin du jingle
- `amix=inputs=3` (stinger + VO + musique), pas 2
- Sans cette restauration, le stinger visuel passe en silence total → user le remarque immédiatement

**Session août 2026 (CES Catering)** : L'utilisateur a signalé *« Le stinger on l'entend pas dans l'intro »*. Le stinger avait `-an` mais l'audio n'avait pas été restauré dans le mix final. Fix appliqué en 3 étapes ci-dessus.

## ⚠ Alignement de série pour scripts standalone : 4 points de consistance

**Session août 2026 (CES Catering)** : L'utilisateur a signalé que l'intro du catering ne ressemblait pas aux autres vidéos. L'audit a révélé 4 divergences entre le script standalone et le standard de la série (master funnel builder) :

| Élément | Standard série (funnel builder) | Script standalone (catering) divergent |
|---------|-------------------------------|---------------------------------------|
| **Stinger** | `signature_ces_stingered.mp4` en ouverture (3.5s) | ❌ Pas de stinger |
| **Voix VO** | `fr-CH-ArianeNeural` | ❌ `fr-FR-DeniseNeural` |
| **Fonts** | `font_title()` = Playfair Display + `font_body()` = Poppins | ❌ `font()` = Montserrat partout |
| **Intro card** | Crème `#F5E8D3`, logo, Playfair titre, dates, contact, tagline | ❌ Terracotta sombre, "CULTURE / EN SAVEURS / CATERING" |

**Checklist d'alignement standalone → série (à exécuter AVANT tout build d'une vidéo standalone dans une campagne) :**

```bash
# 1. Stinger présent dans le script ?
grep -c "stinger\|signature_ces" scripts/build_XXX.py
# Si 0 → ajouter stinger à la timeline + prep + vo_start adjustment

# 2. Voix VO identique à la série ?
grep "edge-tts.*voice" scripts/build_XXX.py
# Doit être fr-CH-ArianeNeural (ou la voix standard de la campagne)

# 3. Functions font identiques au master builder ?
grep "def font" scripts/build_XXX.py
# Doit avoir font_title() + font_body(), pas un seul font() générique

# 4. Design intro card identique ?
grep -A5 "make_intro\|make_hook" scripts/build_XXX.py | grep -E "CREAM|TERRACOTTA_DARK|Playfair|Montserrat"
# Doit utiliser CREAM + Playfair, pas TERRACOTTA_DARK + Montserrat
```

**Pattern de migration des fonts dans un script standalone :**

```python
# AVANT (Montserrat générique)
def font(size, bold=True):
    name = 'Montserrat-Bold.ttf' if bold else 'Montserrat-Regular.ttf'
    return ImageFont.truetype(str(FONT_DIR / name), size)

# APRÈS (aligné sur le master builder)
def font_title(size):
    """Playfair Display — titles."""
    return ImageFont.truetype(str(FONT_DIR / 'PlayfairDisplay-Variable.ttf'), size)

def font_body(size, medium=False):
    """Poppins — body text."""
    name = 'Poppins-SemiBold.ttf' if medium else 'Poppins-Regular.ttf'
    return ImageFont.truetype(str(FONT_DIR / name), size)

def font(size, bold=True):
    """Legacy fallback: Poppins."""
    name = 'Poppins-Bold.ttf' if bold else 'Poppins-Regular.ttf'
    return ImageFont.truetype(str(FONT_DIR / name), size)
```

Puis remplacer tous les appels `font(N, bold=True/False)` dans le script par `font_title(N)` ou `font_body(N, medium=True/False)`. Ne pas oublier les sous-titres ASS (`Style: Default,Poppins SemiBold,...` → `Style: Default,Poppins SemiBold,...` — Poppins SemiBold fonctionne en ASS si la police est installée sur le système).

**⚠ Ne pas oublier le sous-titre ASS Fontname.** Si le script standalone utilisait `Montserrat SemiBold` comme Fontname ASS, le remplacer par `Poppins SemiBold` (ou `Poppins` + Bold=-1 selon le système — voir section "ASS Fontname" ci-dessus).

## ⚠ Git pour projets vidéo : .gitignore agressif obligatoire

**Session août 2026 (CES livraison finale)** : `git add -A` a timeout (30s+) sur un repo contenant 883MB dans `output/` + 1.2GB dans `renders/`. Les vidéos finales et intermédiaires ne sont pas dans `.gitignore` → git tente de hasher des centaines de MB → gel.

**Fix : .gitignore agressif AVANT tout commit sur un projet vidéo.**

```gitignore
# Vidéos finales (gros fichiers, garder en local)
output/

# Rendus intermédiaires
renders/

# Clips IA sources (téléchargeables à nouveau)
assets/seedance_*/*.mp4
assets/food_frames/

# Fichiers concat temporaires
*.concat.mp4
video_concat.mp4

# Garder: scripts, configs, assets essentiels (logo, fonts, .ass, .env)
```

**Règle :** Sur un projet vidéo, seuls les scripts (`scripts/`), configs, assets légers (logo, fonts, subtitles .ass), et docs sont versionnés. Les MP4 (sources, intermédiaires, finaux) restent en local. Un repo vidéo ne devrait pas dépasser ~50MB.

**Pattern de livraison finale :** Créer un dossier `/tmp/<PROJECT>_LIVRAISON/` avec uniquement les vidéos finales compressées TG pour envoi, plutôt que de pousser les fichiers lourds sur git.

## ⚠ Alignement d'intro : `vo_start` et `INTRO_DUR` couplés (standalone → standard campagne)

**Session août 2026 (CES Catering)** : Alignement de l'intro du catering (standalone, intro terracotta divergente) avec le standard de la campagne (hook card crème + VO "L'association Culture en Saveur vous propose..."). L'intro est passée d'une constante fixe `INTRO_DUR = 3.0` à `durations["cat_v3_00"] + 0.5` (~8s, car le hook VO est plus long).

**Pitfall silencieux :** Le calcul `vo_start = INTRO_DUR + STEAM_DUR + 0.3` (qui détermine quand la VO + sous-titres démarrent) référençait encore `INTRO_DUR` (3.0s) alors que l'intro faisait maintenant ~8s. Résultat : la VO et les sous-titres auraient démarré 5s trop tôt, désynchronisés de la hook card visuelle.

**Fix :** `vo_start = 0.0` — la VO commence dès le début (elle joue pendant la hook card, comme dans le master funnel builder où le hook VO accompagne visuellement la hook card).

**Règle :** Quand on change la durée ou la structure de l'intro d'un script standalone :
1. Vérifier `vo_start` — ne pas référencer une constante fixe (`INTRO_DUR`) si l'intro est maintenant pilotée par `durations["hook_vo"]`
2. Vérifier le `vo_delay_ms` dans le build final (`ffmpeg ... -itsoffset`) 
3. Vérifier le `cursor` initial dans la génération de sous-titres ASS
4. Si la VO doit jouer pendant l'intro (pattern standard), `vo_start = 0.0`
5. Si la VO doit commencer après (ex: après stinger), `vo_start` = durée stinger + gap
