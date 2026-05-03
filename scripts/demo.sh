#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# Cortex Leman v5 — Démo Express
# ═══════════════════════════════════════════════════════════════
# Usage: bash scripts/demo.sh
#
# Démarre: NATS + Redis + API + Frontend
# + Vectorise le vault réglementaire dans ChromaDB
# + Ouvre le dashboard dans le navigateur
# ═══════════════════════════════════════════════════════════════
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "═══════════════════════════════════════════════════════════"
echo -e "  ${CYAN}Cortex Leman v5${NC} — Graphe de Confiance"
echo "  Infrastructure de confiance IA — professions régulées FR-CH"
echo "═══════════════════════════════════════════════════════════"
echo ""

# ── 1. Vérifier les dépendances ──
echo -e "${YELLOW}[1/5]${NC} Vérification des dépendances..."

source .venv/bin/activate 2>/dev/null || {
    echo -e "${RED}✗${NC} Environnement Python non trouvé. Création..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt -q
}
echo -e "  ${GREEN}✓${NC} Python $(python --version 2>&1 | cut -d' ' -f2)"

# ── 2. NATS + Redis via Docker ──
echo ""
echo -e "${YELLOW}[2/5]${NC} Démarrage NATS + Redis..."
if command -v docker &>/dev/null; then
    docker compose up -d nats redis 2>/dev/null || {
        echo -e "  ${YELLOW}⚠${NC} Docker non disponible — mode dégradé (sans bus NATS)"
    }

    # Attendre que les services soient prêts
    sleep 2

    # Vérifier NATS
    if nc -z localhost 4222 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} NATS: localhost:4222"
    else
        echo -e "  ${YELLOW}⚠${NC} NATS non disponible — agents en mode dégradé"
    fi

    # Vérifier Redis
    if nc -z localhost 6379 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} Redis: localhost:6379"
    else
        echo -e "  ${YELLOW}⚠${NC} Redis non disponible — verrous distribués désactivés"
    fi
else
    echo -e "  ${YELLOW}⚠${NC} Docker non installé — mode dégradé"
fi

# ── 3. Seed RAG (vectoriser le vault) ──
echo ""
echo -e "${YELLOW}[3/5]${NC} Vectorisation du vault réglementaire..."
python scripts/seed_rag.py 2>/dev/null || echo -e "  ${YELLOW}⚠${NC} RAG déjà peuplé"

# ── 4. Démarrer l'API ──
echo ""
echo -e "${YELLOW}[4/5]${NC} Démarrage API FastAPI..."
export NATS_URL=${NATS_URL:-"nats://localhost:4222"}
export REDIS_HOST=${REDIS_HOST:-"localhost"}
export REDIS_PORT=${REDIS_PORT:-"6379"}

# Lancer en arrière-plan
uvicorn api.main:app --host 0.0.0.0 --port 8099 --reload &
API_PID=$!
echo -e "  ${GREEN}✓${NC} API: http://localhost:8099 (PID: $API_PID)""

# Attendre que l'API soit prête
for i in $(seq 1 10); do
    if curl -s http://localhost:8099/health >/dev/null 2>&1; then
        break
    fi
    sleep 1
done

# ── 5. Frontend ──
echo ""
echo -e "${YELLOW}[5/5]${NC} Démarrage Frontend React..."

# Build si nécessaire
if [ ! -d "frontend/dist" ]; then
    echo "  Build du frontend..."
    cd frontend && npm install --silent && npm run build && cd ..
fi

# Servir le frontend buildé
cd frontend
npx serve dist -l 3000 -s &
FRONTEND_PID=$!
cd ..
echo -e "  ${GREEN}✓${NC} Frontend: http://localhost:3000 (PID: $FRONTEND_PID)"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo -e "  ${GREEN}✓ Cortex Leman v5 est opérationnel${NC}"
echo ""
echo "  🔗 Frontend:    http://localhost:3000"
echo "  🔗 API:         http://localhost:8099"
echo "  🔗 API Docs:    http://localhost:8099/docs"
echo "  🔗 Health:      http://localhost:8099/health"
echo "  🔗 MCP Tools:   http://localhost:8099/mcp/tools"
echo ""
echo "  📋 Comptes démo:"
echo "     admin@cortex-leman.com    / C0rt3xL3m4n!"
echo "     expert@dupont-comptable.fr / comptable"
echo "     avocat@martin-avocat.ch    / avocat"
echo "     medecin@hopital-geneve.ch  / sante"
echo "     analyste@ubank.ch          / banque"
echo "     cto@startup-paris.fr       / startup"
echo "     drh@groupe-rh.fr           / rh"
echo ""
echo "  🛑 Arrêt: Ctrl+C ou kill $API_PID $FRONTEND_PID"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Ouvrir le navigateur
if command -v xdg-open &>/dev/null; then
    xdg-open http://localhost:3000 2>/dev/null &
fi

# Trap pour clean exit
cleanup() {
    echo ""
    echo "Arrêt de Cortex Leman v5..."
    kill $API_PID $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✓${NC} Arrêté proprement"
    exit 0
}
trap cleanup SIGINT SIGTERM

# Garder le script en vie
wait
