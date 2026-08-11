# 📦 DEPLOYMENT GUIDE - CORTEX LEMAN COMPLIANCE GENERATOR

Guide complet de déploiement pour Cortex Leman Compliance Generator.

---

## 🎯 Vue d'ensemble

Ce guide couvre le déploiement complet de:
1. **Backend API** (FastAPI + Docker)
2. **Frontend** (Next.js + Vercel)

---

## 🐋 PARTIE 1: BACKEND (DOCKER)

### Étape 1: Prérequis

- Docker & Docker Compose installés
- Clé API OpenRouter
- Stack Docker Cortex Leman existante

### Étape 2: Configuration

```bash
cd ~/.hermes/skills/cortex-leman/cortex-leman-compliance-generator

# Créer le fichier .env
cp .env.example .env

# Éditer .env
nano .env
```

**Ajouter:**
```bash
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
KIEAI_API_KEY=[REDACTED-KIEAI-KEY]
```

### Étape 3: Intégration Stack Docker

#### Option A: Intégrer dans stack existant

1. Copier `docker-compose.override.yml` dans votre stack Docker Cortex Leman
2. Copier le dossier de l'application dans le stack
3. Ajouter la configuration Nginx

#### Option B: Stack indépendant

```bash
# Construire l'image Docker
docker build -t cortex-leman-compliance-generator .

# Lancer le container
docker run -d \
  -p 8001:8000 \
  --name cortex-leman-compliance-generator \
  -e OPENROUTER_API_KEY=your_key_here \
  -e KIEAI_API_KEY=[REDACTED-KIEAI-KEY] \
  cortex-leman-compliance-generator
```

### Étape 4: Vérifier le déploiement

```bash
# Health check
curl http://localhost:8001/health

# Documentation API
open http://localhost:8001/docs

# Stats API
curl http://localhost:8001/api/stats
```

### Étape 5: Configuration Nginx

Ajouter la configuration Nginx:

```nginx
# Upstream pour le service compliance-generator
upstream compliance_generator {
    server compliance-generator:8000;
}

# Location block pour l'API
location /api/compliance {
    proxy_pass http://compliance_generator/api;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### Étape 6: Monitoring

Grafana / Prometheus (via stack Cortex Leman):
- Health checks
- Response times
- Error rates
- API usage

---

## 🌐 PARTIE 2: FRONTEND (VERCEL)

### Étape 1: Prérequis

- Compte Vercel
- Node.js 18+
- Git repository

### Étape 2: Préparation

```bash
cd ~/.hermes/skills/cortex-leman/cortex-leman-compliance-generator/frontend

# Installer les dépendances
npm install

# Build
npm run build
```

### Étape 3: Déploiement avec Vercel CLI

```bash
# Installer Vercel CLI
npm install -g vercel

# Se connecter
vercel login

# Déployer
vercel

# Questions Vercel:
# - Set up and deploy: Yes
# - Which scope: votre compte
# - Link to existing project: No
# - Project name: cortex-leman-compliance-generator
# - Directory: . (current)
# - Override settings: No
```

### Étape 4: Configuration Vercel

Dans le dashboard Vercel:
- Settings → Environment Variables
- Ajouter:
  - `NEXT_PUBLIC_API_URL` = `https://api.cortex-leman.ch`

### Étape 5: Domaine personnalisé

Dans Vercel:
- Settings → Domains → Add Domain
- Ajouter votre domaine: `compliance.cortex-leman.ch`
- Suivre les instructions DNS

### Étape 6: Vérifier le déploiement

```bash
# Ouvrir le site
open https://compliance.cortex-leman.ch

# Vérifier l'intégration API
curl https://compliance.cortex-leman.ch
```

---

## 🧪 PARTIE 3: TESTING

### Backend Tests

```bash
# Test du générateur
cd ~/.hermes/skills/cortex-leman/cortex-leman-compliance-generator
python scripts/compliance_generator.py

# Vérifier la réponse
curl -X POST http://localhost:8001/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "brief": "Nouvelle obligation RGPD pour IA générative",
    "platforms": ["linkedin"],
    "image_count": 1,
    "tone": "professional"
  }'
```

### Frontend Tests

