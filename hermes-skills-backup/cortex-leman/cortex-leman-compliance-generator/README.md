# Cortex Leman Compliance Generator

Générateur de posts de conformité RGPD/IA pour PME FR-CH.

## 🎯 Vision

Permettre aux PME FR-CH de générer du contenu de conformité RGPD/IA de qualité professionnelle en 60 secondes, sans expertise juridique ou marketing.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│         CORTEX LEMAN COMPLIANCE GENERATOR                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              INPUT                                  │  │
│  │  - Brief: "Nouvelle obligation RGPD"               │  │
│  └─────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │         LE NARRATEUR AUGMENTÉ                         │  │
│  │         Génération de contenu marketing              │  │
│  └─────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │         LE GARDIEN DES NORMES                         │  │
│  │         Validation de conformité                     │  │
│  └─────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           ▼                                 │
│  ┌──────────────────┬──────────────────────────────┐    │
│  │                  │                              │    │
│  │  OPENROUTER      │         KIE.AI               │    │
│  │  (Texte)         │         (Image)              │    │
│  │  - DeepSeek v3.2 │         - NanoBanana          │    │
│  └──────────────────┴──────────────────────────────┘    │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              OUTPUT                                 │  │
│  │  - Post LinkedIn + Twitter                        │  │
│  │  - 1-4 visuels IA                                  │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Prérequis

- Python 3.11+
- Docker & Docker Compose
- Clé API OpenRouter
- Clé API Kie.ai (fournie: `[REDACTED-KIEAI-KEY]`)

## 🚀 Installation Rapide

### 1. Cloner le projet

```bash
cd ~/.hermes/skills/cortex-leman/cortex-leman-compliance-generator
```

### 2. Configurer les variables d'environnement

```bash
cp .env.example .env
# Éditer .env et ajouter OPENROUTER_API_KEY
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Lancer en local

```bash
python api/main.py
```

L'API sera accessible sur: `http://localhost:8000`

### 5. Lancer avec Docker

```bash
# Copier ce fichier dans votre stack Docker Cortex Leman existant
# Puis lancer:
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

## 📡 API Endpoints

### POST /api/generate

Génère des posts de conformité.

**Request:**
```json
{
  "brief": "Nouvelle obligation RGPD pour IA générative",
  "platforms": ["linkedin", "twitter"],
  "image_count": 2,
  "tone": "professional",
  "enable_validation": true
}
```

**Response:**
```json
{
  "success": true,
  "posts": {
    "linkedin": "🔒 RGPD & IA: Ce que les PME FR-CH doivent savoir...",
    "twitter": "🔒 RGPD & IA: Nouvelles obligations UE..."
  },
  "images": [
    {
      "url": "https://...",
      "type": "infography",
      "index": 1
    }
  ],
  "validation": {
    "linkedin": {
      "is_valid": true,
      "confidence": 0.95,
      "issues": []
    }
  },
  "metadata": {
    "brief": "Nouvelle obligation RGPD pour IA générative",
    "platforms": ["linkedin", "twitter"],
    "image_count": 2,
    "tone": "professional"
  },
  "timestamp": "2026-04-06T16:00:00.000000"
}
```

### GET /health

Vérifie la santé de l'API.

### GET /docs

Documentation Swagger/OpenAPI.

## 🧪 Tests

### Test du générateur

```bash
python scripts/compliance_generator.py
```

### Test des clients API

```bash
# Test OpenRouter
python scripts/openrouter_client.py

# Test Kie.ai
python scripts/kieai_client.py

# Test Gardien
python scripts/gardien_validator.py
```

## 🔧 Configuration

### Variables d'environnement

| Variable | Description | Requis |
|----------|-------------|--------|
| `OPENROUTER_API_KEY` | Clé API OpenRouter | Oui |
| `KIEAI_API_KEY` | Clé API Kie.ai | Non (défaut fournie) |
| `API_HOST` | Hôte de l'API | Non (0.0.0.0) |
| `API_PORT` | Port de l'API | Non (8000) |
| `ENABLE_VALIDATION` | Activer la validation | Non (true) |

### Modèles utilisés

- **Texte:** DeepSeek v3.2 (deepseek/deepseek-chat-v3)
- **Image:** NanoBanana (nano-banana)

## 📊 Agents Cortex Leman

### Le Narrateur Augmenté

Rôle: Génération de contenu marketing
- Entrée: Brief sur sujet RGPD/IA
- Sortie: Posts optimisés pour LinkedIn/Twitter
- Style: Professional, accessible, informatif

### Le Gardien des Normes

Rôle: Validation de conformité
- Entrée: Contenu généré
- Sortie: Validation OK ou corrections
- Contrôle: Exactitude juridique, termes RGPD

## 🎨 Frontend (À venir)

L'application Next.js sera créée dans une prochaine phase pour fournir:
- Interface utilisateur
- Formulaire de saisie
- Affichage des résultats
- Bouton copier/coller
- Téléchargement des images

## 📝 Documentation technique

- `scripts/openrouter_client.py` - Client OpenRouter
- `scripts/kieai_client.py` - Client Kie.ai
- `scripts/gardien_validator.py` - Validateur de conformité
- `scripts/compliance_generator.py` - Orchestrateur principal
- `api/main.py` - API FastAPI

## 🔐 Sécurité

- Clés API stockées dans variables d'environnement
- CORS configuré (à restreindre en production)
- Validation automatique du contenu
- Rate limiting (à configurer via Nginx)

## 🚀 Déploiement

### Local

```bash
python api/main.py
```

### Docker

```bash
docker-compose up -d
```

### Production

Via le stack Docker Cortex Leman existant:
1. Ajouter le service `compliance-generator`
2. Configurer Nginx pour le proxy
3. Configurer le monitoring (Grafana/Prometheus)

## 📈 Monitoring

Les métriques sont disponibles via:
- `/health` - Health check
- `/api/stats` - Statistiques de l'API
- Grafana/Prometheus (via le stack Cortex Leman)

## 🤝 Contribution

Ce projet fait partie de l'écosystème Cortex Leman. Pour contribuer:

1. Suivre les guidelines de Cortex Leman
2. Tester les pull requests
3. Documenter les changements

## 📄 Licence

Cortex Leman - Audit RGPD-IA PME FR-CH
Copyright © 2026

## 🔗 Liens

- [Cortex Leman Main](https://cortex-leman.ch)
- [Documentation Cortex Leman](https://docs.cortex-leman.ch)
- [OpenRouter](https://openrouter.ai)
- [Kie.ai](https://kie.ai)

---

**Créé avec ❤️ par Cortex Leman pour les PME FR-CH**
