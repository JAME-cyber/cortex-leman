# Cortex Leman v5 — Dockerfile multi-stage
FROM python:3.11-slim AS base

LABEL maintainer="Cortex Leman <contact@cortex-leman.com>"
LABEL version="5.0.0"
LABEL description="Cortex Leman v5 — Graphe de Confiance"

# Dépendances système
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY core/ /app/core/
COPY api/ /app/api/

# Créer les répertoires de données
RUN mkdir -p /app/data/{journal,reports,precedents}

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Port API
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Démarrage
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
