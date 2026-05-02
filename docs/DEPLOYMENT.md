# Cortex Leman v5 — Guide de Déploiement

## Table des matières

1. [Mode Standard (Cloud)](#mode-standard)
2. [Mode Haute Protection (Edge)](#mode-haute-protection)
3. [Configuration LLM](#configuration-llm)
4. [Intégration n8n](#intégration-n8n)
5. [Endpoints API](#endpoints-api)

---

## Mode Standard

Pour: Startups, RH, Comptables (données non sensibles)

```bash
# 1. Cloner
cd cortex-leman-v5

# 2. Configurer
cp .env.example .env
# Éditer .env avec vos clés API

# 3. Lancer l'infrastructure
docker compose up -d nats redis

# 4. Installer les dépendances
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 5. Lancer l'API
NATS_URL=nats://localhost:4222 \
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

## Mode Haute Protection

Pour: Avocats, Banques, Santé (données régulées)

```bash
# 1. Installer K3s (appliance 3 nœuds)
sudo bash edge/k3s-install.sh

# 2. Installer Ollama (LLM local)
sudo bash edge/ollama-setup.sh

# 3. Configurer le mode
export APP_MODE=haute_protection
export LLM_PROVIDER=ollama
export LLM_BASE_URL=http://localhost:11434

# 4. Déployer les agents
k3s kubectl apply -f edge/manifests/

# 5. Vérifier
k3s kubectl get pods -n cortex-leman
```

## Configuration LLM

### OpenRouter (Mode Standard)

```env
LLM_PROVIDER=openrouter
LLM_MODEL=mistralai/mistral-small-3.1-24b-instruct
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=sk-or-...
```

### Ollama (Mode Haute Protection)

```env
LLM_PROVIDER=ollama
LLM_MODEL=mistral:7b
LLM_BASE_URL=http://localhost:11434
```

Modèles recommandés:
| Modèle | VRAM | Qualité | Usage |
|--------|------|---------|-------|
| `mistral:7b` | 6 GB | Bon | Usage général |
| `llama3:8b` | 6 GB | Bon | Alternative |
| `mistral-nemo:12b` | 10 GB | Très bon | Analyse juridique |
| `codestral:22b` | 16 GB | Excellent | Analyse approfondie |

## Intégration n8n

### Configuration

```env
N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=your-n8n-api-key
N8N_WEBHOOK_BASE=http://localhost:5678/webhook
```

### Webhooks par verticale

Chaque verticale a des workflows prédéfinis accessibles via:
```
POST {N8N_WEBHOOK_BASE}/{vertical}/{workflow_name}
```

Exemples:
- `POST /webhook/comptable/cloture_annuelle`
- `POST /webhook/avocat/dossier_management`
- `POST /webhook/rh/onboarding`

## Endpoints API

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/intentions` | Créer une intention |
| GET | `/api/v1/intentions/{id}` | Statut d'une intention |
| GET | `/api/v1/journal` | Consulter le journal |
| GET | `/api/v1/journal/verify` | Vérifier l'intégrité |
| GET | `/api/v1/mediator/rules` | Règles par verticale |
| GET | `/api/v1/mediator/conflicts` | Conflits actifs |
| GET | `/api/v1/arbitrations` | Arbitrages en attente |
| POST | `/api/v1/arbitrations/{id}/decide` | Décision humaine |
| GET | `/api/v1/compliance/report/daily` | Rapport quotidien |
| GET | `/api/v1/compliance/report/monthly` | Rapport mensuel |
| GET | `/api/v1/agents/status` | Statut agents + circuit breakers |
| GET | `/api/v1/llm/health` | Vérifier provider LLM |
| POST | `/api/v1/llm/generate` | Générer réponse LLM |
| GET | `/api/v1/n8n/health` | Vérifier n8n |
| GET | `/api/v1/n8n/workflows` | Workflows disponibles |
| POST | `/api/v1/n8n/trigger` | Déclencher workflow |
| POST | `/api/v1/vault/clients` | Créer espace client |
| POST | `/api/v1/vault/documents` | Stocker document |
| GET | `/api/v1/vault/search` | Rechercher documents |
| GET | `/api/v1/vault/stats` | Statistiques vault |
| POST | `/api/v1/vault/regulatory/load` | Charger textes réglementaires |
