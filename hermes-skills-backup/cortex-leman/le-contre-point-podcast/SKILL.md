---
name: le-contre-point-podcast
description: Pipeline de production podcast bear case pour L'EFFET COMPOSÉ. Génère vidéo long-form (script + TTS + multi-slide + thumbnail + SRT + package YouTube) en ~3 min par épisode. Format horizontal 1920x1080. ElevenLabs George (journalistique, naturel) avec fallback edge-tts HenriNeural. Moteur TTS partagé `tts_engine.py` utilisé par podcast ET Shorts. Multi-slide par section avec palette contrastée. B-roll IA photoréaliste via Veo 3.1 (kie.ai) pour métaphores visuelles — voir references/kieai-video-api.md.
---

# LE CONTRE-POINT — Pipeline podcast bear case

## Contexte
Série L'EFFET COMPOSÉ. Chaque acteur bull case (Shorts 9:16) a son pendant bear case long-form (LE CONTRE-POINT, 16:9 7-12min). Critères falsifiables, disclosure MiFID II, monologue narrateur.

## Actifs
- **Référence Ep1 OVHcloud**: `~/crypto-project/CHANNEL/le_contre_point/ep01_ovhcloud/` (pipeline validé)
- **Référence Ep2 ASML**: `~/crypto-project/CHANNEL/le_contre_point/ep02_asml/`
- **Référence Ep3 Soitec**: `~/crypto-project/CHANNEL/le_contre_point/ep03_soitec/`
- **Templates thumbnails**: `~/crypto-project/CHANNEL/thumbnails/gen_thumbnail.py` (long-form) + `gen_thumbnail_short.py` (shorts)
- **Logo LEC**: `~/crypto-project/CHANNEL/branding/logo_lec.png`
- **BGM**: `~/crypto-project/audio/bgm_stellardrone.mp3`
- **Environnement**: `~/crypto-project/.venv` (activé avec `uv`)

