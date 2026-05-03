#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# Cortex Leman v5 — Déploiement Pilote
# ═══════════════════════════════════════════════════════════════
# Usage: bash scripts/deploy-pilot.sh
#
# Déploie un environnement pilote complet:
#   - NATS + Redis (infrastructure)
#   - API (backend FastAPI)
#   - Frontend (React + Nginx)
#   - RAG vectorisé
#
# Le cabinet partenaire accède au dashboard via:
#   http://<IP>:8090
# ═══════════════════════════════════════════════════════════════
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "═══════════════════════════════════════════════════════════"
echo -e "  ${CYAN}Cortex Leman v5${NC} — Déploiement Pilote"
echo "═══════════════════════════════════════════════════════════"
echo ""

# ── 1. Vérifications ──
echo -e "${YELLOW}[1/5]${NC} Vérifications pré-déploiement..."

if ! command -v docker &>/dev/null; then
    echo -e "  ${RED}✗${NC} Docker non installé"
    exit 1
fi
echo -e "  ${GREEN}✓${NC} Docker: $(docker --version | cut -d' ' -f3 | tr -d ',')"

if ! command -v docker compose &>/dev/null; then
    echo -e "  ${RED}✗${NC} Docker Compose V2 non disponible"
    exit 1
fi
echo -e "  ${GREEN}✓${NC} Docker Compose V2"

if [ ! -f ".env" ]; then
    echo -e "  ${YELLOW}⚠${NC} Pas de .env — copie depuis .env.example"
    cp .env.example .env
    echo -e "  ${YELLOW}⚠${NC} EDITEZ .env avant le pilote (SECRET_KEY, LLM_API_KEY...)"
fi

# ── 2. Build frontend ──
echo ""
echo -e "${YELLOW}[2/5]${NC} Build du frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install --silent
fi
npm run build 2>&1 | tail -3
cd ..
echo -e "  ${GREEN}✓${NC} Frontend: $(du -sh frontend/dist | cut -f1)"

# ── 3. Build Docker ──
echo ""
echo -e "${YELLOW}[3/5]${NC} Build des images Docker..."
docker compose -f docker-compose.prod.yml build --quiet 2>&1 | tail -5
echo -e "  ${GREEN}✓${NC} Images construites"

# ── 4. Démarrage ──
echo ""
echo -e "${YELLOW}[4/5]${NC} Démarrage des services..."
docker compose -f docker-compose.prod.yml down 2>/dev/null
docker compose -f docker-compose.prod.yml up -d 2>&1 | tail -10

# Attendre que tout soit prêt
echo -n "  Attente santé API"
for i in $(seq 1 30); do
    if curl -sf http://localhost:8090/health >/dev/null 2>&1; then
        echo ""
        break
    fi
    echo -n "."
    sleep 2
done

# ── 5. Vérification ──
echo ""
echo -e "${YELLOW}[5/5]${NC} Vérification des services..."

# API
API_STATUS=$(curl -sf http://localhost:8090/health 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))" 2>/dev/null || echo "fail")
if [ "$API_STATUS" = "healthy" ]; then
    echo -e "  ${GREEN}✓${NC} API: healthy"
else
    echo -e "  ${RED}✗${NC} API: $API_STATUS"
fi

# NATS
if docker compose -f docker-compose.prod.yml exec -T nats wget -q --spider http://localhost:8222/healthz 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} NATS: healthy"
else
    echo -e "  ${YELLOW}⚠${NC} NATS: vérifier les logs"
fi

# Redis
if docker compose -f docker-compose.prod.yml exec -T redis redis-cli ping 2>/dev/null | grep -q PONG; then
    echo -e "  ${GREEN}✓${NC} Redis: healthy"
else
    echo -e " ${YELLOW}⚠${NC} Redis: vérifier les logs"
fi

# MCP
MCP_TOOLS=$(curl -sf http://localhost:8090/mcp/tools 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('tools',[])))" 2>/dev/null || echo "0")
echo -e "  ${GREEN}✓${NC} MCP: ${MCP_TOOLS} tools disponibles"

# ═══ Résumé ═══
echo ""
echo "═══════════════════════════════════════════════════════════"
echo -e "  ${GREEN}✓ Pilote Cortex Leman v5 déployé${NC}"
echo ""
echo "  🔗 Dashboard:    http://localhost:8090"
echo "  🔗 API:          http://localhost:8090/api/v1/"
echo "  🔗 API Docs:     http://localhost:8090/docs"
echo "  🔗 MCP Tools:    http://localhost:8090/mcp/tools"
echo "  🔗 Health:       http://localhost:8090/health"
echo ""
echo "  📋 Comptes pilote:"
echo "     admin@cortex-leman.com    / C0rt3xL3m4n!"
echo "     expert@dupont-comptable.fr / comptable"
echo "     avocat@martin-avocat.ch    / avocat"
echo ""
echo "  📊 Logs:    docker compose -f docker-compose.prod.yml logs -f api"
echo "  🛑 Arrêt:   docker compose -f docker-compose.prod.yml down"
echo "  🔄 Restart: docker compose -f docker-compose.prod.yml restart api"
echo "═══════════════════════════════════════════════════════════"
echo ""
