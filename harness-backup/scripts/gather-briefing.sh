#!/usr/bin/env bash
# gather-briefing.sh — collecte les 3 sources du daily briefing.
# stdout est injecté tel quel dans le prompt de l'agent (Hermes cron).
# Ne renvoie rien d'exploitable si une source est vide : l'agent gère le défaut.
set -u

SRC_DIR="${HERMES_HOME:-$HOME/.hermes}/briefing-sources"
CAL="$SRC_DIR/calendar.md"
LINKS="$SRC_DIR/links.md"
NOTES_DIR="$SRC_DIR/notes"

TODAY="$(date +%F)"   # YYYY-MM-DD

echo "===== SOURCES BRIEFING — $TODAY ====="
echo

# --- Source 1 : calendrier (uniquement les événements du jour) ---
echo "----- 1. CALENDRIER (aujourd'hui) -----"
if [[ -f "$CAL" ]]; then
  # awk : on cherche une section ## YYYY-MM-DD correspondant à aujourd'hui,
  # on imprime jusqu'à la prochaine section ## .
  awk -v d="$TODAY" '
    $0 ~ "^## "d { found=1; next }
    /^## [0-9]{4}-[0-9]{2}-[0-9]{2}/ { if (found) exit }
    found { print }
  ' "$CAL" | sed '/^[[:space:]]*$/d'
else
  echo "(calendrier manquant : $CAL)"
fi
echo

# --- Source 2 : notes / inbox / follow-ups ---
echo "----- 2. NOTES / DÉCISIONS / FOLLOW-UPS -----"
if [[ -d "$NOTES_DIR" ]]; then
  shopt -s nullglob
  for f in "$NOTES_DIR"/*.md; do
    echo "[[ $(basename "$f") ]]"
    cat "$f"
    echo
  done
else
  echo "(dossier notes manquant : $NOTES_DIR)"
fi

# --- Source 3 : liens sauvegardés ---
echo "----- 3. LIENS SAUVEGARDÉS -----"
if [[ -f "$LINKS" ]]; then
  grep -E '^- ' "$LINKS" || echo "(aucun lien)"
else
  echo "(fichier liens manquant : $LINKS)"
fi
echo
echo "===== FIN SOURCES ====="
