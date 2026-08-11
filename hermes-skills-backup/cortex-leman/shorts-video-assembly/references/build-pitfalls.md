# Build Pitfalls — ffmpeg encoding & Python deps

## 1. libx264 preset `medium` timeout sur 1080×1920

**Validé Aug 2026 (african-heroes Mami Wata).** Pour le rendu final d'un short vertical 9:16 (1080×1920) avec subtitles ASS + caption overlay + BGM en un seul pass ffmpeg, le preset `medium` dépasse systématiquement 300s — le timeout par défaut de `terminal()`. Le rendu est tué en cours → fichier .mp4 incomplet (40-60MB mais `ffprobe` retourne pas de durée valide).

**Fix :** utiliser `ultrafast` avec CRF 22 pour le rendu final. Coût qualité minime, temps divisé par 5-10x.

```python
# ❌ TIMEOUT à 300s sur 1080×1920 + ASS subs + overlay + BGM
"-c:v", "libx264", "-preset", "medium", "-crf", "20"

# ✅ Rendu en <60s
"-c:v", "libx264", "-preset", "ultrafast", "-crf", "22"
```

Même règle pour :
- Le concat outro (si présent)
- Le transcode TG (810×1440 → `ultrafast/CRF28` fonctionne)

Si une qualité supérieure est nécessaire (livrable client final), faire le rendu en arrière-plan avec `background=true, notify_on_complete=true` et un timeout élevé, OU splitter le rendu en passes séparées (video d'abord, puis audio, puis subs).

## 2. Playwright absent du venv Hermes

**Récurrent — affecte tout build avec captions HTML→PNG.**

Le venv Hermes (`~/.hermes/hermes-agent/venv`) n'a PAS Playwright installé. Tous les scripts de build qui capturent des captions HTML via `sync_playwright()` échouent avec `ModuleNotFoundError: No module named 'playwright'`.

**Fix :** utiliser le venv crypto-project qui a Playwright + Chromium installés :

```bash
# ❌ python3 build.py → ModuleNotFoundError
# ✅ /home/tars/crypto-project/.venv/bin/python3 build.py
```

**Alternatives :**
- Générer les captions avec PIL directement (si le design est simple — texte + formes géométriques)
- Installer Playwright dans le venv Hermes : `pip install playwright && playwright install chromium` (mais demande escalade — installation package)

## 3. tpad freeze-last-frame (anti-loop alternatif)

Quand un clip Seedance 5s doit couvrir une VO de 7-12s, NE PAS boucler (voir `clip-vo-timing.md` pour le pattern complet). En plus du slow-mo `setpts`, la technique `tpad=stop_mode=clone:stop_duration=N` gèle la dernière frame du clip pour combler la durée manquante :

```python
freeze_dur = dur - clip_dur  # ex: 11.2s VO - 5.0s clip = 6.2s freeze
vf = (
    f"scale=1080:1920:flags=lanczos,"
    f"tpad=stop_mode=clone:stop_duration={freeze_dur:.3f},"
    f"format=yuv420p"
)
```

**Quand utiliser tpad vs setpts :**
- **tpad** → clips contemplatifs, paysages, scènes où le mouvement s'estompe naturellement (la dernière frame est souvent une composition stable)
- **setpts (slow-mo)** → clips avec mouvement continu qu'on veut préserver (action, marche, eau qui coule)
- **Multi-angle cuts** → clips narratifs où l'immobilité casse le rythme

## 4. Seedance parallel generation pattern

**Pattern validé** sur Nzinga v3 et Mami Wata (african-heroes).

Pour générer 6-7 clips Seedance efficacement, utiliser `ThreadPoolExecutor(max_workers=3)` avec fire-all-then-poll :

```python
with ThreadPoolExecutor(max_workers=3) as pool:
    futures = {pool.submit(gen_one, kc, scene): scene["name"] for scene in SCENES}
    for future in as_completed(futures):
        result = future.result()
        # ...
```

**Budget :** ~78 crédits/clip 480p 5s → 7 clips ≈ 546 crédits. Toujours vérifier le solde avant (`kc.get_credits()`) et annoncer le coût estimé.

**Durée typique :** 3-5 minutes pour 7 clips en parallèle (certains clips peuvent mettre 3+ minutes individuellement).
