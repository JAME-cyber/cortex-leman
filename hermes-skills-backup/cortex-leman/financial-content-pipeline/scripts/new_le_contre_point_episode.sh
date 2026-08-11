#!/usr/bin/env bash
# Helper: scaffold un nouvel épisode LE CONTRE-POINT par copy-patch.
# Usage: scripts/new_le_contre_point_episode.sh <ep_num> <slug> [from_ep]
# Exemple: scripts/new_le_contre_point_episode.sh 04 schneider 3
#
# Action:
#   1. Trouve l'épisode source (from_ep si fourni, sinon le plus récent)
#   2. Crée ep<NN>_<slug>/ et copie gen_podcast.py
#   3. Affiche les 5 patches à appliquer (BASE, episode div, topic div, print, OUT, SECTIONS)
#   4. Rappelle les commandes de render + thumbnail + upload package
set -euo pipefail

CHANNEL="${CHANNEL_DIR:-/home/tars/crypto-project/CHANNEL}"
BASE_LECP="$CHANNEL/le_contre_point"

if [ $# -lt 2 ]; then
  echo "Usage: $0 <ep_num> <slug> [from_ep]" >&2
  echo "Exemple: $0 04 schneider 3" >&2
  exit 1
fi

EP_NUM="$1"
SLUG="$2"
FROM_EP="${3:-}"

EP_PADDED=$(printf "%02d" "$EP_NUM")
NEW_DIR="$BASE_LECP/ep${EP_PADDED}_${SLUG}"

# Trouver l'épisode source
if [ -z "$FROM_EP" ]; then
  SRC_DIR=$(ls -d "$BASE_LECP"/ep*_* 2>/dev/null | sort -V | tail -1)
else
  SRC_PADDED=$(printf "%02d" "$FROM_EP")
  SRC_DIR=$(ls -d "$BASE_LECP"/ep${SRC_PADDED}_* 2>/dev/null | head -1)
fi

if [ -z "$SRC_DIR" ] || [ ! -d "$SRC_DIR" ]; then
  echo "❌ Aucun épisode source trouvé." >&2
  exit 1
fi

SRC_SLUG=$(basename "$SRC_DIR" | sed 's/^ep[0-9]*_//')
SRC_EP=$(basename "$SRC_DIR" | sed 's/^ep\([0-9]*\)_.*/\1/' | sed 's/^0*//')
SRC_EP_PADDED=$(printf "%02d" "$SRC_EP")

echo "═══════════════════════════════════════════════════════════"
echo "  LE CONTRE-POINT — Nouvel épisode par copy-patch"
echo "═══════════════════════════════════════════════════════════"
echo "  Source : ep${SRC_EP_PADDED}_${SRC_SLUG}"
echo "  Cible  : ep${EP_PADDED}_${SLUG}"
echo "═══════════════════════════════════════════════════════════"
echo

# Créer le dossier et copier
mkdir -p "$NEW_DIR"
cp "$SRC_DIR/gen_podcast.py" "$NEW_DIR/gen_podcast.py"
echo "✅ Copié : $NEW_DIR/gen_podcast.py"
echo

echo "── 5 PATCHES À APPLIQUER dans gen_podcast.py ──"
echo
echo "1. BASE path :"
echo "   BASE = Path(\".../ep${SRC_EP_PADDED}_${SRC_SLUG}\")"
echo "        → BASE = Path(\".../ep${EP_PADDED}_${SLUG}\")"
echo
echo "2. Episode label :"
echo "   <div class='episode'>Épisode ${SRC_EP}</div>"
echo "        → <div class='episode'>Épisode ${EP_NUM}</div>"
echo
echo "3. Topic div :"
echo "   <div class='topic'>$(echo "$SRC_SLUG" | sed 's/.*/\u&/') — Le bear case</div>"
echo "        → <div class='topic'>$(echo "$SLUG" | sed 's/.*/\u&/') — Le bear case</div>"
echo
echo "4. Print header :"
echo "   print(\"  LE CONTRE-POINT — Épisode ${SRC_EP} : $(echo "$SRC_SLUG" | sed 's/.*/\u&/')\")"
echo "        → print(\"  LE CONTRE-POINT — Épisode ${EP_NUM} : $(echo "$SLUG" | sed 's/.*/\u&/')\")"
echo
echo "5. Output filename :"
echo "   OUT = BASE / \"le_contre_point_ep${SRC_EP_PADDED}_${SRC_SLUG}.mp4\""
echo "        → OUT = BASE / \"le_contre_point_ep${EP_PADDED}_${SLUG}.mp4\""
echo
echo "6. SECTIONS block : remplacer le dict ENTIER (7 sections cold_open → verdict)."
echo "   Conserver les disclaimers intro/outro + teaser outro (placeholders stables)."
echo "   Ne réécrire QUE le contenu analytique (rappel thèse, 3 angles, critères falsifiables, verdict)."
echo
echo "── RENDER ──"
echo "  cd ~/crypto-project && source .venv/bin/activate"
echo "  python3 CHANNEL/le_contre_point/ep${EP_PADDED}_${SLUG}/gen_podcast.py  # 60s à 2fps"
echo
echo "── THUMBNAIL (en parallèle) ──"
echo "  python3 CHANNEL/thumbnails/gen_thumbnail.py \\"
echo "    ${EP_PADDED} <TICKER> \"$(echo "$SLUG" | sed 's/.*/\u&/')\" \"<TAGLINE>\" <bg.jpg>"
echo
echo "── PACKAGE UPLOAD ──"
echo "  Écrire $NEW_DIR/YOUTUBE_UPLOAD.md"
echo "  (titre SEO, description + AMF disclaimer, chapitres alignés sur durations.json,"
echo "   tags, fichiers à uploader : .mp4 + thumbnail .png + audio/subs.srt)"
echo
echo "── VÉRIFICATIONS POST-RENDER ──"
echo "  - ffprobe durée vs somme durations.json (delta < 0.5s)"
echo "  - wc -l audio/subs.srt (devrait être ~120-180 entrées selon longueur)"
echo "  - Luminance centre thumbnail PIL (cible 40-60 pour ambiance sombre lisible)"
echo
echo "═══════════════════════════════════════════════════════════"
