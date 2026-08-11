# Batch Quality Upgrade — Régénérer un lot de vidéos au standard le plus élevé

## Contexte

Session juil. 2026 (Culture en Saveur): une vidéo "Programme V0" a été produite avec des prompts Seedance détaillés (environment, lighting, Triple Identity Lock). Qualité visuelle largement supérieure aux autres clips du lot (T1, T2, T3). L'utilisateur demande de remonter tout le lot au même standard **sans rien perdre des contenus**.

## Principe directeur

**Le contenu narratif est figé. Seul le visuel change.**

- VO text inchangé
- Structure des segments inchangée (ordre, timing, nombre)
- Seuls les clips vidéo sources (image loops → Seedance clips) sont remplacés
- Les CTA cards, sous-titres, intro/stinger restent identiques

## Workflow en 5 étapes

### 1. Identifier le standard de référence
Repérer la vidéo de qualité la plus élevée dans le lot. Extraire son pattern de prompt:
- Détail d'environnement (lieu précis, heure, lumière naturelle)
- Triple Identity Lock (max 1-2 personnages par shot)
- Negative prompts stricts
- Voir `references/seedance-prompting-patterns.md`

### 2. Faire l'inventaire des clips à régénérer
```bash
# Lister les assets vidéo de chaque build script
grep -E "\.mp4|seedance|book_series" scripts/build_*.py | grep -v "^#"
```

Pour chaque clip à remplacer:
- Note le segment auquel il appartient (intro, pays, activité, CTA)
- Le texte VO associé (pour vérifier cohérence visuel/narratif)
- Le contexte géographique requis (ex: Petit-Lancy, Genève)

### 3. Générer les nouveaux clips Seedance
Script de génération batch — voir `templates/seedance_generate.py`.

Budget: ~205 crédits/clip 5s 720p 9:16 via kie.ai. Compter 1 clip par segment narratif.

Règle critique: **vérifier le solde avant de lancer**. La génération parallèle de 5 clips coûte ~1025 crédits.

### 4. Re-pointer les build scripts
Patcher chaque `build_*.py` pour pointer vers les nouveaux clips:

```python
# AVANT
S = BASE / "assets/seedance_t2"

# APRÈS
S2 = BASE / "assets/seedance_t2_v2"
# ... puis remplacer les chemins de clips individuels
```

### 5. Audit complet avant livraison
Lancer l'**audit batch complet** (voir `references/text-qa-checklist.md` § Audit batch complet).

Points spécifiques au quality upgrade:
- ✅ Aucun contenu narratif perdu (grep des mots-clés: pays, plats, noms, lieux)
- ✅ Date correcte (l'année peut avoir changé depuis la création initiale)
- ✅ Contact info cohérent cross-video
- ✅ Audio aligné (même musique partout)
- ✅ Format uniforme (toutes 9:16)
- ✅ Sous-titres cohérents (même police, taille, MarginV)

## Pattern de compression TG parallèle
Quand on re-render plusieurs vidéos, compresser en parallèle:

```bash
# Build + compress en un seul background job par vidéo
cd ~/culture-en-saveur && \
python3.12 scripts/build_t1_v2.py 2>&1 && \
ffmpeg -y -i output/T1_v2_final.mp4 -crf 26 -maxrate 3200k \
  -vf "scale=720:1280" -c:a aac -b:a 128k -movflags +faststart \
  /tmp/T1_v2_TG.mp4 2>/dev/null
```

Lancer 3 jobs en background simultanément (T1+T3+Programme).

## Bug récurrent: année codée en dur
Les CTA cards affichent l'année via `draw.text(..., "10-14 AOUT 2025")`. Quand on re-render des mois plus tard, l'année est souvent périmée. **Toujours vérifier**:
```bash
grep -rn "202[0-9]" scripts/build_*.py | grep -i "aout"
```
