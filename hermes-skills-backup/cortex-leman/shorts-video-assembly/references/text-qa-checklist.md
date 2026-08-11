# Text QA Checklist — Audit orthographique et factuel avant livraison

## Problème

Session juil. 2026 (Culture en Saveur): 3 fautes étaient gravées dans les vidéos finales, détectées seulement à la relecture utilisateur:
1. **"Poids chiches" → "Pois chiches"** — faute de frappe dans le build script catering
2. **"École de Quartier" → "Maison de Quartier"** — nom du lieu inventé au lieu du nom officiel
3. **"Inscrivez vite" → "Inscrivez-vous vite"** — pronom élidé manquant en français formel

## Root Cause

Le texte affiché dans les vidéos provient de sources multiples (VO scripts, drawtext ffmpeg, PIL ImageDraw, fichiers ASS) éparpillées dans plusieurs scripts Python. Aucun audit centralisé n'existe jusqu'à la livraison.

## Checklist obligatoire avant livraison vidéo

### Étape 1: Extraire TOUT le texte affiché
```bash
# VO text
grep -E "^\s+\(" scripts/gen_vo_*.py scripts/build_*.py | grep -E "\"[A-Z]"

# Sous-titres ASS
grep "^Dialogue" subtitles.ass | sed 's/.*,,/  /'

# drawtext ffmpeg
grep -E "text=|drawtext" scripts/build_*.py

# PIL ImageDraw text
grep -E "draw.text|text=" scripts/build_*.py | grep -v "font\|bbox\|import\|#"
```

### Étape 2: Vérifications systématiques
| Catégorie | Vérification | Erreur fréquente |
|-----------|-------------|------------------|
| Orthographe FR | Accord verbe-sujet (Inscrivez-vous) | Pronom élidé oublié |
| Noms propres | Lieu, organisation, personne | Nom approximatif/inventé |
| Noms de plats | Hawawshi, Koshari, Ndolé, Canjeero | Translittération variable |
| Email/handles | cultureensaveur@gmail.com (pas de S) | Cf endcard-completeness-checklist.md |
| Téléphone | Format CH +41 XX XXX XX XX | Inconsistance 0xx/+41 |
| Prix/CHF | Cohérence avec source officielle | Montant approximatif |

### Étape 3: Cross-check avec source officielle
Comparer tous les éléments factuels (lieux, dates, prix, horaires, noms) contre:
- Le flyer officiel (image)
- Le questionnaire client
- Le brief initial

**CRITIQUE — Handles et emails:** les réseaux sociaux ont souvent des underscores invisibles. Le brief `@culture_ensaveurs` (avec `_`) ≠ `@cultureensaveurs` (sans). L'email peut aussi différer (`cultureensaveur@gmail.com` sans S ≠ `@culture_ensaveurs` avec S Instagram). **Toujours grep le brief original**:
```bash
grep -i "instagram\|@culture\|email\|mail" research/client_brief.md
```
Ce bug a survécu 7 vidéos avant d'être détecté par audit LLM externe.

### Étape 4: Re-render si corrections
Patcher le build script source (`patch` tool), pas le fichier vidéo directement. Re-render depuis le script pour traçabilité.

```bash
# Re-render parallèle (3 vidéos en background)
cd ~/culture-en-saveur
python3.12 scripts/build_teaser_clean.py &
python3.12 scripts/build_catering_v2.py &
python3.12 scripts/build_endcard_v2.py &
```

## Pattern: Audit avant delivery, pas après
Faire cet audit AVANT d'envoyer la vidéo à l'utilisateur. Le coût d'un re-render est négligeable vs le coût d'une faute perçue comme un manque de professionnalisme.

---

## Cohérence cross-vidéo (ajout juil 2026)

### Alignement audio
Toutes les vidéos d'une même campagne/brand doivent partager la **même musique de fond**. Identifier la piste de référence et vérifier:
```bash
# Lister les musiques utilisées dans tous les build scripts
grep -E "music|afroswing|afrobeat.*mp3" scripts/build_*.py | grep -v vo | grep "\.mp3"
```
Si incohérence → remplacer dans le build script et re-render.

### Cohérence du décor géographique (Seedance)
Quand une vidéo contient des clips IA montrant un lieu physique, vérifier que le décor correspond au lieu réel de l'événement (pas un décor générique). Voir `references/ffmpeg-zoompan-subtitles.md` §3 (Ancrage géographique).

### Date / année (ajout juil. 2026)
Les CTA cards codent l'année en dur dans les scripts PIL (`draw.text(..., "10-14 AOUT 2025")`). Quand l'année change (nouveau camp, report), ces dates ne sont **jamais mises à jour automatiquement**. 3 vidéos sur 6 affichaient "2025" au lieu de "2026".

Vérification:
```bash
# Trouver toutes les années codées en dur
grep -rn "202[0-9]" scripts/build_*.py | grep -i "aout\|date\|2025\|2026"
```

Règle: **aucune vidéo ne doit afficher une année expirée**. Si certaines vidéos n'affichent pas d'année sur leur CTA (intentionnel), c'est acceptable. Mais toute année affichée doit être correcte.

### Audit batch complet (cross-video)
Quand plusieurs vidéos d'une même campagne sont livrées ou mises à jour ensemble, lancer un audit systématique en une passe. Le pattern complet:

```bash
# 1. Format (toutes doivent être 9:16)
for f in /tmp/*_TG.mp4; do
  ffprobe -v quiet -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "$f"
done

# 2. Audio (toutes doivent partager la même musique de fond)
grep -oP "music.*?\.mp3" scripts/build_*.py

# 3. Sous-titres (taille de police ASS cohérente)
grep "Style.*Default" scripts/build_*.py

# 4. Contact info — VERIFIER LE BRIEF pour les handles exacts
grep -h "076\|cultureensaveur\|@culture" scripts/build_*.py | sort -u
# ATTENTION: @culture_ensaveurs (IG avec _) ≠ cultureensaveur@gmail.com (email sans _ ni S)
# Toujours croiser avec: grep -i "instagram\|email" research/client_brief.md

# 5. CTA unifié — toutes les vidéos d'info doivent avoir les MÊMES champs
#    (dates, tranche d'âge, tarifs jour+nuit, promo fratrie, places, contact)
grep -h "85 CHF\|55 CHF\|10%\|4-12\|8h30\|limit" scripts/build_*.py | sort -u

# 5. Dates
grep -rn "202[0-9]" scripts/build_*.py | grep -i "aout"

# 6. Contenu narratif (rien perdu)
grep -oiP "egypte|koshari|cameroun|ndole|somalie|canjeero|nil|amina|maxime" scripts/build_*.py | sort -u
```

Ce pattern audit en une passe détecte: format incohérent, musique désalignée, police variable, typo email, année expirée, et contenu narratif perdu lors d'un upgrade qualité.
