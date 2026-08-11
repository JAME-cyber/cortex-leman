# Analyser une vidéo de référence depuis X/Twitter

L'utilisateur partage régulièrement des tweets de référence (techniques Seedance, showcases IA, pubs). Cette méthode permet d'extraire le contenu vidéo et de l'analyser sans compte X.

## Pipeline sans authentification

### 1. Récupérer les métadonnées + URL vidéo via vxtwitter

```bash
# Format: api.vxtwitter.com/i/status/TWEET_ID
curl -sL "https://api.vxtwitter.com/i/status/TWEET_ID" | python3.12 -m json.tool
```

Retourne : texte complet, URL vidéo directe (twimg CDN), likes/RT, user info.
**Aucune auth, aucun rate limit.** Read-only.

Si vxtwitter échoue → fallback chain : xurl read → Apify tweet-scraper → RAG browser (souvent bloqué).

### 2. Télécharger la vidéo

```bash
curl -sL -o /tmp/ref_video.mp4 "https://video.twimg.com/amplify_video/VIDEO_ID/vid/avc1/1280x720/HASH.mp4"
```

L'URL vient du champ `media_extended[0].url` de la réponse vxtwitter.

### 3. Scene detection (couper en plans)

```bash
# Détecter les cuts (threshold 0.1 = sensible)
ffmpeg -i /tmp/ref_video.mp4 -vf "select=gt(scene\,0.1),showinfo" -f null - 2>&1 \
  | grep "pts_time" | sed 's/.*pts_time:\([0-9.]*\).*/\1/'
```

Donne : liste des timestamps de cut → calculer durée moyenne par plan → comprendre le rythme de montage.

### 4. Contact sheet avec timestamps

```bash
# 1 frame / 1.2s, avec timestamp overlay
ffmpeg -y -i /tmp/ref_video.mp4 -vf "
  fps=1/1.2,
  scale=400:225,
  drawtext=fontcolor=yellow:fontsize=20:text='%{pts}s':x=5:y=5:box=1:boxcolor=black@0.5,
  tile=COLSxROWS
" /tmp/ref_contact_sheet.jpg
```

### 5. Récupérer le texte du tweet (prompt)

Le tweet principal est accessible via vxtwitter. Les **réponses du thread** (ex: prompt détaillé dans une réponse) nécessitent :

```bash
# Sur le browser X, cliquer "Voir plus" puis extraire via JS console :
document.querySelectorAll('article')[1].innerText
```

⚠ X tronque le texte sans login. Si "Voir plus" ne déplie pas (pas connecté), le texte reste coupé.

### 6. Analyse (vision model)

GLM-5.2 n'a **pas** de vision inline native. Pour analyser visuellement :
- Qwen 2.5 VL 72B via OpenRouter (`qwen/qwen2.5-vl-72b-instruct` SANS `:free`)
- Envoyer les contact sheets ou frames individuelles

**Fallback sans vision :** L'analyse technique seule (scene detection + ffprobe + texte du prompt) suffit déjà pour extraire le pattern de montage et les techniques utilisées.

## Métriques à extraire systématiquement

| Métrique | Comment | Pourquoi |
|----------|---------|----------|
| Durée, résolution, FPS | `ffprobe` | Specs techniques du rendu |
| Nombre de cuts, durée/plan | Scene detection | Rythme de montage |
| Prompt textuel | vxtwitter + DOM | Techniques de prompting |
| Timeline des phases | Contact sheet + cuts | Structure narrative |

## Insights Seedance 2.0 (积累)

### Style 3D animation ( Pixar-like)

**Tweet analysé :** @itsshara_ai (29 juil 2026) — Seedance 2.0 + GPT Image 2
- "Feature-film-quality 3D animation, expressive stylized characters" = Seedance peut faire du style animé, pas juste photoréaliste
- Prompt : *"A cinematic animated short film with feature-film-quality 3D animation, expressive stylized characters, a dimly lit cozy kitchen at midnight, moonlight through the window, warm faint nightlight glow, fast dynamic cinematic camera cuts with tense zoom-ins, playful suspenseful..."*
- Workflow : GPT Image 2 génère keyframes → Seedance 2.0 anime
- 12 cuts en 15s = avg 1.16s/plan (funnel d'escalade)
- Double source lumineuse (moonlight + nightlight) maintenue à travers 12 cuts = cohérence IA démontrée

**Applicabilité CES :** Le style "expressive stylized characters" pourrait remplacer le photoréalisme pour les clips enfants — plus ludique, moins uncanny valley.
**Applicabilité African Heroes :** Style animation 3D pour récits historiques animés.
