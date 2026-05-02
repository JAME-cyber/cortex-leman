#!/bin/bash
# Cortex Leman v5 — Déploiement Edge (Mode Haute Protection)
set -e

MODE="${1:-haute_protection}"
VERTICAL="${2:-comptable}"

echo "🧠 Cortex Leman v5 — Déploiement Edge"
echo "   Mode: ${MODE}"
echo "   Verticale: ${VERTICAL}"
echo ""

if [ "${MODE}" = "haute_protection" ]; then
    echo "🔒 Mode Haute Protection activé"
    echo "   - Infrastructure locale uniquement"
    echo "   - Aucune connexion sortante"
    echo "   - LLM: Ollama local"
    echo ""
    
    # 1. Installer K3s
    bash edge/k3s-install.sh
    
    # 2. Installer Ollama
    bash edge/ollama-setup.sh
    
    # 3. Déployer les manifests
    echo "📦 Déploiement des agents..."
    k3s kubectl apply -f edge/manifests/
    
    # 4. Configurer la verticale
    k3s kubectl set env deployment/mediator ACTIVE_VERTICAL="${VERTICAL}" -n cortex-leman
    
    echo ""
    echo "✅ Déploiement Haute Protection terminé"
    echo "   Vérifier: k3s kubectl get pods -n cortex-leman"

elif [ "${MODE}" = "standard" ]; then
    echo "📋 Mode Standard activé"
    echo "   - Cloud privé / Kubernetes mutualisé"
    echo "   - LLM: OpenRouter ou local"
    echo ""
    
    # Déploiement Docker Compose
    docker compose up -d --build
    
    echo ""
    echo "✅ Déploiement Standard terminé"
    echo "   API: http://localhost:8000"
else
    echo "❌ Mode inconnu: ${MODE}"
    echo "   Utiliser: standard | haute_protection"
    exit 1
fi