```bash
cd frontend

# Tests unitaires
npm test

# Type check
npm run type-check

# Lancer en dev
npm run dev
```

### E2E Tests (futur)

```bash
# Playwright / Cypress
npm run test:e2e
```

---

## 📊 PARTIE 4: MONITORING

### Health Checks

```bash
# Backend
curl https://api.cortex-leman.ch/health

# Frontend
curl https://compliance.cortex-leman.ch
```

### Logs

```bash
# Backend (Docker)
docker logs -f cortex-leman-compliance-generator

# Frontend (Vercel)
vercel logs
```

### Metrics

- **Grafana**: Dashboard Cortex Leman
- **Prometheus**: Metrics collection
- **Vercel Analytics**: Frontend metrics

### Alerts

- Uptime monitoring
- API response time > 5s
- Error rate > 5%
- API key invalid

---

## 🔐 PARTIE 5: SÉCURITÉ

### API Keys

- Stocker dans variables d'environnement
- Ne jamais commit dans le repository
- Rotate régulièrement
- Limit spend limits (OpenRouter: $5)

### CORS

Backend FastAPI:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://compliance.cortex-leman.ch"],  # Restreindre
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Rate Limiting

Configuré via Nginx:
```nginx
limit_req_zone $binary_remote_addr zone=compliance:10m rate=10r/m;

location /api/compliance {
    limit_req zone=compliance burst=20 nodelay;
    ...
}
```

### HTTPS

- **Backend**: Certificat SSL (Let's Encrypt via Nginx)
- **Frontend**: HTTPS par défaut sur Vercel

---

## 🚨 PARTIE 6: TROUBLESHOOTING

### Erreurs communes

#### Backend: API Key invalide

```bash
# Symptôme: 401 Unauthorized
# Solution: Vérifier OPENROUTER_API_KEY
echo $OPENROUTER_API_KEY
```

#### Backend: Port déjà utilisé

```bash
# Symptôme: Error starting server
# Solution: Changer le port ou kill le process
lsof -i :8000
kill -9 <PID>
```

#### Frontend: API inaccessible

```bash
# Symptôme: Erreur de connexion
# Solution: Vérifier NEXT_PUBLIC_API_URL
cat frontend/.env.local
```

#### Vercel: Build failed

```bash
# Symptôme: Build échoue
# Solution: Vérifier les logs
vercel logs --build

# Solutions courantes:
# - Node version incompatible
# - Dependencies manquantes
# - TypeScript errors
```

---

## 📈 PARTIE 7: SCALING

### Backend Scaling

```yaml
# docker-compose.yml
services:
  compliance-generator:
    deploy:
      replicas: 3  # 3 instances
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

### Frontend Scaling

Vercel gère automatiquement le scaling:
- Edge network
- CDN global
- Auto-scaling

---

## 🔄 PARTIE 8: UPDATES

### Backend Update

```bash
# Pull changes
git pull

# Rebuild
docker-compose build compliance-generator

# Restart
docker-compose up -d compliance-generator
```

### Frontend Update

```bash
# Vercel auto-deploy sur git push
git push origin main

# Ou manuel:
vercel --prod
```

---

## 📋 CHECKLIST DE DÉPLOIEMENT

- [ ] Backend Docker construit
- [ ] Backend running sur port 8001
- [ ] Health check API OK
- [ ] Nginx configuré
- [ ] Frontend build succès
- [ ] Frontend déployé sur Vercel
- [ ] Domaine personnalisé configuré
- [ ] DNS propagé
- [ ] HTTPS validé
- [ ] Tests E2E passés
- [ ] Monitoring actif
- [ ] Logs accessibles
- [ ] Alerts configurés

---

## 🎞️ PARTIE 9: ROLLBACK

### Backend Rollback

```bash
# Docker
docker-compose down
docker-compose up -d

# Git
git checkout <previous-commit>
docker-compose build
docker-compose up -d
```

### Frontend Rollback

```bash
# Vercel
vercel rollback <deployment-url>

# Git
git checkout <previous-commit>
git push
vercel --prod
```

---

## 📞 SUPPORT

- **Documentation**: https://docs.cortex-leman.ch
- **Issues**: GitHub Issues
- **Email**: support@cortex-leman.ch

---

**Créé avec ❤️ par Cortex Leman**
