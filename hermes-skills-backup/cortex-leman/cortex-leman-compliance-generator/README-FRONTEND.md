# 🎉 CORTEX LEMAN - COMPLIANCE GENERATOR

**Générateur de posts de conformité RGPD/IA pour PME FR-CH - Complet**

---

## 📋 SOMMAIRE

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture](#architecture)
3. [Prérequis](#prérequis)
4. [Installation](#installation)
5. [Backend API](#backend-api)
6. [Frontend Next.js](#frontend-nextjs)
7. [Déploiement](#déploiement)
8. [Utilisation](#utilisation)
9. [Tests](#tests)
10. [Monitoring](#monitoring)

---

## 🎯 Vue d'ensemble

### Problème

Les PME FR-CH doivent publier sur leurs réseaux sociaux des contenus sur la conformité RGPD/IA, mais:
- Elles ne savent pas quoi écrire
- Elles n'ont pas d'expertise juridique
- Elles n'ont pas de visuels
- Elles manquent de temps

### Solution

**Cortex Leman Compliance Generator** - Application SaaS qui génère du contenu de conformité RGPD/IA en 60 secondes:

- **Posts professionnels** pour LinkedIn et Twitter
- **Visuels IA générés** (infographies, diagrammes)
- **Validation automatique** par Le Gardien des Normes
- **Sans expertise juridique ou marketing**

### Technologie

**Backend:**
- Python 3.11
- FastAPI
- OpenRouter (DeepSeek v3.2)
- Kie.ai (NanoBanana)
- Docker

**Frontend:**
- Next.js 15
- TypeScript
- Tailwind CSS
- Vercel

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  CORTEX LEMAN ECOSYSTEM                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              FRONTEND (Next.js)                     │  │
│  │  - Page accueil avec formulaire                      │  │
│  │  - Affichage des résultats                          │  │
│  │  - Copier/coller & téléchargement                    │  │
│  │  - Déployé sur Vercel                               │  │
│  └─────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              BACKEND (FastAPI)                       │  │
│  │  - API REST                                         │  │
│  │  - Intégration OpenRouter                          │  │
│  │  - Intégration Kie.ai                              │  │
│  │  - Le Narrateur (génération)                        │  │
│  │  - Le Gardien (validation)                          │  │
│  └─────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           ▼                                 │
│  ┌──────────────────┬──────────────────────────────┐    │
│  │                  │                              │    │
│  │  OPENROUTER      │         KIE.AI               │    │
│  │  (Texte)         │         (Image)              │    │
│  │  - DeepSeek      │         - NanoBanana          │    │
│  │  - Posts         │         - Visuels             │    │
│  └──────────────────┴──────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Prérequis

### Système

- Linux / macOS / Windows (WSL2)
- Docker & Docker Compose
- Node.js 18+ (pour le frontend)
- Python 3.11+ (pour le backend)

### API Keys

- **OpenRouter API Key** (requis)
  - Obtenir sur: https://openrouter.ai/keys
  - Modèle: DeepSeek v3.2

- **Kie.ai API Key** (fourni)
  - Clé: `[REDACTED-KIEAI-KEY]`

---

## 🚀 Installation

### Étape 1: Cloner le projet

```bash
cd ~/.hermes/skills/cortex-leman/cortex-leman-compliance-generator
```

### Étape 2: Configurer le backend

```bash
# Créer le fichier .env
cp .env.example .env

# Éditer .env et ajouter OPENROUTER_API_KEY
nano .env
```

**Contenu de `.env`:**
```bash
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
KIEAI_API_KEY=[REDACTED-KIEAI-KEY]
API_HOST=0.0.0.0
API_PORT=8000
```

### Étape 3: Installer les dépendances backend

```bash
pip install -r requirements.txt
```

### Étape 4: Installer les dépendances frontend

```bash
cd frontend
npm install
cd ..
```

### Étape 5: Lancer le backend

```bash
# En local
python api/main.py

# Avec Docker
docker-compose -f docker-compose.override.yml up -d
```

L'API sera accessible sur: `http://localhost:8000`

### Étape 6: Lancer le frontend

```bash
cd frontend
npm run dev
```

Le frontend sera accessible sur: `http://localhost:3000`

---

## 🔧 Backend API

### Endpoints

#### POST `/api/generate`

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

#### GET `/health`

Vérifie la santé de l'API.

#### GET `/docs`

Documentation Swagger/OpenAPI.

---

## 🎨 Frontend Next.js

### Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Layout principal
│   ├── page.tsx            # Page d'accueil
│   └── globals.css         # Styles globaux
├── components/
│   ├── ComplianceForm.tsx   # Formulaire de génération
│   ├── ResultDisplay.tsx   # Affichage des résultats
│   ├── Button.tsx          # Bouton réutilisable
│   ├── Label.tsx           # Label
│   ├── Textarea.tsx        # Zone de texte
│   ├── Select.tsx          # Menu déroulant
│   ├── Checkbox.tsx       # Case à cocher
│   ├── CopyButton.tsx      # Copier le texte
│   ├── DownloadButton.tsx   # Télécharger l'image
│   ├── ValidationBadge.tsx  # Badge de validation
│   └── LoadingSpinner.tsx   # Indicateur de chargement
├── types/
│   └── compliance.ts       # Types TypeScript
└── configuration
    ├── package.json
    ├── tsconfig.json
    ├── tailwind.config.ts
    ├── next.config.js
    └── vercel.json
```

### Variables d'environnement

Créer `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Lancer en développement

```bash
cd frontend
npm run dev
```

### Build pour production

```bash
cd frontend
npm run build
```

---

## 🌐 Déploiement

### Backend (Docker)

```bash
# Copier le fichier docker-compose.override.yml dans votre stack Docker Cortex Leman existant
# Puis lancer:
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

### Frontend (Vercel)

```bash
cd frontend

# Installer Vercel CLI
npm install -g vercel

# Se connecter
vercel login

# Déployer
vercel

# Variables d'environnement dans Vercel:
# - NEXT_PUBLIC_API_URL=https://api.cortex-leman.ch
```

### Domaine personnalisé

Dans les settings Vercel:
- Settings → Domains → Add Domain
- Ajouter votre domaine (ex: compliance.cortex-leman.ch)

---

## 📝 Utilisation

### Workflow

1. **Accéder à l'application**
   - Frontend: `http://localhost:3000` (dev) ou `https://compliance.cortex-leman.ch` (prod)
   - API: `http://localhost:8000` (dev) ou `https://api.cortex-leman.ch` (prod)

2. **Remplir le formulaire**
   - Sujet du post (ex: "Nouvelle obligation RGPD")
   - Plateformes (LinkedIn, Twitter)
   - Nombre d'images (1-4)
   - Ton du post (Professionnel, Accessible, etc.)

3. **Générer**
   - Cliquer sur "Générer le post"
   - Attendre ~60 secondes

4. **Récupérer le résultat**
   - Posts prêts à copier/coller
   - Images à télécharger
   - Validation de conformité

5. **Publier**
   - Copier les posts
   - Télécharger les images
   - Publier sur vos réseaux sociaux

---

## 🧪 Tests

### Backend

```bash
# Test du générateur
python scripts/compliance_generator.py

# Test OpenRouter
python scripts/openrouter_client.py

# Test Kie.ai
python scripts/kieai_client.py

# Test Gardien
python scripts/gardien_validator.py
```

### Frontend

```bash
cd frontend

# Tests
npm test

# Type check
npm run type-check
```

---

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### Stats API

```bash
curl http://localhost:8000/api/stats
```

### Logs Docker

```bash
docker logs -f cortex-leman-compliance-generator
```

### Grafana / Prometheus

Via le stack Cortex Leman existant.

---

## 🎯 Prochaines étapes

### Phase 3: Testing & Déploiement

1. **Tests complets**
   - Tests backend
   - Tests frontend
   - Tests E2E

2. **Déploiement production**
   - Backend Docker
   - Frontend Vercel
   - Domaine personnalisé

3. **Monitoring**
   - Grafana dashboards
   - Prometheus metrics
   - Logs centralisés

### Phase 4: Améliorations futures

1. **Nouvelles plateformes**
   - Instagram
   - Facebook

2. **Nouveaux formats**
   - Articles blog (2000 mots)
   - Infographies interactives

3. **Fonctionnalités avancées**
   - Scheduling automatique
   - Analytics & ROI
   - Multi-utilisateurs

---

## 📄 License

Cortex Leman - Audit RGPD-IA PME FR-CH
Copyright © 2026

---

## 🔗 Liens

- **Cortex Leman Main:** https://cortex-leman.ch
- **Documentation:** https://docs.cortex-leman.ch
- **OpenRouter:** https://openrouter.ai
- **Kie.ai:** https://kie.ai
- **Vercel:** https://vercel.com

---

**Créé avec ❤️ par Cortex Leman pour les PME FR-CH**
