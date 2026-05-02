#!/bin/bash
# ============================================================
# Cortex Leman v5 — Installation Ollama (LLM local)
# Mode Haute Protection: Aucune requête LLM externe
# ============================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}Cortex Leman v5 — Ollama Setup${NC}"
echo -e "${CYAN}LLM local pour Mode Haute Protection${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

# === Configuration ===
OLLAMA_DIR="${OLLAMA_DIR:-/opt/cortex-leman/ollama}"
MODEL_NAME="${MODEL_NAME:-mistral:7b}"
GPU_TYPE="${GPU_TYPE:-auto}"

echo -e "${YELLOW}Configuration:${NC}"
echo "  Répertoire: ${OLLAMA_DIR}"
echo "  Modèle: ${MODEL_NAME}"
echo "  GPU: ${GPU_TYPE}"
echo ""

# === Vérifier GPU ===
echo -e "${YELLOW}[1/5] Vérification GPU...${NC}"

if [[ "${GPU_TYPE}" == "auto" ]]; then
    if command -v nvidia-smi &>/dev/null; then
        GPU_TYPE="nvidia"
        GPU_INFO=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader)
        echo -e "${GREEN}  ✓ GPU NVIDIA détecté: ${GPU_INFO}${NC}"
    elif command -v rocm-smi &>/dev/null; then
        GPU_TYPE="amd"
        echo -e "${GREEN}  ✓ GPU AMD ROCm détecté${NC}"
    else
        GPU_TYPE="cpu"
        echo -e "${YELLOW}  ⚠ Pas de GPU détecté — utilisation CPU${NC}"
        echo -e "${YELLOW}  ⚠ Les performances seront limitées${NC}"
    fi
fi

# === Installation Ollama ===
echo -e "${YELLOW}[2/5] Installation Ollama...${NC}"

if command -v ollama &>/dev/null; then
    echo -e "${GREEN}  ✓ Ollama déjà installé: $(ollama --version 2>/dev/null || echo 'version inconnue')${NC}"
else
    curl -fsSL https://ollama.com/install.sh | sh
    echo -e "${GREEN}  ✓ Ollama installé${NC}"
fi

# === Configuration ===
echo -e "${YELLOW}[3/5] Configuration Ollama...${NC}"

mkdir -p "${OLLAMA_DIR}"/{models,logs}

# Configuration systemd pour démarrage auto
cat > /etc/systemd/system/ollama-cortex.service << EOF
[Unit]
Description=Ollama LLM Server (Cortex Leman)
After=network.target

[Service]
Type=simple
Environment=OLLAMA_MODELS=${OLLAMA_DIR}/models
Environment=OLLAMA_HOST=127.0.0.1:11434
Environment=OLLAMA_ORIGINS=*
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=5
StandardOutput=append:${OLLAMA_DIR}/logs/ollama.log
StandardError=append:${OLLAMA_DIR}/logs/ollama-error.log

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ollama-cortex
systemctl start ollama-cortex

echo -e "${GREEN}  ✓ Service systemd configuré${NC}"

# === Téléchargement modèle ===
echo -e "${YELLOW}[4/5] Téléchargement modèle ${MODEL_NAME}...${NC}"
echo -e "${YELLOW}  (Première installation — peut prendre plusieurs minutes)${NC}"

# Attendre qu'Ollama soit prêt
for i in $(seq 1 30); do
    if curl -s http://127.0.0.1:11434/api/tags &>/dev/null; then
        break
    fi
    sleep 1
done

# Télécharger le modèle
ollama pull "${MODEL_NAME}"

echo -e "${GREEN}  ✓ Modèle ${MODEL_NAME} téléchargé${NC}"

# === Vérification ===
echo -e "${YELLOW}[5/5] Vérification...${NC}"

# Test de génération
TEST_RESPONSE=$(curl -s http://127.0.0.1:11434/api/generate -d '{
    "model": "'"${MODEL_NAME}"'",
    "prompt": "Cortex Leman test: répondre OK",
    "stream": false
}' 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('response','FAIL')[:50])" 2>/dev/null || echo "FAIL")

if [[ "${TEST_RESPONSE}" != "FAIL" ]]; then
    echo -e "${GREEN}  ✓ Ollama opérationnel — réponse reçue${NC}"
else
    echo -e "${RED}  ✗ Ollama ne répond pas${NC}"
    echo -e "${YELLOW}  Vérifier: systemctl status ollama-cortex${NC}"
fi

# === Modèles additionnels recommandés ===
echo ""
echo -e "${CYAN}Modèles disponibles pour installation:${NC}"
echo "  ollama pull mistral:7b       — Recommandé (FR/CH)"
echo "  ollama pull llama3:8b        — Alternative"
echo "  ollama pull mistral-nemo:12b — Meilleure qualité (12GB VRAM)"
echo "  ollama pull codestral:22b    — Code + analyse (24GB VRAM)"
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Ollama Setup TERMINÉ${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "Configuration:"
echo -e "  URL: ${CYAN}http://127.0.0.1:11434${NC}"
echo -e "  Modèle: ${CYAN}${MODEL_NAME}${NC}"
echo -e "  Stockage: ${CYAN}${OLLAMA_DIR}${NC}"
echo -e "  Logs: ${CYAN}${OLLAMA_DIR}/logs/${NC}"
