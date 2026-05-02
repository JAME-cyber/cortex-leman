# Cortex Leman v5 — MVP Product Owner Guide

## Vision produit

> Vendre une **infrastructure de confiance** qui garantit que chaque décision assistée par IA est documentée, traçable et conforme — pas un outil d'automatisation de plus.

**Tagline :** *"On ne vend pas une IA qui décide. On vend une IA qui garantit que chaque décision humaine est documentée, traçable et conforme."*

---

## Périmètre MVP (V1)

### Ce qui EST dans le MVP

| Fonctionnalité | Statut | Value pour le client |
|----------------|--------|---------------------|
| Pipeline 5 étapes | ✅ Implémenté | Orchestration structurée |
| 5 agents spécialisés | ✅ Implémenté | Traitement intelligent |
| Agent Médiateur | ✅ Implémenté | Conformité temps réel |
| 6 jeux de règles métier | ✅ Implémenté | Verticalisation immédiate |
| Journal WORM | ✅ Implémenté | Traçabilité opposable |
| Arbitrage humain | ✅ Implémenté | L'humain reste décideur |
| Circuit breakers | ✅ Implémenté | Résilience |
| Saga pattern | ✅ Implémenté | Rollback automatique |
| Compliance Gateway | ✅ Implémenté | Rapports automatiques |
| Dashboard MVP | ✅ Implémenté | Démonstration produit |
| API 26 endpoints | ✅ Implémenté | Intégration complète |
| Edge K3s scripts | ✅ Implémenté | Déploiement avocat/banque |
| LLM unifié (OpenRouter+Ollama) | ✅ Implémenté | Flexibilité standard/edge |
| n8n workflows | ✅ Implémenté | 12 workflows prêts |
| Knowledge Vault | ✅ Implémenté | Stockage isolé par client |
| 51 tests unitaires | ✅ Passent | Qualité garantie |

### Ce qui N'EST PAS encore dans le MVP

| Fonctionnalité | Priorité | Effort | Sprint |
|----------------|----------|--------|--------|
| Interface React complète | P1 | 4 sem | Sprint 2 |
| RAG vectoriel (embeddings) | P1 | 3 sem | Sprint 3 |
| Signature électronique (Yousign) | P1 | 2 sem | Sprint 2 |
| Horodatage RFC 3161 réel | P1 | 1 sem | Sprint 2 |
| OAuth2 / Keycloak | P2 | 2 sem | Sprint 3 |
| Intégration ERP réelle (Sage, SAP) | P2 | 4 sem | Sprint 4 |
| Dashboard métriques Grafana | P2 | 2 sem | Sprint 3 |
| Mobile app (notifications) | P3 | 4 sem | Sprint 5 |
| Certification ISO/IEC 42001 | P3 | 6 sem | Sprint 6 |

---

## User Stories — MVP

### Epic 1 : Soumission d'intention

```
US-1.1 : En tant que cabinet comptable,
         Je veux soumettre une demande en langage naturel,
         Pour que le système route automatiquement vers les bons agents.

US-1.2 : En tant qu'avocat,
         Je veux que ma demande soit traitée exclusivement en local,
         Pour respecter le secret professionnel (Art. 321 CP).
```

### Epic 2 : Conformité automatique

```
US-2.1 : En tant qu'expert RH,
         Je veux que le Médiateur bloque toute décision d'embauche automatique,
         Pour respecter l'AI Act et la loi anti-discrimination.

US-2.2 : En tant que banquier,
         Je veux que toute opération > 15K CHF demande validation hiérarchique,
         Pour respecter les obligations anti-blanchiment.
```

### Epic 3 : Arbitrage humain

```
US-3.1 : En tant qu'expert métier,
         Je veux voir les positions contradictoires des agents avec sources et confiance,
         Pour trancher en toute connaissance de cause.

US-3.2 : En tant qu'auditeur,
         Je veux que chaque décision humaine soit signée et horodatée,
         Pour pouvoir opposer la preuve de supervision.
```

### Epic 4 : Journal d'audit

```
US-4.1 : En tant que DPO,
         Je veux vérifier l'intégrité du journal d'audit à tout moment,
         Pour garantir la traçabilité lors d'un contrôle CNIL.

US-4.2 : En tant que responsable conformité,
         Je veux générer un rapport de conformité quotidien,
         Pour piloter la conformité en continu.
```

---

## Matrice des verticales

| Verticale | Règles | Mode requis | LLM | Prix indicatif |
|-----------|--------|-------------|-----|---------------|
| 📊 Comptable | 5 | Standard | OpenRouter | 500€/mois |
| ⚖️ Avocat | 4 | **Haute Protection** | **Ollama local** | 1500€/mois |
| 🏥 Santé | 3 | **Haute Protection** | **Ollama local** | 1500€/mois |
| 🏦 Banque | 3 | **Haute Protection** | **Ollama local** | 2000€/mois |
| 🚀 Startup | 2 | Standard | OpenRouter | 300€/mois |
| 👥 RH | 3 | Standard | OpenRouter | 400€/mois |

---

## Roadmap Produit