## Structure narrative (7 sections, monologue)
1. `01_cold_open` — **Hook chiffré** (chiffre concret + impact boursier) + **mécanisme de tease** (planter une question/"élément qu'on vous cache") + disclaimer MiFID II (~45s)
2. `02_rappel` — Thèse bull en 3 piliers (~50s)
3. `03_angle1` — Premier angle-mort (~85-95s)
4. `04_angle2` — Deuxième angle-mort (~85-95s)
5. `05_angle3` — Troisième angle-mort (~85-95s)
6. `06_changement` — Critères falsifiables (3 conditions mesurables, datées) (~50s)
7. `07_verdict` — **Résolution du tease** (révéler l'élément teasé au cold open) + **bénéfice viewer explicite** ("ce que ça change pour votre portefeuille") + disclosure + teaser épisode suivant (~75s)

Total cible: ~8-12 min (1000-1400 mots).

### Patterns narratifs intégrés (benchmark Yassine Sdiri, juil. 2026)
- **Hook chiffré obligatoire** dans `01_cold_open`: ouvrir avec un chiffre concret + impact mesurable (ex: "-34% en une séance", "2,7 milliards de capex annulés"). Jamais d'intro générique ("aujourd'hui on parle de X").
- **Mécanisme de tease**: le cold open plante une question/promesse qui n'est résolue qu'au `07_verdict`. Crée une boucle de rétention sur toute la durée. Le tease doit être lié au 3e angle-mort (le plus contre-intuitif) pour maximiser l'effet.
- **Bénéfice viewer** dans `07_verdict`: formuler la synthèse en termes actionnable pour le viewer ("ce que ça change concrètement pour votre position/exposition"). Pas de conclusion purement théorique.

## Workflow de production (3 min par épisode)

### Étape 1: Créer la structure
```bash
mkdir -p ~/crypto-project/CHANNEL/le_contre_point/ep<N>_<ticker>/
cp ~/crypto-project/CHANNEL/le_contre_point/ep0<N-1>_<prev>/gen_podcast.py \
   ~/crypto-project/CHANNEL/le_contre_point/ep<N>_<ticker>/gen_podcast.py
```

### Étape 2: 6 patchs ciblés sur `gen_podcast.py`
1. `BASE = Path(".../ep<N>_<ticker>")`
2. `<div class='episode'>Épisode <N></div>` + `<div class='topic'><Company> — Le bear case</div>`
3. `print("  LE CONTRE-POINT — Épisode <N> : <Company>")`
4. `OUT = BASE / "le_contre_point_ep<N>_<ticker>.mp4"`
5. **Remplacement intégral du dict `SECTIONS = {...}`** par le nouveau script
6. **Définir `SECTIONS_META`** : dict parallèle avec `text_key` (texte-clé majuscule affiché sur la slide) et `bg`/`accent` (couleurs de la palette multi-slide). Voir `## Alternance visuelle` pour la palette par section.

**Règles de contenu pour `SECTIONS`** (patterns narratifs benchmark):
- `01_cold_open`: phrase d'ouverture = **chiffre choc vérifiable + impact boursier + échelle de référence** (ex: "-34% en une séance" + "sur un marché de 15 milliards d'euros"). Jamais d'intro générique. Terminer par un **tease** pointant vers le 3e angle: "Mais le risque le plus grave, c'est celui dont personne ne parle. J'y reviens à la fin."
- `03_angle1` et `04_angle2`: angles classiques (valuation, concurrence, exécution).
- `05_angle3`: **angle le plus contre-intuitif** — c'est lui qui résout le tease. Le placer en 3e pour maximiser la rétention.
- `07_verdict`: ouvrir par "Rappelez-vous au début..." (résolution du tease), puis **bénéfice viewer** ("Ce que ça change concrètement pour votre exposition"), puis **question ouverte binaire** ("À vous de juger: la barrière, c'est le timing ou l'économie ? Dites-le en commentaire"), puis disclosure.

**Texte-clé pour `SECTIONS_META`** (majuscules, 3-5 mots):
- `01_cold_open`: le chiffre choc lui-même (ex: "-34%")
- `02_rappel`: "THÈSE BULL"
- `03_angle1`: mot-clé du premier angle (ex: "CYCLICITÉ AUTOMOBILE")
- `04_angle2`: mot-clé du deuxième angle
- `05_angle3`: mot-clé du troisième angle (le plus contre-intuitif)
- `06_changement`: "CRITÈRES FALSIFIABLES"
- `07_verdict`: "VERDICT"

### Étape 3: Lancer render (background, ~60-90s)
```bash
cd ~/crypto-project && source .venv/bin/activate && \
python3 CHANNEL/le_contre_point/ep<N>_<ticker>/gen_podcast.py
```
Output: `<base>/le_contre_point_ep<N>_<ticker>.mp4` (1920x1080, H264/AAC) + `audio/subs.srt`

### Étape 4: Thumbnail (5s)
```bash
python3 CHANNEL/thumbnails/gen_thumbnail.py <N> <TICKER> <Company> "<tagline>" <bg_path>
```
Output: `CHANNEL/thumbnails/le_contre_point_ep<N>_<ticker>/thumb_ep<N>_officiel.png`

### Étape 5: Package YouTube
Créer `YOUTUBE_UPLOAD.md` avec:
- Titre SEO (`<Company>: 3 risques qu'on ne vous dit pas`)
- Description (3 angles résumés + disclaimer MiFID II)
- Chapitres (timestamps calculés depuis `audio/durations.json`)
- Tags + catégorie Éducation/Finance

## Stack technique validée

| Composant | Choix | Pourquoi |
|---|---|---|
| TTS | **ElevenLabs George** (`JBFqnCBsd6RMkjVDRZzb`, multilingual_v2, stability=0.5, similarity=0.75) avec **fallback edge-tts HenriNeural** | Naturel (évite label "IA" YT). George = timbre journalistique, plus rapide naturellement qu'Adam. Fallback gratuit si quota dépassé. Voir `references/elevenlabs-tts-integration.md`. **Moteur partagé `tts_engine.py`** (voir section "Architecture TTS partagée"). |
| Slide | HTML/CSS statique 1920x1080 | Reproductible, style cohérent |
| Capture | Playwright (sync_api) | Headless, rapide |
| FPS | **2 fps** (slide statique) | Render 15x plus rapide, qualité visuelle identique |
| Preset ffmpeg | `ultrafast` + CRF 23 | Slide sans motion = pas besoin de medium |
| BGM | `volume=-28dB`, fade in 3s + fade out 4s | Voix reste intelligible |
| Sous-titres | `SUBS_ENABLED = False` (désactivés par défaut) | SRT uploadé séparément côté YT, pas burn-in |

## Architecture TTS partagée (`tts_engine.py`)

Le module `CHANNEL/le_contre_point/tts_engine.py` est la **source unique de voix** pour tout le pipeline LEC (podcast long-form + Shorts 9:16). Il ne faut PAS réimporter `edge_tts` directement dans les scripts — toujours passer par ce module.

### API publique
- `generate_tts(text, output_path)` → `{"path", "duration", "engine", "words"}`. Essaie George, fallback HenriNeural si quota/erreur.
- `generate_tts_batch(sections_dict, output_dir, json_path=None)` → idem pour N sections. Remplace le pattern `async def gen() + asyncio.run()` des anciens scripts Shorts.

### Fallback automatique
Le module tente ElevenLabs George en premier. Sur erreur (quota dépassé, 401, réseau), il bascule sur edge-tts HenriNeural `+0%` sans interruption. Le résultat indique `"engine": "elevenlabs"` ou `"edge"` — **toujours vérifier ce champ** dans le log pour savoir si le quota a tenu.

### Scripts consommateurs (migration edge-tts → tts_engine)
**Statut migration code (juil. 2026): TOUS les scripts importent `tts_engine.py`.**
- **Podcast long-form**: `ep03_soitec/gen_podcast.py` (référence migrée, 100% George validé). `ep01_ovhcloud/` et `ep02_asml/` restent en HenriNeural direct (code non migré — `edge_tts.Communicate` encore présent).
- **Shorts 9:16**: `video2/gen_tts_v2.py` (CoreWeave), `video3/build_clips.py` (OVH B/C/D), `video3/make_clipA.py` (OVH hook), `video3/make_signature.py` (bumper), `video4/gen_tts.py` (Trumpf), `video5/gen_tts.py` (ASML), `video6_portfolio/gen_portfolio.py` (portfolio), `branding/outro_signature/gen_outro.py` (outro).
- **Rendus audio+vidéo validés 100% George (juil. 2026)**: ep03 Soitec (7156 chars, 7.5min), video5 ASML (1273 chars, 69.4s, 14.2 MB), video4 Trumpf (100.2s body, 117s final 71 MB), video2 CoreWeave (339.1s body, 432s final 158 MB), video6 Portfolio (56.2s audio), video3 Clip A (48.8s body, 80.5s final 10 MB), video3 Clip B (48.0s body, 56.2s final), video3 Clip C (49.0s body, ~57s final).
- **En fallback HenriNeural (quota épuisé)**: video3 Clip D (65.9s, 100% edge), outro signature (11.9s, edge).
- **Intro+outro ajoutés manuellement** (ffmpeg concat) sur: video3 Clip A, video4 Trumpf, video2 CoreWeave.
- **Reste à faire**: (a) re-render Clip D + outro en George quand quota disponible (3ème clé ou plan Starter), (b) assembler video6 Portfolio (TTS prêt, vidéo pas assemblée), (c) ~~re-render Clips B+C avec pipeline corrigé~~ ✅ FAIT (CRF 18 + stream copy, sharpness 74→97 pour Clip B) — TTS en fallback HenriNeural, re-render George quand quota disponible. Voir `references/video-quality-encoding.md` section 5 pour les mesures.
- **Quota consommation catalogue**: 2 clés gratuites (10k chacune) épuisées. Catalogue complet estimé ~24k chars → plan Starter $5/30k couvre tout.

### Pattern d'import (pitfall: profondeur relative)
Les scripts Shorts vivent à des profondeurs variables sous `CHANNEL/`. L'import `sys.path.insert` doit pointer vers `CHANNEL/le_contre_point/`. Règle: `sys.path.insert(0, str(Path(__file__).parent.parent / "le_contre_point"))` couvre `CHANNEL/videoN/script.py` et `CHANNEL/branding/X/script.py` (2 niveaux). **Ne pas copier aveuglément un `parent.parent.parent`** — vérifier la profondeur réelle, sinon `ModuleNotFoundError: No module named 'tts_engine'`.

### Pacing: pas de `rate` avec ElevenLabs
George parle naturellement à ~137 mots/min, soit ~17% plus rapide qu'HenriNeural `+10%` (117 mots/min). Le paramètre `rate` d'edge-tts **n'a pas d'équivalent** ElevenLabs et n'est plus nécessaire. Les anciens Shorts à `+10%` sont correctement rendus par George sans accélération artificielle. Ne pas chercher à ralentir George pour "matcher" l'ancien timing — les timings vidéo se recalcule depuis les durées MP3 réelles (`durations.json`).

## Règles éditoriales

### Obligatoires
- **Disclaimer MiFID II** au début et disclosure à la fin (conformité AMF L. 541-1)
- **Critères falsifiables** publics et datés (sinon le bear case n'a pas de valeur)
- **Aucune recommandation d'achat/vente** explicite
- **Disclosure position** (même "ne détient pas de position")

### Style narratif
- Monologue posé, **ElevenLabs George** (multilingual_v2, stability=0.5, similarity=0.75), fallback auto edge-tts HenriNeural si quota dépassé
- Phrases courtes, ponctuées
- Chiffres prononcés en toutes lettres (ex: "cinquante-six pour cent", pas "56%")
- Sigles épelés: "T. S. M. C." (pas "TSMC")
- **Pacing variable** (différenciant vs Tech In Check): ralentir sur les angles bear, accélérer sur le verdict
- Pas de jargon non expliqué

### Patterns narratifs obligatoires (hook + tease)
- **Cold open = hook chiffré double**: la toute première phrase doit contenir (1) un chiffre marquant + impact et (2) une échelle de référence qui donne la mesure. Ex: "Quand OVHcloud a perdu quarante pour cent en une séance, c'est l'équivalent de quinze ans d'investissement qui s'évaporent." Bannir les intros génériques. Le chiffre doit être vérifiable et falsifiable.
- **Tease → résolution**: le cold open plante une promesse ("Mais il y a un détail que personne ne mentionne, et c'est le plus dangereux. J'y reviens à la fin.") résolue explicitement au verdict ("Rappelez-vous, au début, je vous ai dit qu'il y avait un détail..."). Le tease doit pointer vers le 3e angle-mort (le plus contre-intuitif).
- **Verdict = bénéfice viewer + question ouverte**: conclure par (1) l'impact concret pour le viewer ("Ce que ça change pour votre exposition"), puis (2) une question ouverte binaire qui force l'engagement commentaire ("À vous de juger: la barrière, c'est le timing ou l'économie ? Dites-le en commentaire"). Pas de conclusion purement théorique.

### Design thumbnail (long-form)
- Background photo: `brightness(0.95)` + `saturate(1.15)` (CLAIRE, jamais <0.80)
- Gradient directionnel: top 0.30 (clair) → bottom 0.75 (sombre)
- Texte: double `text-shadow` + `drop-shadow` (lisibilité conservée)
- Topbar or `#d4a017` "LE CONTRE-POINT"
- Risk-box jaune or top-right (3 puces)
- Ticker bordure or
- Logo LEC bottom-right

## Pièges et leçons

1. **Burn-in sous-titres = TUEUR de perf**: une fois testé à 30fps medium preset → 15min/rendu + timeout/crash. Solution: 2fps + ultrafast + `SUBS_ENABLED = False`. SRT reste dispo pour upload YT séparé.

2. **Ne pas oublier le disclaimer**: la conformité AMF/MiFID II est non négociable pour du contenu financier FR. Le LLM ne génère jamais seul l'autorité finale sur sujets réglementés — moteur de règles en aval.

3. **Pas de clip bull case pour cet acteur?** Le signaler explicitement dans le `YOUTUBE_UPLOAD.md` (transparence éditoriale). La thèse bull est reconstruite à partir du positionnement public.

4. **Background thumbnail trop sombre** (rejet user): le seuil minimum absolu est `brightness(0.80)`. En dessous, la photo devient invisible et le CTR chute.

5. **Ordre des opérations**: générer le script Markdown d'abord (pour validation contenu), ensuite seulement patcher `gen_podcast.py`. Évite de devoir re-render pour des corrections éditoriales.

6. **`execute_code` bloqué en cron**: ne pas utiliser `execute_code` pour les substitutions de fichiers en production cron — passer par `patch` (mode replace) qui marche dans tous les contextes.

7. **Identifier un pattern ≠ l'intégrer** (leçon workflow): quand un benchmark concurrentiel identifie un pattern (ex: "alternance visuelle", "hook chiffré"), l'identifier ne suffit pas. Toujours aller jusqu'à l'**implémentation concrète** (code/template testé) dans la même session. Un pattern noté comme "piste" sans code associé sera ignoré par le pipeline au prochain run. Les patterns appartiennent au SKILL.md (règles obligatoires) ou à un `templates/` (code prêt à copier) — pas à un "à faire plus tard" qui n'existe pas.

8. **Permissions de clé ElevenLabs**: une clé peut être limitée à un sous-ensemble de voix (erreur 401 `missing_permissions` sur les voix premium). Tester `client.voices.search()` en premier pour valider les permissions. Si refusée, tester directement les voice_id connus (Adam, George sont les plus accessibles). Voir `references/elevenlabs-tts-integration.md`.

9. **Profondeur `sys.path` pour `tts_engine`**: quand on migre un script Shorts vers le moteur partagé, l'import `from tts_engine import ...` échoue si la profondeur relative est mauvaise. Règle: compter les niveaux entre le script et `CHANNEL/le_contre_point/`. **Profondeur 2** (`CHANNEL/videoN/script.py`, `CHANNEL/branding/X/script.py`): `parent.parent`. **Profondeur 3** (`CHANNEL/branding/outro_signature/gen_outro.py`): `parent.parent.parent`. Toujours vérifier le premier run (`ModuleNotFoundError: No module named 'tts_engine'` = profondeur erronée), ne pas supposer que copier l'import d'un autre script fonctionne.

10. **Ne pas supposer le quota ElevenLabs**: la clé TTS-only ne permet pas de lire le quota restant (`user.get()` → 401 `missing_permissions`). On ne sait jamais combien il reste. Le fallback edge-tts est la sécurité — si George échoue, HenriNeural prend le relais silencieusement. Vérifier le champ `"engine"` dans les logs de render pour savoir ce qui s'est réellement passé.

11. **Batch render = risque d'audio mixte non publiable** (leçon juil. 2026): quand on render plusieurs vidéos d'affilée, les premières sections passent en George puis, quand le quota (10k chars/mois en gratuit) s'épuise, les suivantes tombent en fallback HenriNeural. **Un MP4 dont les sections sont mixtes George+HenriNeural n'est PAS publiable** — la voix change en plein milieu. Deux garde-fous: (a) **render séquentiel** + vérifier `all(r["engine"]=="elevenlabs" for r in durations.values())` après chaque vidéo, aborter si mixte; (b) **plan Starter ($5/30k chars)** couvre le catalogue complet (~24k: 7k/épisode podcast + ~17k pour les Shorts). Coût par épisode podcast ≈ 7 156 chars; Short moyen ≈ 500-2000 chars. Ne jamais lancer un batch de migration sans budget quota confirmé.

12. **`asyncio.run()` crash après migration tts_engine** (leçon juil. 2026, FIX IMPLÉMENTÉ): `build_clips.py` appelle `asyncio.run(gen_tts(...))` dans `build_clip()`. Le fallback edge-tts dans `tts_engine.py` appelait aussi `asyncio.run(c.save(...))`. Quand les deux sont imbriqués (event loop déjà actif), Python lève `RuntimeError: asyncio.run() cannot be called from a running event loop`. **Clip B et D ont crashé**, Clip C a passé (intermittent selon l'état du loop). **Fix appliqué dans `tts_engine.py`**: helper `_run_async_safely(coro)` qui détecte si un event loop tourne déjà (`asyncio.get_running_loop()`) et, si oui, lance la coroutine dans un `ThreadPoolExecutor` isolé avec son propre loop. Si aucun loop actif, `asyncio.run()` normal. Ce fix rend le fallback edge-tts compatible avec tous les contextes d'appel (sync, async, Playwright, batch).

13. **Rotation de clé ElevenLabs** (leçon juil. 2026): quand le quota est épuisé en cours de batch, pas besoin d'attendre le reset mensuel. Créer une nouvelle clé sur le dashboard ElevenLabs, puis `patch` le `.env` avec la nouvelle valeur `ELEVENLABS_API_KEY=sk_...`. Le module `tts_engine.py` lit la clé via `os.environ` au moment de l'import — un re-run du script TTS prend la nouvelle clé automatiquement. Tester avec un mot ('Test.') avant de relancer le batch complet. Coût catalogue complet ≈ 24k chars → une clé Starter ($5/30k) couvre tout.

14. **Intro+outro signature : TOUS les scripts assemble sont incohérents** (leçon juil. 2026, USER CORRECTION): la gestion intro/outro varie selon le script, et **aucun n'est complet**:
    - `make_clipA.py` (video3 Clip A): ❌ ni intro ni outro → ffmpeg concat manuel requis.
    - `assemble_v2.py` (video4 Trumpf): ✅ intro, ❌ pas d'outro.
    - `assemble_v2_broll.py` (video2 CoreWeave): ❌ ni intro ni outro.
    - `build_clips.py` (video3 Clips B/C/D): ✅ intro + outro (le seul complet).
    - `assemble_v2.py` (video5 ASML): ✅ intro + outro.
    
    **Règle absolue**: après tout render, vérifier la présence de l'intro (`intro_9x16.mp4`, 5.0s) ET l'outro (`outro_signature.mp4`, ~11s) dans le MP4 final. Si manquant, concaténer via:
    ```bash
    # concat_list.txt: un file '...' par ligne (intro → body → outro)
    ffmpeg -y -f concat -safe 0 -i concat_list.txt \
      -c:v libx264 -preset ultrafast -pix_fmt yuv420p -r 24 \
      -c:a aac -b:a 128k output_FINAL.mp4
    ```
    L'utilisateur s'attend à ce que **chaque** clip livré ait le branding LEC complet. Ne jamais livrer un MP4 brut sans vérifier.

15. **Compression Telegram : H.264 single-pass dégrade le texte** (leçon juil. 2026, USER CORRECTION): pour livrer une vidéo >50 MB via bot Telegram, la compression H.264 single-pass à 900 kbps dégrade gravement la netteté des slides textuelles — l'utilisateur le remarque immédiatement ("la nette des images se sont dégradées"). **Règle générale**: pour les vidéos LEC (slides texte + b-roll), **jamais** de compression H.264 single-pass en dessous de 1500 kbps. Préférer **HEVC (H.265) 2-pass** à ~850 kbps qui préserve la netteté du texte à taille équivalente (HEVC est ~40% plus efficace que H.264 à qualité égale). Commande de référence (compter 15-20 min pour 7 min de 1080p, lancer en `background=true`):
    ```bash
    # 2-pass HEVC pour Telegram (<50 MB, texte net)
    ffmpeg -y -i input.mp4 -c:v libx265 -preset medium -b:v 850k \
      -x265-params "pass=1" -an -f null /dev/null
    ffmpeg -y -i input.mp4 -c:v libx265 -preset medium -b:v 850k \
      -x265-params "pass=2" -pix_fmt yuv420p -c:a aac -b:a 96k output_HEVC.mp4
    ```
    Le 2-pass double le temps d'encodage mais garantit une distribution bitrate optimale. Pour une vidéo de 7 min en 1080p, compter 15-20 min de render. Lancer en `background=true` avec `notify_on_complete=true`. Toujours vérifier la taille finale `<50 MB` avant envoi.

19. **HEVC échoue sur l'output concaténé du pipeline B-roll AI v3** (leçon juil. 2026): le pipeline `assemble_ai_broll_v3_full.py` produit un MP4 via `ffmpeg concat -c copy` (stream copy de segments H.264 loopés avec `-stream_loop`). **libx265 refuse cet input** — erreur silencieuse: `frame=0 fps=0.0 Lsize=0kB` + `Conversion failed!` dès la première frame, en single-pass ET en 2-pass. Le problème vient probablement des timestamps créés par `-stream_loop` qui désorientent l'encodeur HEVC.
    **Fix validé**: H.264 ultrafast à 1100 kbps (single-pass) sur l'output concaténé v3 produit un résultat acceptable (49 MB pour 5:28, user n'a pas signalé de dégradation). Commande:
    ```bash
    ffmpeg -y -i video2_broll_ai_v3.mp4 \
      -c:v libx264 -preset ultrafast -b:v 1100k -maxrate 1500k -bufsize 2200k \
      -c:a aac -b:a 128k video2_broll_ai_v3_tg.mp4
    ```
    **Règle**: si le HEVC échoue avec `frame=0` sur un input concaténé, basculer immédiatement sur H.264 ultrafast 1100k plutôt que de debuguer libx265. Le bitrate 1100k est le sweet spot pour 720p 5-6 min (<50 MB). Pour 1080p, viser 1000-1200k (le texte reste net grâce à la résolution supérieure).

20. **Livraison en clips individuels (un par section)** (USER PREFERENCE juil. 2026): l'utilisateur peut demander "des vidéos au même timing de chaque changement de clip" = **clips séparés par section**, pas un seul fichier long. Chaque clip `clip_NN_<section>.mp4` existe déjà comme intermédiaire du pipeline v3 — il suffit de les compresser individuellement pour Telegram. Script de batch: `templates/compress_individual.py`. Résultat typique: 2-8 MB par clip (vs 49 MB pour le fichier complet). **Toujours vérifier** si l'utilisateur veut le fichier complet OU les clips individuels avant de lancer la compression — c'est une vraie bifurcation de livraison, pas une action automatique.
    
    **Ne pas demander confirmation pour les actions standardisées** (leçon juil. 2026, USER CORRECTION): la compression Telegram est une étape automatique du pipeline, pas une décision. Quand l'utilisateur dit "comme d'habitude" ou "ben comme d'habitude", c'est un signal que la question était superflue. Règle: pour toute action récurrente déjà documentée dans ce skill (compression TG, ajout intro/outro, vérification sharpness), **exécuter directement sans demander**. Réserver les questions pour les vraies décisions éditoriales ou les bifurcations de pipeline.

16. **Dégradation multi-pass dans `build_clips.py`** (leçon juil. 2026): le pipeline Shorts `build_clips.py` ( Clips B/C/D) encodait la vidéo **4 fois** en cascade: (1) `build_video_segment` CRF 21, (2) mux vidéo+audio CRF 20, (3) subs+BGM CRF 20, (4) concat intro+body+signature CRF 20. Résultat: bitrate final dérisoire (332 kbps pour Clip C), slides texte floues. **Diagnostique**: `ffprobe` montre un bitrate <500 kbps sur un Short 1080x1920 = problème qualité. Comparer avec un clip de référence sain (Clip A: ~1041 kbps). **Fix appliqué** (juil. 2026): (a) segments initiaux en CRF 18 (au lieu de 21), (b) mux vidéo+audio en `-c:v copy` (stream copy, pas de re-encode), (c) subs+BGM CRF 18, (d) concat final CRF 18. Cela réduit à **3 encodages** (au lieu de 4) et chaque passage préserve mieux le texte. **Règle générale**: tout pipeline FFmpeg multi-étapes doit minimiser les re-encodages intermédiaires — utiliser `-c:v copy` ou des codecs lossless (`-c:v ffv1`, `-c:v libx264 -crf 0`) pour les intermédiaires, et réserver l'encodage lossy (CRF 18-20) à l'étape finale uniquement. Pour les slides statiques (peu de variance visuelle), le CRF est trompeur: le compresseur alloue peu de bits car il n'y a pas de mouvement → le texte devient flou. Surveiller le bitrate final, pas seulement le CRF.

17. **`zoompan` avec pre-scale 2x = timeout/crash** (leçon juil. 2026, pipeline B-roll AI): le filtre `zoompan` appliqué sur une image pré-scalée à `W*2:H*2` (ex: 2560×1440) génère des fichiers intermédiaires énormes (158 MB pour 40s de slide) et provoque des timeouts (>5 min par slide). **Diagnostique**: un seul slide PNG → MP4 fait >100 MB ou le render dépasse 300s sans compléter. **Fix**: pour les slides statiques, remplacer `zoompan` par un simple `scale=W:H` (sans zoom du tout) ou `scale + crop` fixe. Si l'effet Ken Burns est vraiment nécessaire, utiliser `zoompan` directement sur la résolution cible `s=WxH` sans pre-scale, avec un incrément minimal (`0.03` au lieu de `0.05`). L'effet visuel est négligeable sur des slides texte statiques — la netteté prime sur le mouvement. Dans `assemble_ai_broll.py`, le passage de `scale=W*2:H*2 + zoompan` à `scale=W:H` simple a réduit le render de >300s (timeout) à ~60s total pour 9 sections.

18. **B-roll AI loop: timeout render sur 9 sections** (leçon juil. 2026): l'encodage x264 de 9 clips AI (chacun loopé sur 20-55s) dépasse 300s en foreground. Chaque section nécessite (1) loop + scale du clip source, (2) overlay slide, (3) mux audio = 3 passes ffmpeg par section. **Fix**: toujours lancer `assemble_ai_broll_v2.py` en `background=true` avec `notify_on_complete=true`. Le preset `ultrafast` est obligatoire — `medium` multiplie le temps par 5. Si le timeout frappe en cours de batch, les clips déjà rendus (`clip_NN_*.mp4`) sont préservés — relancer ne re-render que les sections manquantes en vérifiant les fichiers existants. Alternative: générer section par section via des appels ffmpeg directs (une section = une commande), puis concaténer.

## Benchmark concurrentiel et améliorations

Voir `references/competitive-benchmark-yassine-sdiri.md` pour l'analyse complète d'un créateur YT IA/tech FR (256k abonnés, format long-form 16:50).

Patterns empruntables identifiés et intégrés (benchmarks Yassine Sdiri + Tech In Check French, juil. 2026):
1. **Hook chiffré double** — ouvrir avec un chiffre concret + impact boursier + échelle de référence (ex: "-34% en une séance" + "2,7 milliards de capex, c'est l'investissement annuel de toute l'industrie européenne"). Plus puissant qu'un chiffre seul.
2. **Mécanisme de tease** — planter une question au cold open, la résoudre au verdict (rétention 12+ min observée chez les deux chaînes)
3. **Alternance visuelle multi-slide** — 7 slides par section au lieu d'une slide unique, codes couleur contrastés + texte-clé par section (voir `## Alternance visuelle` ci-dessous)
4. **Bénéfice viewer explicite** — reformuler le verdict en "ce que ça change pour votre portefeuille"
5. **Question ouverte finale** — clore par une question binaire qui force l'engagement commentaire (signal algo YT)

Avantages différenciants à conserver: dual bull/bear (eux = pure bull), conformité AMF (eux = aucun disclaimer), pipeline automatisé ~3min (eux = studio manuel), critères falsifiables, monologue posé non-robotique (pacing variable vs Tech In Check 270-310 mots/min monotone).

Références: `references/competitive-benchmark-yassine-sdiri.md`, `references/competitive-benchmark-tech-in-check.md`, `references/video-quality-encoding.md` (qualité vidéo, bitrates, compression Telegram, dégradation multi-pass).

## Alternance visuelle (multi-slide par section)

**Problème**: la slide unique statique loopée = aucune variation visuelle. Yassine alterne talking head/screen (lum 30→160), Tech In Check alterne b-roll sombre/data clairs (lum 38→163). Notre pipeline doit créer un contraste similaire.

**Solution implémentée**: remplacer `capture_slide()` (1 PNG unique) par `capture_slides()` (7 PNGs, un par section) avec codes couleur et texte-clé contrastés. Concaténation vidéo par section au render.

### Palette par section

| Section | Background | Accent | Texte-clé affiché | Effet visuel |
|---------|-----------|--------|-------------------|--------------|
| `01_cold_open` | `#04102B` (bleu nuit profond) | Rouge `#E84545` | "RISQUE #1" / chiffre choc | Sombre, alarmant |
| `02_rappel` | `#0A1F3C` (bleu nuit clair) | Vert `#36D478` | "THÈSE BULL" | Doux, neutre |
| `03_angle1` | `#1A0A0A` (rouge noir) | Rouge `#E84545` | Mot-clé angle 1 (ex: "CYCLICITÉ") | Sombre, menaçant |
| `04_angle2` | `#1A0A0A` (rouge noir) | Rouge `#E84545` | Mot-clé angle 2 (ex: "CONCENTRATION") | Sombre, menaçant |
| `05_angle3` | `#1A0A0A` (rouge noir) | Rouge `#E84545` | Mot-clé angle 3 (ex: "CAPEX") | Sombre, menaçant |
| `06_changement` | `#0A2A0A` (vert noir) | Or `#D2B257` | "CRITÈRES FALSIFIABLES" | Ouvert, analytique |
| `07_verdict` | `#04102B` (bleu nuit profond) | Or `#D2B257` | "VERDICT" | Synthèse, posé |

### Texte-clé par slide
Chaque slide de section affiche, en plus du branding LEC:
- Le numéro de section (ex: "01", "02"...)
- Un **texte-clé** majuscule, 3-5 mots, qui résume la section (ex: "CYCLICITÉ AUTOMOBILE", "CONCENTRATION CLIENT")
- Pour `01_cold_open`: le **chiffre choc** du hook en très grand
- Pour `06_changement`: les **3 critères falsifiables** listés

### Impact technique
- Capture: 7 screenshots Playwright au lieu d'1 → +5-7s (de ~3s à ~8-10s)
- Render: concaténation de 7 segments vidéo au lieu d'un loop → négligeable (2fps ultrafast)
- Taille output: identique (H264 CRF 23)
- Le texte-clé doit être défini dans le dict `SECTIONS_META` (séparé du texte TTS)

## B-roll IA (Veo 3.1 via kie.ai)

**Cas d'usage validé (juil. 2026): B-roll photoréaliste pour vidéo2 CoreWeave.** Les clips IA (datacenter, GPU racks, fibre optique, construction timelapse, trading screens) remplacent les Ken Burns statiques sur les sections à fort contenu visuel (hook, capacité, capex). Un pipeline **parallèle** distinct (`CHANNEL/video2/broll_ai.py`) génère les clips sans toucher au pipeline principal.

### Règle de présentation: B-roll en loop background + slides transparentes (USER CORRECTION juil. 2026)

**Trois approches testées et classées par ordre de validation user:**

| Version | Approche | Verdict user |
|---------|----------|-------------|
| v1 (`assemble_ai_broll.py`) | Clip AI 1-3s en intro de section, puis slide prend le relais | ❌ "furtif, on voit à peine la vidéo" |
| v2 (`assemble_ai_broll_v2.py`) | Clip AI loop + slide PNG opaque overlay à 88% | ❌ "on ne voit presque rien, le fond opaque couvre la vidéo" |
| v3 (`assemble_ai_broll_v3_full.py`) | Clip AI loop + **slide à fond transparent** (bg #04102B → alpha 0) | ✅ "pas mal, essayons comme ça" |

**Pattern validé (v3)**: le clip AI joue en boucle pendant toute la section. La slide est rendue **transparente** — le fond `#04102B` est remplacé par de l'alpha (PIL/numpy), seul le texte et les éléments graphiques restent. La vidéo AI est visible derrière le texte sur ~85% de la surface du cadre.

**Étapes critiques v3:**
1. **Transparentisation des slides** (PIL + numpy, 84.8% des pixels deviennent transparents):
   ```python
   from PIL import Image
   import numpy as np
   img = Image.open("slide.png").convert("RGBA")
   arr = np.array(img)
   BG_R, BG_G, BG_B = 4, 16, 43  # #04102B
   tol = 15
   mask = ((np.abs(arr[:,:,0].astype(int) - BG_R) < tol) &
           (np.abs(arr[:,:,1].astype(int) - BG_G) < tol) &
           (np.abs(arr[:,:,2].astype(int) - BG_B) < tol))
   arr[mask, 3] = 0  # transparent
   # Soft edges (tol+12 pixels)
   edge = (...tol+12...) & ~mask
   arr[edge, 3] = arr[edge, 3] // 3
   Image.fromarray(arr).save("slide_transparent.png")
   ```
2. **Compositing ffmpeg** (loop AI + slide transparente overlay):
   ```
   ffmpeg -stream_loop N -i clip.mp4 -t $DUR \
     -i slide_transparent.png \
     -filter_complex "[0:v]scale=W:H:force_original_aspect_ratio=increase,crop=W:H,eq=brightness=-0.05:saturation=0.9:contrast=1.05[bg];[bg][1:v]overlay=0:0[v]" \
     -map "[v]" -t $DUR composed.mp4
   ```
3. Lancer en `background=true` avec `notify_on_complete=true` (9 sections > 300s foreground).

**Rejets à ne pas réessayer:**
- **Layout split (panneau droite)**: coupe le texte ou le clip en deux ("on voit la moitié du texte ou du clips"). Ne pas tenter un crop de la slide dans un panneau latéral.
- **Slide opaque à 88% opacity**: le fond `#04102B` reste opaque à 88% → la vidéo est invisible derrière. L'opacité d'un PNG overlay ne traverse pas les couleurs sombres.

**Template v3 complet**: `templates/assemble_ai_broll_v3_full.py` — pipeline prêt à copier (transparentisation PIL + loop AI + overlay + concat + BGM).

### Règle absolue: B-roll IA ≠ slides texte
L'IA vidéo photoréaliste (Veo 3.1, Seedance, Kling) est **incompatible** avec les slides textuelles LEC — elle génère du texte déformé/illisable. Usage restreint aux **métaphores visuelles** (datacenters, GPU, infrastructure, trading floors). Les slides (scorecards, critères falsifiables, chiffres) restent en HTML/CSS capturé par Playwright. Ne jamais tenter de générer une slide texte en IA vidéo.

### Coût & budget
- **Veo 3.1 Fast 1080p**: 65 crédits/clip ($0.325). Un short à 5 clips = 325 crédits (~$1.63).
- Seedance 2.0 et Kling 2.5 sont des alternatives viables (même pattern API, coûts similaires).
- Le solde crédits n'est pas lisible via API — suivre manuellement sur https://kie.ai/billing.

### Workflow (pipeline parallèle)
1. **Génération** (`broll_ai.py`): submit N clips via `POST /api/v1/veo/generate` → reçoit `taskId` par clip.
2. **Polling** (background, 2 min interval): `GET /api/v1/veo/record-info?taskId=...` jusqu'à `successFlag==1`. **⚠️ `successFlag` est au niveau `data`, PAS `data.response`** — lire `data["data"]["successFlag"]`. Délai typique 5-15 min. Voir `references/kieai-video-api.md` pitfall #1.
3. **Download**: récupère `resultUrls[]` → wget en local. **Rétention 14 jours** sur kie.ai.
4. **Intégration** (`assemble_ai_broll_v2.py`): clip AI en **loop sur toute la durée de section** + slide PNG overlay à 88% (style CNBC). **Pas d'intro furtif** — le clip joue en background pendant que les chiffres s'affichent par-dessus. Voir `## Règle de présentation` ci-dessus.
5. **A/B comparison**: livrer version originale (Ken Burns) + version IA pour validation visuelle user.

### Pattern prompt B-roll
Photoréaliste, cinématique, **pas de texte lisible**, pas de personnes identifiables. Exemple validé:
> "Cinematic slow camera pan through a massive modern data center. Endless rows of server racks with blue and green LED lights blinking. Cold fog rolling across the floor. Cool blue lighting, photorealistic, 4K cinematic, shallow depth of field. No people, no text."

**Template script**: `templates/broll_ai.py` — client kie.ai Veo 3.1 prêt à copier. Définir `BROLL_CLIPS` (id + prompt), lancer `python broll_ai.py` puis `--status`. Le fix `successFlag` au niveau `data` est déjà intégré.

**Template assemblage v3 (VALIDÉ)**: `templates/assemble_ai_broll_v3_full.py` — pipeline complet (transparentisation PIL + loop AI + overlay + concat + BGM). **C'est la version à utiliser.** Copier, adapter `BROLL_MAP` et les paths, lancer en background.

**Template compression clips individuels**: `templates/compress_individual.py` — batch H.264 pour livraison Telegram en clips séparés (un par section, 2-8 MB chacun). Utiliser quand l'utilisateur demande "des vidéos au timing de chaque section" plutôt qu'un seul fichier long. Voir SKILL.md pitfall #19 (HEVC KO sur inputs concaténés) et #20 (format livraison clips individuels).

**Template assemblage v2 (OBSOLÈTE)**: `templates/assemble_ai_broll_v2.py` — ancienne approche slide opaque 88%, rejetée par user (vidéo invisible derrière). Conservé pour archive uniquement.

Voir `references/kieai-video-api.md` pour le détail complet des endpoints, paramètres, pricing, et pitfalls.

## Sources factuelles (à vérifier par épisode)
- Rapports annuels entreprises
- Communications investisseurs
- Sources publiques (DigiTimes, communiqués TSMC, BIS US, etc.)
- Web tools (`web_search`) si configurés — sinon connaissance générique avec prudence sur les chiffres précis

## Vérification finale (avant livraison)
```bash
# Durée + format
ffprobe -v quiet -show_entries format=duration:stream=width,height,codec_name \
        -of json <mp4>
# SRT valide
wc -l <base>/audio/subs.srt
head -30 <base>/audio/subs.srt
# Thumbnail dimensions
python3 -c "from PIL import Image; print(Image.open('<thumb>').size)"
```

Critères d'acceptation:
- Vidéo: 1920x1080, H264+AAC, 7-12 min, <15 MB
- SRT: >100 entrées, timestamp final ≈ durée vidéo
- Thumbnail: 1280x720
- `YOUTUBE_UPLOAD.md` présent avec disclaimer + chapitres + tags
