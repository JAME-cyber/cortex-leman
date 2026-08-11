#!/usr/bin/env bash
set -euo pipefail

# Veille Video AI Watchdog — SILENT si rien n'a changé, ALERT si nouveau modèle/feature/prix
# Surveille: kie.ai (Seedance), kinetix.tech (Kamo-1), Google Veo, Kling, Wan
# Pattern: compare état actuel vs état connu (hash). Alert seulement si delta.

STATE_DIR="/tmp/.veille-video-ai"
mkdir -p "$STATE_DIR"

ALERT=""
CHANGES=""

# ==========================================
# 1. KIE.AI — Page Seedance (nouveaux modèles, prix)
# ==========================================
KIE_HASH_FILE="$STATE_DIR/kie_hash"
KIE_CONTENT=$(curl -sL --max-time 15 "https://kie.ai/seedance-2-5" 2>/dev/null | sha256sum | cut -d' ' -f1)
if [ -n "$KIE_CONTENT" ]; then
  KIE_OLD=$(cat "$KIE_HASH_FILE" 2>/dev/null || echo "none")
  if [ "$KIE_CONTENT" != "$KIE_OLD" ]; then
    if [ "$KIE_OLD" != "none" ]; then
      CHANGES+="🔄 kie.ai/seedance-2-5 — page modifiée (hash changé)\n"
      CHANGES+="  Vérifier: https://kie.ai/seedance-2-5\n"
    fi
    echo "$KIE_CONTENT" > "$KIE_HASH_FILE"
  fi
fi

# 2. KIE.AI — Homepage (nouveaux modèles en générale)
KIE_HOME_HASH="$STATE_DIR/kie_home_hash"
KIE_HOME=$(curl -sL --max-time 15 "https://kie.ai" 2>/dev/null | sha256sum | cut -d' ' -f1)
if [ -n "$KIE_HOME" ]; then
  KIE_HOME_OLD=$(cat "$KIE_HOME_HASH" 2>/dev/null || echo "none")
  if [ "$KIE_HOME" != "$KIE_HOME_OLD" ]; then
    if [ "$KIE_HOME_OLD" != "none" ]; then
      CHANGES+="🔄 kie.ai homepage — nouveau contenu détecté\n"
      CHANGES+="  Vérifier: https://kie.ai\n"
    fi
    echo "$KIE_HOME" > "$KIE_HOME_HASH"
  fi
fi

# ==========================================
# 3. KINETIX.TECH — Kamo-1 (beta → API, pricing, new features)
# ==========================================
KAMO_HASH="$STATE_DIR/kamo_hash"
KAMO_CONTENT=$(curl -sL --max-time 15 "https://kinetix.tech" 2>/dev/null | sha256sum | cut -d' ' -f1)
if [ -n "$KAMO_CONTENT" ]; then
  KAMO_OLD=$(cat "$KAMO_HASH" 2>/dev/null || echo "none")
  if [ "$KAMO_CONTENT" != "$KAMO_OLD" ]; then
    if [ "$KAMO_OLD" != "none" ]; then
      CHANGES+="🔄 kinetix.tech — page modifiée (Kamo-1 update?)\n"
      CHANGES+="  Vérifier: https://kinetix.tech\n"
    fi
    echo "$KAMO_CONTENT" > "$KAMO_HASH"
  fi
fi

# ==========================================
# 4. WAN VIDEO — Nouvelles versions (2.x → 3.x)
# ==========================================
WAN_HASH="$STATE_DIR/wan_hash"
WAN_CONTENT=$(curl -sL --max-time 15 "https://wan.video" 2>/dev/null | sha256sum | cut -d' ' -f1)
if [ -n "$WAN_CONTENT" ]; then
  WAN_OLD=$(cat "$WAN_HASH" 2>/dev/null || echo "none")
  if [ "$WAN_CONTENT" != "$WAN_OLD" ]; then
    if [ "$WAN_OLD" != "none" ]; then
      CHANGES+="🔄 wan.video — page modifiée (nouvelle version?)\n"
      CHANGES+="  Vérifier: https://wan.video\n"
    fi
    echo "$WAN_CONTENT" > "$WAN_HASH"
  fi
fi

# ==========================================
# 5. KLING AI — Nouveaux modèles / prix
# ==========================================
KLING_HASH="$STATE_DIR/kling_hash"
KLING_CONTENT=$(curl -sL --max-time 15 "https://kling.kuaishou.com" 2>/dev/null | sha256sum | cut -d' ' -f1)
if [ -n "$KLING_CONTENT" ]; then
  KLING_OLD=$(cat "$KLING_HASH" 2>/dev/null || echo "none")
  if [ "$KLING_CONTENT" != "$KLING_OLD" ]; then
    if [ "$KLING_OLD" != "none" ]; then
      CHANGES+="🔄 kling.kuaishou.com — page modifiée\n"
      CHANGES+="  Vérifier: https://klingai.com\n"
    fi
    echo "$KLING_CONTENT" > "$KLING_HASH"
  fi
fi

# ==========================================
# OUTPUT
# ==========================================
if [ -n "$CHANGES" ]; then
  echo "📡 VEILLE VIDÉO IA — Changements détectés:"
  echo ""
  echo -e "$CHANGES"
  echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
else
  # Silent — rien de nouveau
  exit 0
fi