### Sprint 1 (Sem 1-4) — MVP TECHNIQUE ✅

- [x] Pipeline 5 étapes événementiel
- [x] Bus NATS JetStream
- [x] Journal WORM hash-chainé
- [x] 5 agents + Médiateur
- [x] 6 verticales de règles
- [x] Arbitrage humain
- [x] Circuit breakers + Saga
- [x] API REST 26 endpoints
- [x] Scripts Edge K3s + Ollama
- [x] Dashboard MVP de démonstration
- [x] 51 tests unitaires
- [x] Documentation certification

### Sprint 2 (Sem 5-8) — MVP COMMERCIAL

- [ ] Interface React complète (Wizard, Dashboard, Journal)
- [ ] Signature électronique (Yousign / DocuSign)
- [ ] Horodatage RFC 3161
- [ ] Authentification (JWT + rôles)
- [ ] Onboarding wizard par verticale
- [ ] Email templates pour notifications
- [ ] Démo automatisée pour prospects

### Sprint 3 (Sem 9-12) — INTÉGRATIONS

- [ ] RAG vectoriel (ChromaDB / Qdrant)
- [ ] Intégration Slack/Teams
- [ ] Dashboard Grafana
- [ ] OAuth2 / Keycloak SSO
- [ ] Connecteurs ERP (Sage pilot)
- [ ] Export PDF des rapports

### Sprint 4 (Sem 13-16) — DÉPLOIEMENT PILOTE

- [ ] Pilote chez cabinet comptable partenaire
- [ ] Monitoring production
- [ ] Support client (helpdesk)
- [ ] Documentation utilisateur
- [ ] Formation en ligne
- [ ] SLA et support

### Sprint 5-6 (Sem 17-24) — CERTIFICATION

- [ ] Audit de code par cabinet externe
- [ ] Certification ISO/IEC 42001
- [ ] Label "IA de confiance FR-CH"
- [ ] Extension aux 6 verticales complètes
- [ ] Mobile notifications
- [ ] Self-service onboarding

---

## KPIs Produit

| KPI | Cible MVP | Cible V2 |
|-----|-----------|----------|
| Temps de traitement d'une intention | < 30s | < 10s |
| Taux de conflits détectés | > 15% | > 20% |
| Taux d'arbitrages résolus < 24h | 100% | 100% |
| Intégrité journal (verify) | 100% | 100% |
| Uptime API | 99.5% | 99.9% |
| Temps de réponse API | < 500ms | < 200ms |
| Coverage tests | > 80% | > 95% |
| NPS clients pilotes | > 40 | > 60 |

---

## Pricing

### Mode Standard (Cloud)
- **Startup** : 300€/mois — RGPD basic, 2 workflows
- **RH** : 400€/mois — AI Act, anti-discrimination
- **Comptable** : 500€/mois — Audit trail, 5 workflows

### Mode Haute Protection (Edge)
- **Avocat** : 1 500€/mois — Art. 321 CP, Ollama local
- **Santé** : 1 500€/mois — LPM/HDS, données locales
- **Banque** : 2 000€/mois — Art. 47 LB, FINMA

### Setup initial
- Audit RGPD-IA initial : 2 500€ — 7 500€
- Installation Edge : 5 000€ (appliance incluse)
- Formation : 1 000€ / jour

---

## Démonstration MVP

### Lancement

```bash
cd /home/tars/cortex-leman-v5

# Backend
source .venv/bin/activate
docker compose up -d nats redis
NATS_URL=nats://localhost:4222 REDIS_HOST=localhost REDIS_PORT=6380 \
  uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload &

# Frontend
cd mvp/frontend
python3 -m http.server 3000
```

### Scénario de démo

1. **Dashboard** : Montrer les stats en temps réel
2. **Soumettre une intention** : Choisir "Comptable", taper une requête
3. **Observer le flux** : Voir les agents traiter en temps réel
4. **Conflit** : Le Médiateur détecte une divergence
5. **Arbitrage** : L'expert tranche avec justification
6. **Journal** : Vérifier l'intégrité hash-chainée
7. **Règles** : Montrer les 6 verticales et leurs règles
8. **Compliance** : Générer le rapport quotidien

### Arguments clés pour le prospect

> "Chaque action de nos agents est enregistrée dans un journal immuable. Vous pouvez vérifier l'intégrité à tout moment avec un seul clic."

> "Notre Médiateur bloque automatiquement toute opération non conforme. Vous ne validez pas après coup — vous arbitrez avant."

> "Pour les avocats et les banques : zéro donnée ne sort de vos locaux. Le modèle IA tourne sur votre infrastructure."

---

## Fichiers du MVP

```
mvp/
├── frontend/
│   └── index.html          → Dashboard interactif complet
└── docs/
    └── MVP-PRODUCT-GUIDE.md → Ce document
```

```
cortex-leman-v5/           → Backend complet
├── core/                  → 10 modules (bus, journal, orchestrateur, etc.)
├── api/                   → 26 endpoints REST
├── edge/                  → Scripts K3s + Ollama
├── tests/                 → 51 tests unitaires
└── docs/                  → Certification + Déploiement
```
