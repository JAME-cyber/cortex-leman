# Post-Feedback Batch Rebuild Workflow

Quand un client donne des retours nécessitant des changements de texte, musique, prix, ou autres éléments non-visuels à travers toute une série vidéo.

## 1. Les changements de script NE SONT PAS le livrable — les vidéos re-rendues le sont

Après avoir édité les build scripts (Python), il faut IMPÉRATIVEMENT re-exécuter TOUS les build scripts pour produire de nouveaux `.mp4`. Le livrable du client est la vidéo, pas le code source.

**Anti-pattern (attrapé juil. 2026) :** Agent a édité 19 scripts pour changer musique + prix, puis a annoncé "terminé" — l'utilisateur a dû demander *"Tu as fait le changement sur toutes les vidéos?"* parce qu'aucune vidéo n'avait été re-rendue.

## 2. Inventorier L'ENSEMBLE COMPLET des vidéos envoyées au client

Ne jamais supposer qu'un seul build script couvre tout. Un batch client peut s'étaler sur plusieurs scripts (ex: `build_funnel_all.py` pour 5 vidéos + `build_t4_funnel.py` pour la 6e + `build_v1pro_final_v2.py` pour la présentation).

Avant de rebuilder :
```bash
# Lister toutes les vidéos par date de modification (autour de la date d'envoi)
find output/ -name "*.mp4" -newermt "YYYY-MM-DD" -not -newermt "YYYY-MM-DD+1" -printf "%T+ %p\n" | sort
```

Identifier TOUTES les vidéos reçues par le client, puis faire correspondre chacune à son script générateur. Si le compte ne correspond pas à ce que l'utilisateur dit avoir envoyé, DEMANDER.

**Cas réel (juil. 2026) :** L'agent a supposé 5 vidéos (funnel_all) → l'utilisateur a corrigé "Moi j'ai six vidéos envoyées" → la 6e était T4 traditions (`build_t4_funnel.py`) + V1 PRO présentation (`build_v1pro_final_v2.py`).

## 3. Pattern de batch rebuild

Lancer les build scripts comme processus background avec `notify_on_complete=true`. Plusieurs scripts peuvent tourner en parallèle s'ils ne partagent pas de fichiers temporaires.

```python
# Après les builds, vérifier que chaque output a un timestamp frais
import os, time
for f in output_files:
    mtime = os.path.getmtime(f)
    age_hours = (time.time() - mtime) / 3600
    if age_hours > 1:
        print(f"⚠️ {f} not rebuilt (age: {age_hours:.1f}h)")
```

Après les builds :
- Vérifier chaque fichier output a un timestamp frais
- Compresser pour livraison Telegram (CRF 26, maxrate 3200k, preset fast)
- Livrer toutes les versions compressées ensemble

## 4. Pitfall asset reference — chemins explicites, JAMAIS glob

**Pitfall (juil. 2026) :** Un build script utilisait `glob("*.mp3")` pour trouver la musique. Après génération de nouvelles variantes musicales, le glob a pris le MAUVAIS fichier (premier alphabétiquement).

```python
# MAUVAIS — fragile, prend le mauvais fichier quand de nouveaux assets sont ajoutés
music_track = None
for m in (BASE / "assets/music").glob("*.mp3"):
    music_track = m
    break

# BON — déterministe
music_track = BASE / "assets/music/ces_v2_main.mp3"
```

Cela s'applique à TOUTES les références d'assets : musique, clips, images, fonts. Tout pattern glob/loop-first est un bug latent.

## 5. Corrections textuelles globales (prix, lieu, noms)

Quand le client corrige un détail factuel (prix, orthographe lieu, numéro de téléphone) qui apparaît dans plusieurs scripts :

```bash
# 1. Chercher dans TOUS les fichiers d'abord
search_files pattern="85.*semaine" path="project_root"

# 2. Fix en batch via terminal sed pour la rapidité
cd project_root && find scripts/ -name "*.py" -exec sed -i 's/85 CHF \/ semaine/85 CHF \/ journée/g' {} +

# 3. Vérification finale — 0 occurrence restante obligatoire
search_files pattern="85.*semaine" path="project_root"
# Doit retourner 0 match (ou seulement des faux positifs comme des timestamps)
```

## 6. Workflow complet de correction client (checklist)

1. ✅ Lister TOUS les retours client (texte, musique, visuel)
2. ✅ Identifier TOUS les scripts concernés (search_files)
3. ✅ Appliquer les corrections aux scripts
4. ✅ Vérifier 0 occurrence de l'ancien texte
5. ✅ Identifier TOUTES les vidéos envoyées au client (find par date)
6. ✅ Lancer TOUS les build scripts nécessaires (background + notify)
7. ✅ Vérifier timestamps frais sur chaque output
8. ✅ Compresser pour Telegram
9. ✅ Livrer toutes les vidéos ensemble
10. ✅ Annoncer ce qui a changé (musique X, prix Y, lieu Z)
