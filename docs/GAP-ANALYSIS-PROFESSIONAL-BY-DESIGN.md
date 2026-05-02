# Cortex Leman v5 — Gap Analysis: Professional by Design
# État actuel vs. État cible production

## LÉGENDE
✅ = Implémenté et fonctionnel
🔧 = Existe mais incomplet/cassé
❌ = Manquant

---

## 1. BACKEND (Python/FastAPI)

### ✅ Ce qui est bon
- 55 endpoints API REST
- 265 tests (dont 50 sprint2, 42 e2e, 41 auth)
- Journal WORM hash-chainé SHA-256
- Médiateur déterministe JsonLogic (27 règles, 6 verticals)
- Arbitrage humain avec escalade
- Circuit breakers + Saga pattern
- Compliance Gateway (rapports daily/monthly)
- Knowledge Vault (chiffré, isolé par client)
- RAG vectoriel (ChromaDB)
- Guardrails LLM (PII + Topic + Output)
- AutoDefense multi-agent (3 validateurs)
- RBAC 4 rôles (admin/expert/operator/viewer)
- JWT + API Keys
- Onboarding service avec validations réglementaires

### 🔧 À compléter
- **Onboarding tests** (0 tests) → tests/test_onboarding.py
- **Dockerfile** ne copie pas `core/onboarding/` ni les templates
- **requirements.txt** a une dépendance cassée (`asyncio-nats-client>=0.13.0`)
- **.env.example** n'existe pas (nouvel utilisateur ne sait pas quoi configurer)

### ❌ Manquant
- **Rate limiting** sur les endpoints onboarding
- **Email de bienvenue** après onboarding
- **Migration DB** pour les nouveaux tenants (Alembic)

---

## 2. FRONTEND (React/TypeScript/Vite)

### ✅ Ce qui est bon
- Landing page (11 sections, design professionnel)
- Login page avec comptes démo
- Onboarding wizard 6 étapes (même design system)
- ChatPanel avec sélecteur vertical/agent
- API client (api.ts + onboarding.ts)
- Hook useAuth
- Zero erreurs TypeScript, build clean

### 🔧 À compléter
- **DashboardPage** = Sidebar + Chat SEULEMENT. Les 5 autres nav items (Dashboard, Intentions, Journal, Arbitrage, Paramètres) sont cliquables mais ne font rien
- **ChatPanel** = Interface basique. Pas de:
  - Indicateur de confiance
  - Badge "Gel préventif"
  - Références réglementaires cliquables
  - Bouton "Demander arbitrage"
  - Historique des révisions

### ❌ Manquant (pages entières)
- **DashboardView** — Widgets KPI: compliance score, intentions actives, conflits, agents status
- **IntentionsView** — Liste des intentions avec statut, pipeline 5 étapes visuel
- **JournalView** — Journal d'audit avec filtres, vérification intégrité
- **ArbitrationView** — Dashboard contradictions, vote approve/reject/modify
- **SettingsView** — Profil, verticals, API keys, utilisateurs, data residency
- **Page transitions/animations** (slide-in comme Danswer)
- **Responsive mobile** (sidebar collapsible)
- **Loading states** (skeletons, spinners)
- **Toast notifications** (succès/erreur après actions)

---

## 3. INTÉGRATION BACKEND ↔ FRONTEND

### 🔧 CORS
- ✅ Corrigé (localhost:5173 ajouté)
- ❌ Manque la config pour production (domaine Cortex Leman)

### 🔧 Authentification post-onboarding
- L'utilisateur est créé en DB mais le frontend ne reçoit pas de JWT token
- `onComplete` doit appeler `/auth/login` pour obtenir un token et le stocker

### ❌ Missing API responses format
- Le frontend appelle des endpoints qui retournent des formats parfois incompatibles
- Pas de schema de validation côté frontend (Zod, etc.)

---

## 4. DÉPLOIEMENT

### 🔧 Docker
- Dockerfile existe mais est cassé (requirements, pas de onboarding/)
- Pas de docker-compose avec frontend (nginx pour servir le build)

### ❌ Manquant
- **CI/CD pipeline** (GitHub Actions)
- **Environment variables** sécurisées en prod
- **SSL/TLS** (Let's Encrypt)
- **Monitoring** (Grafana dashboard Cortex Leman spécifique)
- **Backup strategy** automatisée
- **Log aggregation** (structuré mais pas centralisé)

---

## 5. DOCUMENTATION

### ✅ Existant
- 10 docs (architecture, compliance, onboarding, AG2, déploiement, etc.)
- MVP Product Guide
- Agent configs YAML détaillés par vertical

### ❌ Manquant
- **API documentation** (Swagger/OpenAPI auto-généré par FastAPI mais pas exposé)
- **User guide** (pour l'utilisateur final, pas le dev)
- **Admin guide** (gestion tenants, utilisateurs, verticals)
- **Changelog** (versionning des releases)
- **Contributing guide**
- **Security audit documentation** (pour la certification ISO/IEC 42001)

---

## 6. PRIORISATION — Ce qu'il faut faire EN PREMIER

### P0 — Bloquant pour démo professionnelle (cette semaine)

| # | Tâche | Effort | Impact |
|---|-------|--------|--------|
| 1 | **DashboardPage avec vraies vues** (Dashboard, Intentions, Journal) | 3j | L'utilisateur voit la valeur |
| 2 | **Auth post-onboarding** (JWT token après setup) | 2h | Onboarding → Dashboard fluide |
| 3 | **Dockerfile fix** (copier onboarding/, fix requirements) | 2h | Déploiement possible |
| 4 | **Onboarding tests** (backend) | 4h | Confiance dans le flow |

### P1 — Qualité production (semaine suivante)

| # | Tâche | Effort | Impact |
|---|-------|--------|--------|
| 5 | **ArbitrationView** (dashboard contradictions) | 2j | Key differentiator |
| 6 | **SettingsView** (profil, API keys, team) | 2j | Self-service |
| 7 | **Animations/transitions** entre pages | 1j | Polish UX |
| 8 | **Email bienvenue** post-onboarding | 4h | Professionalisme |
| 9 | **.env.example** documenté | 1h | Onboarding dev |
| 10 | **CI/CD GitHub Actions** | 1j | Automatisation |

### P2 — Scale (sprint suivant)

| # | Tâche | Effort | Impact |
|---|-------|--------|--------|
| 11 | **Multi-tenancy DB** (schéma par tenant) | 1sem | Scale clients |
| 12 | **Mobile responsive** | 3j | Accessibilité |
| 13 | **Grafana dashboard** Cortex Leman | 2j | Monitoring pro |
| 14 | **SSL + domaine** | 1j | Production réelle |
| 15 | **Backup automation** | 1j | Sécurité données |

---

## RÉSUMÉ VISUEL

```
                    PRODUCTION READINESS
    Backend ████████████░░░░░  75%
  Frontend ██████░░░░░░░░░░░░  35%
Intégration ████████░░░░░░░░░  50%
Déploiement ████░░░░░░░░░░░░  20%
   Docs     ██████████░░░░░░  60%
─────────────────────────────────
   TOTAL    ████████░░░░░░░░  48%
```

**Le backend est solide (75%). Le frontend est le bottleneck (35%).**
Le prochain investissement majeur est dans les pages Dashboard.
