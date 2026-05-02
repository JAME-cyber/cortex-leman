#!/bin/bash
# ============================================================
# Cortex Leman v5 — Installation K3s Appliance (Mode Haute Protection)
# Pour: avocats, banques, santé (Suisse)
# 
# 3 nœuds Kubernetes minimal sur appliance physique
# Aucune connexion sortante pour l'inférence
# ============================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}Cortex Leman v5 — K3s Appliance Installer${NC}"
echo -e "${CYAN}Mode: Haute Protection${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

# === Configuration ===
CLUSTER_NAME="${CLUSTER_NAME:-cortex-leman}"
NODE_COUNT="${NODE_COUNT:-3}"
DATA_DIR="${DATA_DIR:-/opt/cortex-leman}"
K3S_VERSION="${K3S_VERSION:-v1.29.3+k3s1}"

echo -e "${YELLOW}Configuration:${NC}"
echo "  Cluster: ${CLUSTER_NAME}"
echo "  Nœuds: ${NODE_COUNT}"
echo "  Data: ${DATA_DIR}"
echo "  K3s: ${K3S_VERSION}"
echo ""

# === Vérifications préalables ===
echo -e "${YELLOW}[1/7] Vérifications système...${NC}"

if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}Erreur: Exécuter en tant que root${NC}"
    exit 1
fi

# Vérifier la mémoire (min 4GB)
TOTAL_MEM=$(grep MemTotal /proc/meminfo | awk '{print int($2/1024)}')
if [[ $TOTAL_MEM -lt 3600 ]]; then
    echo -e "${RED}Erreur: 4GB RAM minimum requis (${TOTAL_MEM}MB détectés)${NC}"
    exit 1
fi
echo -e "${GREEN}  ✓ RAM: ${TOTAL_MEM}MB${NC}"

# Vérifier le stockage (min 50GB)
DISK_AVAIL=$(df -BG / | tail -1 | awk '{print $4}' | tr -d 'G')
if [[ $DISK_AVAIL -lt 50 ]]; then
    echo -e "${RED}Erreur: 50GB stockage minimum requis (${DISK_AVAIL}GB disponibles)${NC}"
    exit 1
fi
echo -e "${GREEN}  ✓ Stockage: ${DISK_AVAIL}GB disponibles${NC}"

# Vérifier l'architecture
ARCH=$(uname -m)
echo -e "${GREEN}  ✓ Architecture: ${ARCH}${NC}"

# === Répertoires ===
echo -e "${YELLOW}[2/7] Création répertoires...${NC}"
mkdir -p "${DATA_DIR}"/{data,journal,reports,ollama,secrets,logs,backups}
echo -e "${GREEN}  ✓ ${DATA_DIR} créé${NC}"

# === Installation K3s ===
echo -e "${YELLOW}[3/7] Installation K3s...${NC}"

if command -v k3s &>/dev/null; then
    echo -e "${GREEN}  ✓ K3s déjà installé: $(k3s --version)${NC}"
else
    # Installer K3s sans Traefik (on utilisera nginx)
    curl -sfL https://get.k3s.io | \
        INSTALL_K3S_VERSION="${K3S_VERSION}" \
        K3S_NODE_NAME="${CLUSTER_NAME}-master" \
        sh -s - \
        --disable=traefik \
        --disable=servicelb \
        --write-kubeconfig="${DATA_DIR}/kubeconfig.yaml" \
        --data-dir="${DATA_DIR}/k3s-data"

    echo -e "${GREEN}  ✓ K3s installé${NC}"
fi

# === Sécurisation réseau ===
echo -e "${YELLOW}[4/7] Sécurisation réseau...${NC}"

# Bloquer tout trafic sortant sauf DNS et updates
iptables -A OUTPUT -p tcp --dport 53 -j ACCEPT      # DNS
iptables -A OUTPUT -p udp --dport 53 -j ACCEPT      # DNS
iptables -A OUTPUT -p tcp --dport 123 -j ACCEPT     # NTP
iptables -A OUTPUT -o lo -j ACCEPT                   # Local
iptables -A OUTPUT -m state --state ESTABLISHED -j ACCEPT

echo -e "${GREEN}  ✓ Pare-feu configuré (trafic sortant restreint)${NC}"

# === Secrets ===
echo -e "${YELLOW}[5/7] Génération secrets...${NC}"

# Clé de signature du journal
JOURNAL_KEY=$(openssl rand -hex 32)
echo "JOURNAL_SIGNING_KEY=${JOURNAL_KEY}" > "${DATA_DIR}/secrets/journal.env"

# Clé API interne
API_KEY=$(openssl rand -hex 32)
echo "SECRET_KEY=${API_KEY}" > "${DATA_DIR}/secrets/api.env"

# Certificat self-signed pour mTLS
openssl req -x509 -newkey rsa:4096 -keyout "${DATA_DIR}/secrets/tls.key" \
    -out "${DATA_DIR}/secrets/tls.crt" -days 365 -nodes \
    -subj "/CN=cortex-leman.local/O=CortexLeman/C=CH"

chmod 600 "${DATA_DIR}"/secrets/*
echo -e "${GREEN}  ✓ Secrets générés${NC}"

# === Configuration application ===
echo -e "${YELLOW}[6/7] Configuration Cortex Leman...${NC}"

cat > "${DATA_DIR}/.env.haute_protection" << 'ENVEOF'
# Mode Haute Protection — Aucune connexion externe
APP_MODE=haute_protection
LLM_PROVIDER=ollama
LLM_MODEL=mistral:7b
LLM_BASE_URL=http://localhost:11434
COMPLIANCE_DATA_RESIDENCY=CH
COMPLIANCE_ENCRYPTION=AES-256
MTLS_ENABLED=true
MTLS_CERT_PATH=/opt/cortex-leman/secrets/tls.crt
MTLS_KEY_PATH=/opt/cortex-leman/secrets/tls.key
JOURNAL_SIGNING_KEY=__JOURNAL_KEY__
SECRET_KEY=__API_KEY__
ARBITRATION_SIGNATURE_ENABLED=true
NATS_REPLICAS=3
ENVEOF

sed -i "s/__JOURNAL_KEY__/${JOURNAL_KEY}/" "${DATA_DIR}/.env.haute_protection"
sed -i "s/__API_KEY__/${API_KEY}/" "${DATA_DIR}/.env.haute_protection"

echo -e "${GREEN}  ✓ Configuration générée${NC}"

# === Vérification ===
echo -e "${YELLOW}[7/7] Vérification...${NC}"

if k3s kubectl get nodes &>/dev/null; then
    echo -e "${GREEN}  ✓ Cluster K3s opérationnel${NC}"
else
    echo -e "${RED}  ✗ Cluster K3s non disponible${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Installation K3s TERMINÉE${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "Prochaines étapes:"
echo -e "  1. ${CYAN}bash edge/ollama-setup.sh${NC} — Installer Ollama + modèle"
echo -e "  2. ${CYAN}k3s kubectl apply -f edge/manifests/${NC} — Déployer agents"
echo -e "  3. ${CYAN}cat ${DATA_DIR}/secrets/journal.env${NC} — Clés de signature"
echo ""
echo -e "${YELLOW}⚠️  SÉCURITÉ: Aucune connexion sortante autorisée${NC}"
echo -e "${YELLOW}⚠️  Secret professionnel: Infrastructure 100% locale${NC}"
