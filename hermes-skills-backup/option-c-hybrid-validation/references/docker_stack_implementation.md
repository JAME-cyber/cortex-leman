---
name: Cortex Leman Docker Infrastructure
category: cortex-leman
description: Infrastructure Docker setup, debugging, and deployment for Cortex Leman Option C (Hybrid) stack. Covers Docker Compose v2, dependency conflicts, port resolution, and container state troubleshooting.

---

# CORTEX LEMAN DOCKER INFRASTRUCTURE

## RÔLE
Infrastructure Engineer pour Cortex Leman. Setup, build, debug et validation du stack Docker Option C (Hybrid).

## CONTEXTE
Option C = Stack Docker local pour validation business avant déploiement production. 9 services: API, Orchestrator, Worker, Vault, Nginx, PostgreSQL, Redis, Prometheus, Grafana.

## PREREQUIS
- Docker 29.3.1+
- Docker Compose v5.1.1+ (toujours `docker compose`, PAS `docker-compose`)
- Python 3.11-slim comme base image
- Ports libres: 80 (nginx), 8000 (API), 8001 (Vault), 3000 (Grafana), 9090 (Prometheus), 5432 (PostgreSQL), 6379 (Redis)

## WORKFLOW

### 1. INITIAL BUILD
```bash
cd /home/tars/.hermes/cortex-leman
./scripts/docker_start.sh dev
```

**ATTENTION:** Script utilise `docker compose` (v2), PAS `docker-compose` (legacy).

### 2. DEBUGGER LES ERREURS DE BUILD

#### Erreur: "No such file or directory" pour COPY
**Cause:** Répertoire ou fichier manquant dans le build context Docker.

**Solution 1:** Créer les fichiers Python manquants
```bash
mkdir -p cortex_leman/api cortex_leman/orchestrator cortex_leman/worker cortex_leman/knowledge_vault
touch cortex_leman/__init__.py
touch cortex_leman/api/__init__.py cortex_leman/api/main.py
touch cortex_leman/orchestrator/__init__.py cortex_leman/orchestrator/main.py
touch cortex_leman/worker/__init__.py cortex_leman/worker/main.py
touch cortex_leman/knowledge_vault/__init__.py cortex_leman/knowledge_vault/main.py
```

**Solution 2:** Corriger les Dockerfiles - utiliser les bons chemins
```dockerfile
# MAUVAIS
COPY api/ /app/api/

# BON
COPY cortex_leman/ /app/cortex_leman/
```

#### Erreur: "SyntaxError: invalid character in identifier"
**Cause:** Guillemets français `"` et `"` dans fichiers Python.

**Solution:** Recréer les fichiers avec guillemets standards `"` et `"`.
- Éviter de copier-coller depuis des éditeurs qui convertissent automatiquement les guillemets
- Utiliser des guillemets doubles standards `"`, PAS de guillemets typographiques

#### Erreur: "RuntimeError: Form data requires 'python-multipart' to be installed"
**Cause:** Dépendance manquante dans requirements.

**Solution:** Ajouter `python-multipart==0.0.6` au fichier requirements concerné.

### 3. RÉSOUDRE LES CONFLITS DE DÉPENDANCES

#### Conflit Celery/Redis
**Erreur:** `celery[redis]==5.3.4` vs `redis==5.0.1` - "ResolutionImpossible"

**Cause:** Celery 5.3.4 nécessite `redis != 4.5.5, < 5.0.0, >= 4.5.2`

**Solution:** Retirer `redis==5.0.1` explicitement du requirements. Celery[redis] gérera les dépendances automatiquement.

```bash
# MAUVAIS
celery[redis]==5.3.4
redis==5.0.1

# BON
celery[redis]==5.3.4
# (redis installé automatiquement par celery[redis])
```

#### Package inexistant
**Erreur:** `Could not find a version that satisfies the requirement python-cors==1.0.0`

**Cause:** Package n'existe pas ou mauvaise version.

**Solution 1:** Changer le package
- `python-cors==1.0.0` → `fastapi-cors` (vérifier la version disponible)

**Solution 2:** Retirer si non nécessaire
- FastAPI a un support CORS intégré depuis v0.68.0
- Gérer CORS directement dans l'application avec `CORSMiddleware`

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. RÉSOUDRE LES CONFLITS DE PORTS

#### Erreur: "address already in use"
**Cause:** Port déjà utilisé par un autre conteneur.

**Diagnostic:**
```bash
# Identifier le conteneur conflictuel
docker ps --format "table {{.Names}}\t{{.Ports}}" | grep ":80->"

# Arrêter le conteneur conflictuel
docker stop <container_name>
```

**Exemple:** Keycloak utilisait le port 8080 → conflit avec nginx
```bash
docker stop keycloak
docker compose up -d nginx
```

### 5. DEBUGGER LES CONTENEURS

