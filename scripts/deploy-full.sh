#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# Cortex Leman v5 — Déploiement Complet sur la Machine Locale
# ═══════════════════════════════════════════════════════════════════
# Usage: bash scripts/deploy-full.sh [--stop-old] [--build] [--dev]
#
# Déploie TOUTE la stack v5:
#   - NATS JetStream (bus événementiel)
#   - Redis (cache + verrous distribués)
#   - PostgreSQL (base de données)
#   - API FastAPI v5 (backend avec les 5 agents)
#   - Frontend React (servi par Nginx)
#   - ChromaDB (RAG vectoriel)
#   - Prometheus + Grafana (monitoring)
#
# Accessible depuis TOUTES les machines du réseau local.
# ═══════════════════════════════════════════════════════════════════
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Couleurs
G='\033[0;32m'; C='\033[0;36m'; Y='\033[1;33m'; R='\033[0;31m'; B='\033[1m'
NC='\033[0m'

# Parse args
STOP_OLD=false
BUILD=false
MODE="prod"
for arg in "$@"; do
    case $arg in
        --stop-old) STOP_OLD=true ;;
        --build)    BUILD=true ;;
        --dev)      MODE="dev" ;;
    esac
done

echo ""
echo "═══════════════════════════════════════════════════════════"
echo -e "  ${C}Cortex Leman v5${NC} — Déploiement Complet (${MODE})"
echo "═══════════════════════════════════════════════════════════"
echo ""

# ── Détection IP locale ──
LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
[ -z "$LOCAL_IP" ] && LOCAL_IP="192.168.0.25"

# ── 1. Vérifications ──
echo -e "${Y}[1/7]${NC} Vérifications..."

if ! command -v docker &>/dev/null; then
    echo -e "  ${R}✗${NC} Docker non installé!"
    echo "  → curl -fsSL https://get.docker.com | sh"
    exit 1
fi
echo -e "  ${G}✓${NC} Docker $(docker --version | grep -oP '\d+\.\d+\.\d+')"

if ! docker compose version &>/dev/null; then
    echo -e "  ${R}✗${NC} Docker Compose V2 requis!"
    exit 1
fi
echo -e "  ${G}✓${NC} Docker Compose V2"

if [ ! -f ".env" ]; then
    echo -e "  ${Y}⚠${NC} Pas de .env — copie depuis .env.example"
    cp .env.example .env
    echo -e "  ${R}⚠${NC}  EDITEZ .env AVANT de continuer (LLM_API_KEY, SECRET_KEY...)"
    echo -e "  ${R}⚠${NC}  Puis relancez ce script."
    exit 1
fi
echo -e "  ${G}✓${NC} .env présent"

# ── 2. Stopper l'ancienne stack ──
echo ""
echo -e "${Y}[2/7]${NC} Nettoyage..."

if [ "$STOP_OLD" = true ]; then
    echo -e "  ${Y}→${NC} Arrêt de l'ancienne stack hermes/cortex-leman..."
    cd /home/tars/.hermes/cortex-leman 2>/dev/null && docker compose down 2>/dev/null || true
    cd "$ROOT"
    echo -e "  ${G}✓${NC} Ancienne stack arrêtée"
else
    echo -e "  ${Y}⚠${NC} Ancienne stack encore active. Pour l'arrêter: --stop-old"
fi

# Arrêter les anciens conteneurs v5 (s'ils existent)
docker compose down 2>/dev/null || true
docker compose -f docker-compose.prod.yml down 2>/dev/null || true
echo -e "  ${G}✓${NC} Anciens conteneurs v5 nettoyés"

# ── 3. Build frontend ──
echo ""
echo -e "${Y}[3/7]${NC} Build du frontend React..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo -e "  ${C}→${NC} Installation des dépendances npm..."
    npm install --silent 2>&1 | tail -3
fi
echo -e "  ${C}→${NC} npm run build..."
npm run build 2>&1 | tail -5
cd "$ROOT"
if [ -d "frontend/dist/index.html" ] || [ -f "frontend/dist/index.html" ]; then
    echo -e "  ${G}✓${NC} Frontend: $(du -sh frontend/dist 2>/dev/null | cut -f1)"
else
    echo -e "  ${R}✗${NC} Build frontend échoué!"
    exit 1
fi

# ── 4. Build Docker images ──
echo ""
echo -e "${Y}[4/7]${NC} Build des images Docker..."

if [ "$MODE" = "prod" ]; then
    echo -e "  ${C}→${NC} Build image production (multi-stage)..."
    docker build -f Dockerfile.prod -t cortex-leman-v5:latest . 2>&1 | tail -5
else
    echo -e "  ${C}→${NC} Build image développement..."
    docker build -f Dockerfile -t cortex-leman-v5:latest . 2>&1 | tail -5
fi
echo -e "  ${G}✓${NC} Image cortex-leman-v5:latest prête"

# ── 5. Préparer les volumes ──
echo ""
echo -e "${Y}[5/7]${NC} Préparation des volumes..."

mkdir -p data/journal data/reports data/vault data/precedents data/chroma_db data/intentions

