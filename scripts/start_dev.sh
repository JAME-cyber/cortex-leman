#!/bin/bash
# Cortex Leman v5 — Démarrage développement
set -e

echo "🧠 Cortex Leman v5 — Démarrage développement"
echo ""

# Vérifier les dépendances
if ! command -v docker &>/dev/null; then
    echo "❌ Docker non installé"
    exit 1
fi

# Copier .env si nécessaire
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ .env créé depuis .env.example"
fi

# Créer les répertoires de données
mkdir -p data/{journal,reports,precedents}

# Démarrer l'infrastructure
echo "📦 Démarrage NATS + Redis..."
docker compose up -d nats redis

# Attendre que NATS soit prêt
echo "⏳ Attente NATS..."
for i in $(seq 1 30); do
    if docker compose exec -T nats wget --spider -q http://localhost:8222/healthz 2>/dev/null; then
        break
    fi
    sleep 1
done

echo "✅ Infrastructure prête"
echo ""
echo "🚀 Démarrage API..."
echo "   → http://localhost:8000"
echo "   → Docs: http://localhost:8000/docs"
echo "   → Health: http://localhost:8000/health"
echo ""

# Démarrer l'API
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