#### Conteneur en état "Restarting"
**Diagnostic:**
```bash
# Vérifier le status
docker ps --filter name=<container> --format "{{.Status}}: {{.Ports}}"

# Voir les logs
docker logs <container> --tail 50

# Voir les logs en continu
docker logs <container> --follow
```

#### Relancer un conteneur sans rebuild complet
```bash
# Option 1: Restart rapide
docker compose restart <service>

# Option 2: Recrée le conteneur (mais garde l'image)
docker compose up -d --force-recreate <service>

# Option 3: Rebuild sans cache (si modifications requirements)
docker compose build --no-cache <service> && docker compose up -d <service>
```

### 6. NGINX GATEWAY TROUBLESHOOTING

#### Erreur: "host not found in upstream" nginx restart loop
**Symptôme:** Nginx container en boucle de redémarrage avec erreur `host not found in upstream "api:8000"`

**Cause:** Problème de résolution DNS Docker entre conteneurs. Nginx essaie de résoudre le nom d'hôte au démarrage mais le DNS Docker interne ne répond pas correctement.

**Diagnostic:**
```bash
# Voir les logs nginx
docker logs cortex-leman-nginx --tail 30

# Vérifier si le conteneur est bien dans le réseau
docker network inspect cortex-leman_cortex-network | grep api

# Tester la résolution DNS depuis nginx
docker exec cortex-leman-nginx nslookup api 127.0.0.11
```

**Solution 1: Utiliser IP directe (RECOMMANDÉ)**
Remplacer les hostnames par les IP fixes dans `nginx/nginx.conf`:

```nginx
# Dans location /api/ sections:
# AVANT (problématique)
proxy_pass http://api:8000/;

# APRÈS (solution)
proxy_pass http://172.16.1.7:8000/;
```

**Trouver les IP des conteneurs:**
```bash
docker inspect cortex-leman-api --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'
# => 172.16.1.7
```

**Solution 2: Simplifier la configuration**
Supprimer les blocs `upstream` et utiliser directement les hostnames/IP dans les blocs `location`:

```nginx
# MAUVAIS (bloque nginx au démarrage si DNS fail)
upstream api_backend {
    server api:8000;
}

location /api/ {
    proxy_pass http://api_backend/;
}

# BON (ne bloque pas nginx)
location /api/ {
    proxy_pass http://172.16.1.7:8000/;
}
```

**Solution 3: Désactiver temporairement les services problématiques**
Si un service comme vault est en boucle de redémarrage, commenter sa section dans nginx:

```nginx
# Knowledge Vault (temporarily disabled due to startup issues)
# location /vault/ {
#     limit_req zone=general_limit burst=10 nodelay;
#     proxy_pass http://vault:8001/;
#     ...
# }
```

#### Erreur: "address already in use" pour le port 80
**Cause:** Service nginx hôte déjà en cours d'exécution, empêchant le conteneur nginx de bind le port 80.

**Diagnostic:**
```bash
# Voir ce qui utilise le port 80
sudo netstat -tulpn | grep :80

# Exemple: nginx: master process (PID 1599)
```

**Solution:** Arrêter le service nginx hôte
```bash
sudo systemctl stop nginx
# ou
sudo pkill nginx
```

Puis redémarrer le conteneur nginx:
```bash
docker compose up -d nginx
```

#### Problème: Port mapping vide après recreation
**Symptôme:** `docker inspect` montre `{} pour .NetworkSettings.Ports` alors que les ports devraient être mappés

**Cause:** Container mal recréé, le mapping ports n'a pas été appliqué correctement.

**Solution:** Recréer le conteneur proprement
```bash
# Arrêter et supprimer le conteneur
docker stop cortex-leman-nginx && docker rm cortex-leman-nginx

# Recréer avec docker compose (qui applique le bon mapping)
docker compose -f /home/tars/.hermes/cortex-leman/docker-compose.yml up -d nginx

# Vérifier le mapping
docker inspect cortex-leman-nginx --format '{{json .NetworkSettings.Ports}}' | python3 -m json.tool
# Devrait montrer: {"80/tcp": [{"HostIp": "0.0.0.0", "HostPort": "80"}]}
```

#### Validation nginx après réparation
```bash
# Vérifier que nginx tourne et écoute sur le port 80
docker exec cortex-leman-nginx netstat -tulpn | grep nginx

# Tester la configuration nginx
docker exec cortex-leman-nginx nginx -t

# Test healthcheck depuis le conteneur
docker exec cortex-leman-nginx wget --quiet --tries=1 --spider http://localhost/health

# Test depuis l'hôte
curl -I http://localhost/health

# Test routing API
curl -s http://localhost/api/health
```

### 7. VALIDATION DES SERVICES

