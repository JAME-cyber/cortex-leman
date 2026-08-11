# Livraison Telegram — Compression & Content Map

## Compression TG (OBLIGATOIRE avant envoi)

Les vidéos finales (10-18MB en 720×1280) sont trop lourdes pour Telegram en qualité brute.
Toujours compresser avant envoi :

```bash
ffmpeg -i input.mp4 \
  -c:v libx264 -crf 26 -maxrate 3200k -bufsize 6400k -preset fast \
  -c:a aac -b:a 128k \
  -movflags +faststart \
  -y /tmp/output_TG.mp4
```

**Résultat typique** : 14MB → 7.5MB, qualité visuelle identique.

## ⚠ Pitfall : timeout ffmpeg (lot de 12+ vidéos)

La compression d'une vidéo >10MB dépasse systématiquement le timeout terminal par défaut (60s). En lot de 12 vidéos, la compression séquentielle dans une seule boucle dépasse même le timeout 300s.

**Session août 2026 (CES lot complet 12 vidéos)** : Une boucle shell compressant 12 vidéos séquentiellement a timeout à 300s après seulement 3 vidéos complétées. 

**Fix : traiter par sous-lots de 3-4 vidéos max par appel terminal.**

```bash
# MAL: 12 vidéos en une boucle → timeout à 300s après 3 vidéos
for pair in "vid1|src1" "vid2|src2" ... "vid12|src12"; do
  ffmpeg -y -i "$src" -crf 26 ... "$dst"   # ← trop long au total
done

# BIEN: lots de 3-4 par appel terminal (timeout=280)
for pair in "vid1|src1" "vid2|src2" "vid3|src3" "vid4|src4"; do
  ffmpeg -y -i "$src" -crf 26 -maxrate 3200k -bufsize 6400k -preset fast \
    -c:a aac -b:a 128k -movflags +faststart "$dst" 2>/dev/null
done
# Puis lot 2 (vid5-vid8), lot 3 (vid9-vid12)
```

**Pattern alternatif (plus robuste) : tâches en arrière-plan parallèles**

```bash
# Lancer 4 compressions en parallèle (background jobs)
for pair in "vid1|src1" "vid2|src2" "vid3|src3" "vid4|src4"; do
  name="${pair%%|*}"; src="${pair##*|}"
  ffmpeg -y -i "$src" -crf 26 -maxrate 3200k -bufsize 6400k -preset fast \
    -c:a aac -b:a 128k -movflags +faststart "/tmp/TG_lot_${name}.mp4" 2>/dev/null &
done
wait  # attendre toutes
```

**Ordre de priorité pour minimiser le temps total :**
1. D'abord les petites vidéos (<5MB, passent en direct sans compression → `cp`)
2. Ensuite les moyennes (5-10MB, ~30-60s chacune)
3. Enfin les grosses (10-20MB, ~90-120s chacune) en background parallèle

**Vérification post-compression :** Toujours vérifier que le fichier de sortie existe et fait une taille raisonnable (>100KB). Un fichier de 300K pour une vidéo de 11MB source indique une compression échouée silencieusement.

```bash
for f in /tmp/TG_lot_*.mp4; do
  sz=$(du -m "$f" | cut -f1)
  [ "$sz" -lt 1 ] && echo "⚠️ SUSPECT: $f = ${sz}MB"
done
```

## Limite 50MB Telegram ( vidéos > 50MB)

Telegram bot API hard cap = 50MB pour l'envoi de fichiers. Une vidéo de 51MB échoue silencieusement (le fichier n'arrive jamais).

**Fix — Compression agressive (scale down + CRF élevé)** :

```bash
ffmpeg -y -i input_51MB.mp4 \
  -c:v libx264 -preset ultrafast -crf 28 \
  -c:a aac -b:a 96k \
  -vf scale=720x1280 \
  -movflags +faststart \
  output_TG.mp4
```

**Résultat typique** : 51MB 1080×1920 → 13MB 720×1280. Qualité suffisante pour preview/approval sur mobile.

⚠️ `-preset fast` sur une vidéo 51MB timeout à 120s. Utiliser `-preset ultrafast` pour les fichiers > 30MB.

## Content Map (OBLIGATOIRE pour livraison multi-vidéo)

L'utilisateur suit le contenu par **thématique** (henné, tambours, visio, activités), pas par nom de fichier.

Quand on livre un lot de plusieurs vidéos, toujours fournir une **content map** :

```
| Contenu/thème | Vidéo | Segment |
|---------------|-------|---------|
| Henné | T4 Traditions | seg_henne |
| Tambours | T4 Traditions | seg_tambours |
| Visio orphelinat | T2 Visio | segment principal |
| Activités Rhône | T4 Traditions | seg_rhone |
```

**Pitfall** : si l'utilisateur demande "où est X ?", c'est que la livraison précédente n'avait pas de content map. Ne pas supposer qu'il connaît la structure T1/T2/T3/T4.

## Ordre de livraison recommandé

1. Compresser toutes les vidéos en parallèle (background jobs)
2. Fournir le content map en tableau
3. Envoyer les vidéos une par une avec MEDIA:
4. Indiquer la taille compressée vs originale