# Copier les données réglementaires si le vault est vide
if [ ! -f "data/vault/catalog.json" ] && [ -d "data/vault" ]; then
    echo -e "  ${C}→${NC} Données vault déjà présentes"
else
    echo -e "  ${C}→${NC} Volumes data/ prêts"
fi
echo -e "  ${G}✓${NC} Volumes prêts"

# ── 6. Démarrage ──
echo ""
echo -e "${Y}[6/7]${NC} Démarrage des services..."

# Choisir le compose file
if [ "$MODE" = "dev" ]; then
    COMPOSE_FILE="docker-compose.yml"
else
    COMPOSE_FILE="docker-compose.prod.yml"
fi

# Démarrer
docker compose -f "$COMPOSE_FILE" up -d 2>&1 | tail -10

# Attendre que l'API soit prête
echo -n "  Attente API"
for i in $(seq 1 40); do
    if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
        echo " ${G}✓${NC}"
        break
    fi
    echo -n "."
    sleep 2
    if [ $i -eq 40 ]; then
        echo ""
        echo -e "  ${R}✗${NC} API n'a pas démarré dans les 80s"
        echo -e "  → docker compose -f $COMPOSE_FILE logs api"
        exit 1
    fi
done

# ── 7. Vérification ──
echo ""
echo -e "${Y}[7/7]${NC} Vérification des services..."

check_service() {
    local name=$1
    local url=$2
    local status=$(curl -sf "$url" 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))" 2>/dev/null || echo "fail")
    if [ "$status" = "healthy" ]; then
        echo -e "  ${G}✓${NC} $name: ${status}"
    else
        echo -e "  ${Y}⚠${NC} $name: ${status}"
    fi
}

check_service "API" "http://localhost:8000/health"

# NATS
if docker compose -f "$COMPOSE_FILE" exec -T nats wget -q --spider http://localhost:8222/healthz 2>/dev/null; then
    echo -e "  ${G}✓${NC} NATS: healthy"
else
    echo -e "  ${Y}⚠${NC} NATS: vérifier"
fi

# Redis
if docker compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping 2>/dev/null | grep -q PONG; then
    echo -e "  ${G}✓${NC} Redis: healthy"
else
    echo -e "  ${Y}⚠${NC} Redis: vérifier"
fi

# Seed les données réglementaires RAG
echo ""
echo -e "  ${C}→${NC} Seed des données réglementaires..."
curl -sf -X POST http://localhost:8000/api/v1/vault/regulatory/load \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $(curl -sf -X POST http://localhost:8000/api/v1/auth/login \
        -H 'Content-Type: application/json' \
        -d '{"email":"admin@cortex-leman.com","password":"C0rt3xL3m4n!"}' \
        | python3 -c 'import sys,json; print(json.load(sys.stdin).get("access_token",""))')" \
    2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'  {d}')" 2>/dev/null || echo "  (seed optionnel)"

# ═══ RÉSUMÉ ═══
echo ""
echo "═══════════════════════════════════════════════════════════"
echo -e "  ${G}✓ Cortex Leman v5 DÉPLOYÉ${NC}"
echo ""
echo -e "  ${B}🔗 ACCÈS LOCAL:${NC}"
echo "     Dashboard:  http://localhost:${PILOT_PORT:-8090}"
echo "     API:        http://localhost:8000"
echo "     API Docs:   http://localhost:8000/docs"
echo "     Health:     http://localhost:8000/health"
echo ""
echo -e "  ${B}🔗 ACCÈS RÉSEAU (autres machines):${NC}"
echo "     Dashboard:  http://${LOCAL_IP}:${PILOT_PORT:-8090}"
echo "     API:        http://${LOCAL_IP}:8000"
echo ""
echo -e "  ${B}📋 Comptes:${NC}"
echo "     admin@cortex-leman.com    / C0rt3xL3m4n!"
echo "     expert@dupont-comptable.fr / comptable"
echo "     avocat@martin-avocat.ch    / avocat"
echo "     medecin@hopital-geneve.ch  / sante"
echo "     analyste@ubank.ch          / banque"
echo "     cto@startup-paris.fr       / startup"
echo "     drh@groupe-rh.fr           / rh"
echo ""
echo -e "  ${B}📊 Monitoring:${NC}"
if [ "$MODE" = "dev" ]; then
    echo "     Prometheus: http://${LOCAL_IP}:9090"
    echo "     Grafana:    http://${LOCAL_IP}:3000 (admin/admin)"
fi
echo ""
echo -e "  ${B}🔧 Commandes utiles:${NC}"
echo "     Logs:    docker compose -f $COMPOSE_FILE logs -f api"
echo "     Arrêt:   docker compose -f $COMPOSE_FILE down"
echo "     Restart: docker compose -f $COMPOSE_FILE restart api"
echo "     Status:  docker compose -f $COMPOSE_FILE ps"
echo ""
echo -e "  ${B}🌐 Pour déployer sur une autre machine:${NC}"
echo "     1. Copier le projet: scp -r $ROOT user@AUTRE_IP:~/cortex-leman-v5"
echo "     2. Installer Docker: curl -fsSL https://get.docker.com | sh"
echo "     3. Lancer: bash scripts/deploy-full.sh --build"
echo "═══════════════════════════════════════════════════════════"
echo ""