#### Check santé de tous les conteneurs
```bash
docker ps --filter name=cortex-leman --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

**Services attendus:**
- cortex-leman-api: Up (healthy) + 0.0.0.0:8000->8000/tcp
- cortex-leman-orchestrator: Up
- cortex-leman-worker: Up
- cortex-leman-vault: Up + 0.0.0.0:8001->8001/tcp
- cortex-leman-nginx: Up + 0.0.0.0:80->80/tcp
- cortex-leman-postgres: Up (healthy) + 0.0.0.0:5432->5432/tcp
- cortex-leman-redis: Up (healthy) + 0.0.0.0:6379->6379/tcp
- cortex-leman-prometheus: Up + 0.0.0.0:9090->9090/tcp
- cortex-leman-grafana: Up + 0.0.0.0:3000->3000/tcp

#### Tests HTTP
```bash
# API Health
curl -s http://localhost:8000/health

# API Root
curl -s http://localhost:8000/

# Vault Health
curl -s http://localhost:8001/health

# Prometheus (accessible via navigateur)
http://localhost:9090

# Grafana (accessible via navigateur)
http://localhost:3000
```

## PITFALLS

### 1. Nginx Gateway DNS Resolution
- **ATTENTION:** Docker DNS interne (127.0.0.11) peut ne pas répondre correctement entre conteneurs
- **Solution:** Utiliser les IP fixes des conteneurs dans `nginx/nginx.conf` au lieu des hostnames
- **Diagnostic:** Si nginx boucle sur "host not found in upstream", passer aux IP directes
- **Commande utile:** `docker inspect <container> --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'`

### 2. Host vs Container Port Conflicts
- **Vérifier avant démarrage:** `netstat -tuln | grep LISTEN` pour les ports 80, 8000, 8001, etc.
- **Conflit fréquent:** Service nginx hôte (port 80) vs conteneur nginx
- **Solution:** Arrêter le service hôte: `sudo systemctl stop nginx`
- **Mapping corrompu:** Si `docker inspect` montre `{} pour .NetworkSettings.Ports`, recréer le conteneur

### 3. Docker Compose Version
- Le Dockerfile doit référencer les bons chemins relatifs au build context
- `COPY cortex_leman/ /app/cortex_leman/` PAS `COPY api/ /app/api/`

### 3. Dependencies Python
- **Toujours** vérifier la compatibilité des versions
- Utiliser `pip show` pour voir les dépendances installées d'un package
- Celery[redis] gère ses propres dépendances redis - ne PAS les surcharger

### 4. French Quotes in Code
- **Jamais** utiliser `"` et `"` dans fichiers Python
- Utiliser uniquement `"` et `"`

### 5. Port Management
- Avant de démarrer, vérifier que les ports sont libres: `netstat -tuln | grep LISTEN`
- Documenter quels services utilisent quels ports dans le README

### 6. Cache Docker
- Si une modification de requirements n'est pas prise en compte: `docker compose build --no-cache <service>`
- Si un fichier Python modifié n'est pas pris en compte: `docker compose up -d --force-recreate <service>`

## STRUCTURE DES FICHIERS

```
cortex_leman/
├── __init__.py
├── api/
│   ├── __init__.py
│   └── main.py
├── orchestrator/
│   ├── __init__.py
│   ├── __main__.py
│   └── main.py
├── worker/
│   ├── __init__.py
│   └── main.py
└── knowledge_vault/
    ├── __init__.py
    └── main.py
```

## DOCKERFILES PATTERNS

### API Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY cortex_leman/ /app/cortex_leman/

CMD ["uvicorn", "cortex_leman.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Orchestrator Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements-orchestrator.txt .
RUN pip install --no-cache-dir -r requirements-orchestrator.txt

COPY cortex_leman/ /app/cortex_leman/

CMD ["python", "-m", "cortex_leman.orchestrator.main"]
```

### Worker Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements-worker.txt .
RUN pip install --no-cache-dir -r requirements-worker.txt

COPY cortex_leman/ /app/cortex_leman/

CMD ["celery", "-A", "cortex_leman.worker", "worker", "--loglevel=info", "--concurrency=4"]
```

### Vault Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements-vault.txt .
RUN pip install --no-cache-dir -r requirements-vault.txt

COPY cortex_leman/ /app/cortex_leman/

RUN mkdir -p /app/vault

CMD ["uvicorn", "cortex_leman.knowledge_vault.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

## COMMANDES UTILES

```bash
# Arrêter tout
docker compose down

# Arrêter + supprimer volumes
docker compose down -v

# Voir les logs d'un service
docker compose logs -f <service>

# Entrer dans un conteneur
docker compose exec <service> bash

# Voir les resources utilisées
docker stats

# Nettoyer les images inutilisées
docker image prune -a

# Rebuild tout sans cache
docker compose build --no-cache && docker compose up -d
```

## LIVRABLES
1. Infrastructure Docker fonctionnelle (Option C)
2. 9 services opérationnels
3. Validation des endpoints HTTP
4. Documentation des ports et services

---
**Docker. Infrastructure. Production-ready.**
