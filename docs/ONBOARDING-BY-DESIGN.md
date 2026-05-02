# Cortex Leman v5 — Onboarding Professional by Design
# Analyse concurrentielle + Architecture d'excellence

## 1. BENCHMARK CONCURRENTIEL

### A. Danswer/Onyx (Enterprise AI Search) — ⭐⭐⭐⭐⭐ Le meilleur onboarding du marché

**Pattern**: Stepped Wizard avec reducer state machine
```
Welcome → Name → LLM Provider → Complete → Dashboard
```

**Ce qu'ils font d'excellent**:
- `OnboardingStep` enum + `OnboardingActionType` reducer = state machine robuste
- Step navigation map (next/prev par étape) = UX prévisible
- Chaque step est un composant indépendant (`NameStep`, `LLMStep`, `FinalStep`)
- `FinalStep` propose des next-actions concrètes (web search, image gen, invite team)
- Progression visuelle (`iconPercentage: 10 → 40 → 70 → 100`)
- Animation `slide-in-from-right` entre les étapes
- CLI onboarding séparé (Go) avec splash art + test de connexion en live

**Ce qui manque**: Pas de verticalisation, pas de compliance, pas de guardrails visuels

### B. Tabby (AI Code Assistant) — ⭐⭐⭐⭐ Setup technique exemplaire

**Pattern**: IDE-first onboarding + admin setup wizard
```
Register → Setup Endpoint → Connect IDE → Start Coding
```

**Ce qu'ils font d'excellent**:
- Setup admin visuel (capture d'écran dans docs)
- Walkthrough VS Code intégré (`setupServer.md`)
- Configuration BentoML/Docker documentée
- Zero-config pour l'utilisateur final

### C. Axio Work (Agent Platform) — ⭐⭐⭐⭐ Simplicité brutale

**Pattern**: 60-second onboarding (déjà analysé dans AXIO-ONBOARDING-ANALYSIS.md)
```
Email/Google → Dashboard → Premier agent en 3 clics
```

**Leur force**: L'utilisateur voit IMMÉDIATEMENT la valeur

---

## 2. CE QUE CORTEX LEMAN DOIT AVOIR (que personne n'a)

### Le gap du marché: Onboarding COMPLIANT

Aucun concurrent n'a d'onboarding réglementaire. C'est notre moat.

Quand un cabinet comptable s'inscrit:
- ✅ Il DOIT choisir sa vertical (RGPD, AI Act)
- ✅ Le mode de protection s'active AUTOMATIQUEMENT
- ✅ Les règles JsonLogic se chargent pour SA vertical
- ✅ Le journal WORM démarre IMMÉDIATEMENT
- ✅ Le data residency est configuré par défaut

---

## 3. ARCHITECTURE ONBOARDING — Professional by Design

### Flux complet (6 étapes en 3 minutes)

```
┌──────────────────────────────────────────────────────────────────┐
│  Step 0: Welcome                                                 │
│  ═══════════════                                                 │
│  🏛️ Cortex Leman                                                │
│  Infrastructure de confiance IA pour professions régulées FR-CH  │
│                                                                  │
│  [Commencer]          [J'ai déjà un compte]                      │
│                                                                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │ 🇫🇷 France   │ │ 🇨🇭 Suisse   │ │ 🇫🇷🇨🇭 FR-CH  │               │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
│                                                                  │
│  Progress: ●○○○○○  (0%)                                         │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  Step 1: Identité & Organisation                                 │
│  ════════════════════════════════                                 │
│  👤 Votre profil                                                  │
│  Nom complet: [________________]                                  │
│  Email pro:   [________________]                                  │
│                                                                  │
│  🏢 Votre organisation                                            │
│  Nom du cabinet: [________________]                               │
│  Taille:  ◐ 1-5  ◐ 6-20  ◐ 21-50  ◐ 50+                        │
│                                                                  │
│  Progress: ●●○○○○  (20%)                                         │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  Step 2: Vertical & Réglementation                               │
│  ══════════════════════════════════                               │
│  Choisissez votre domaine d'activité:                            │
│                                                                  │
│  ┌──────────────────────┐  ┌──────────────────────┐             │
│  │ 📊 Expert-comptable   │  │ ⚖️ Avocat            │             │
│  │ RGPD + AFC + TVA      │  │ CP 321 + Secret      │             │
│  │ Mode: standard        │  │ Mode: haute_protection│ ← AUTO     │
│  └──────────────────────┘  └──────────────────────┘             │
│  ┌──────────────────────┐  ┌──────────────────────┐             │
│  │ 🏥 Santé              │  │ 🏦 Banque/Finance    │             │
│  │ LPM + HDS + Consent   │  │ LB 47 + KYC/AML      │             │
│  │ Mode: haute_protection│  │ Mode: haute_protection│ ← AUTO     │
│  └──────────────────────┘  └──────────────────────┘             │
│  ┌──────────────────────┐  ┌──────────────────────┐             │
│  │ 🚀 Startup/Tech       │  │ 👥 Ressources Humaines│             │
│  │ DPIA + AI Act         │  │ Art.22 + Anti-discrim │             │
│  │ Mode: standard        │  │ Mode: standard        │             │
│  └──────────────────────┘  └──────────────────────┘             │
│                                                                  │
│  ⚠️ Mode Haute Protection activé automatiquement pour:           │
│     avocat, banque, santé (secret professionnel suisse)           │
│                                                                  │
│  Progress: ●●●○○○  (40%)                                         │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  Step 3: Conformité & Protection                                 │
│  ══════════════════════════════════                               │
│  Basé sur votre vertical (comptable), voici vos paramètres:      │
│                                                                  │
│  📍 Data Residency                                                │
│  ○ EU (France)  ● CH (Suisse)  ○ EU+CH                          │
│  → Seuil gel préventif: 10 000 €                                  │
│                                                                  │
│  🔐 Chiffrement                                                   │
│  ● AES-256 (recommandé)  ○ ChaCha20                              │
│                                                                  │
│  🤖 Modèle IA                                                     │
│  ● Cloud (OpenRouter)  ○ Local (Ollama)  ○ Hybride               │
│  → Si avocat/banque: seul "Local" ou "Hybride" est proposé       │
│                                                                  │
│  📋 Règles chargées automatiquement:                              │
│     ✅ comptable-001: Décision fiscale → gel sans validation      │
│     ✅ comptable-002: Data transfer EU→CH → blocage               │
│     ✅ comptable-003: Montant > 10K€ → validation expert          │
│     ... (7 règles pour votre vertical)                            │
│                                                                  │
│  Progress: ●●●●○○  (60%)                                         │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  Step 4: Sécurité & Accès                                        │
│  ═════════════════════════════                                    │
│  🔑 Mot de passe admin                                            │
│  [________________] [________________]  (confirmation)            │
│  Force: ████████░░  Fort                                         │
│                                                                  │
│  🛡️ 2FA (optionnel mais recommandé)                              │
│  ◐ TOTP (Google Authenticator)  ◐ SMS                            │
│                                                                  │
│  📧 Inviter des collègues (optionnel)                             │
│  [email@...] [+ Ajouter]                                         │
│    Rôle: ○ expert  ○ operator  ○ viewer                          │
│                                                                  │
│  Progress: ●●●●●○  (80%)                                         │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  Step 5: Activation & Premier contact                            │
│  ═════════════════════════════════════                            │
│  ✅ Journal WORM activé (SHA-256 hash-chain)                     │
│  ✅ Règles JsonLogic chargées (7 règles)                          │
│  ✅ Textes réglementaires vectorisés (RGPD, AI Act, AFC)          │
│  ✅ Vault client créé (chiffré AES-256)                           │
│  ✅ Data residency configuré (EU)                                  │
│  ✅ Modèle IA connecté (OpenRouter)                                │
│  ✅ Mode: standard                                                 │
│  ✅ Audit trail actif                                               │
│                                                                  │
│  ┌─────────────────────────────────────────────────┐             │
│  │  🤖 Bonjour [Nom]!                               │             │
│  │                                                   │             │
│  │  Je suis l'assistant Cortex Leman pour            │             │
│  │  [Cabinet Dupont] — expert-comptable.             │             │
│  │                                                   │             │
│  │  Votre infrastructure de confiance est prête:     │             │
│  │  • 7 règles de conformité actives                 │             │
│  │  • Journal d'audit hash-chainé opérationnel      │             │
│  │  • Seuil de gel préventif: 10 000 €               │             │
│  │                                                   │             │
│  │  Essayez maintenant:                               │             │
│  │  [Vérifier conformité client]                      │             │
│  │  [Soumettre une intention]                         │             │
│  │  [Explorer le dashboard]                           │             │
│  └─────────────────────────────────────────────────┘             │
│                                                                  │
│  Progress: ●●●●●●  (100%)  ✅ Terminé !                         │
└──────────────────────────────────────────────────────────────────┘
```

---

## 4. IMPLÉMENTATION TECHNIQUE

### A. State Machine (inspiré Danswer, adapté compliance)

```typescript
// interfaces/onboarding.ts

export enum OnboardingStep {
  Welcome         = "welcome",
  Identity        = "identity",
  Vertical        = "vertical",
  Compliance      = "compliance",
  Security        = "security",
  Activation      = "activation",
}

export interface OnboardingData {
  // Step 0: Welcome
  jurisdiction: "FR" | "CH" | "FR_CH";

  // Step 1: Identity
  fullName: string;
  email: string;
  organizationName: string;
  organizationSize: "1-5" | "6-20" | "21-50" | "50+";

  // Step 2: Vertical
  vertical: Vertical;
  verticalConfig: VerticalConfig;

  // Step 3: Compliance
  dataResidency: "EU" | "CH" | "EU_CH";
  encryption: "AES-256" | "ChaCha20";
  llmMode: "cloud" | "local" | "hybrid";
  freezeThreshold: number;

  // Step 4: Security
  adminPassword: string;
  twoFactorMethod?: "totp" | "sms";
  inviteEmails: { email: string; role: UserRole }[];

  // Step 5: Activation (auto-generated)
  journalInitialized: boolean;
  rulesLoaded: number;
  vaultCreated: boolean;
  ragSeeded: number;
}

export type Vertical =
  | "comptable"
  | "avocat"
  | "sante"
  | "banque"
  | "startup"
  | "rh";

export interface VerticalConfig {
  mode: "standard" | "haute_protection";
  autoFreezeThreshold: number;
  requiredRules: string[];
  regulatoryTexts: string[];
  guardrails: {
    pii: boolean;
    topic: boolean;
    output: boolean;
  };
  allowedLlmModes: ("cloud" | "local" | "hybrid")[];
}

// Maps vertical → config (DRY, single source of truth)
export const VERTICAL_CONFIGS: Record<Vertical, VerticalConfig> = {
  comptable: {
    mode: "standard",
    autoFreezeThreshold: 10000,
    requiredRules: ["comptable-001", "comptable-002", "comptable-003", "comptable-004", "comptable-005"],
    regulatoryTexts: ["rgpd-art22", "ai-act-high-risk", "rgpd-art5"],
    guardrails: { pii: true, topic: true, output: true },
    allowedLlmModes: ["cloud", "local", "hybrid"],
  },
  avocat: {
    mode: "haute_protection",
    autoFreezeThreshold: 5000,
    requiredRules: ["avocat-001", "avocat-002", "avocat-003", "avocat-004"],
    regulatoryTexts: ["art321-cp", "rgpd-art22", "ai-act-high-risk"],
    guardrails: { pii: true, topic: true, output: true },
    allowedLlmModes: ["local", "hybrid"],  // Cloud interdit (secret professionnel)
  },
  sante: {
    mode: "haute_protection",
    autoFreezeThreshold: 0,  // Tout gelé par défaut
    requiredRules: ["sante-001", "sante-002", "sante-003"],
    regulatoryTexts: ["lpm-sante", "rgpd-art9", "ai-act-high-risk"],
    guardrails: { pii: true, topic: true, output: true },
    allowedLlmModes: ["local", "hybrid"],
  },
  banque: {
    mode: "haute_protection",
    autoFreezeThreshold: 15000,
    requiredRules: ["banque-001", "banque-002", "banque-003", "banque-004"],
    regulatoryTexts: ["art47-lb", "rgpd-art22", "ai-act-high-risk"],
    guardrails: { pii: true, topic: true, output: true },
    allowedLlmModes: ["local", "hybrid"],
  },
  startup: {
    mode: "standard",
    autoFreezeThreshold: 50000,
    requiredRules: ["startup-001", "startup-002", "startup-003"],
    regulatoryTexts: ["rgpd-art22", "ai-act-high-risk", "dpia-guide"],
    guardrails: { pii: true, topic: true, output: true },
    allowedLlmModes: ["cloud", "local", "hybrid"],
  },
  rh: {
    mode: "standard",
    autoFreezeThreshold: 20000,
    requiredRules: ["rh-001", "rh-002", "rh-003"],
    regulatoryTexts: ["rgpd-art22", "ai-act-high-risk", "anti-discrim"],
    guardrails: { pii: true, topic: true, output: true },
    allowedLlmModes: ["cloud", "local", "hybrid"],
  },
};

// Step navigation (comme Danswer, mais 6 étapes)
export const STEP_NAVIGATION: Record<OnboardingStep, {
  next?: OnboardingStep;
  prev?: OnboardingStep;
}> = {
  [OnboardingStep.Welcome]:    { next: OnboardingStep.Identity },
  [OnboardingStep.Identity]:   { next: OnboardingStep.Vertical,    prev: OnboardingStep.Welcome },
  [OnboardingStep.Vertical]:   { next: OnboardingStep.Compliance,  prev: OnboardingStep.Identity },
  [OnboardingStep.Compliance]: { next: OnboardingStep.Security,    prev: OnboardingStep.Vertical },
  [OnboardingStep.Security]:   { next: OnboardingStep.Activation,  prev: OnboardingStep.Compliance },
  [OnboardingStep.Activation]: { prev: OnboardingStep.Security },
};
```

### B. API Endpoint d'onboarding

```python
# POST /api/v1/onboarding/setup
# Un seul endpoint qui crée TOUT en une transaction:

{
  "identity": {
    "full_name": "Jean Dupont",
    "email": "jean@dupont-comptable.fr",
    "organization": "Dupont & Associés",
    "organization_size": "6-20"
  },
  "vertical": "comptable",
  "compliance": {
    "data_residency": "EU",
    "encryption": "AES-256",
    "llm_mode": "cloud"
  },
  "security": {
    "admin_password": "********",
    "two_factor_method": "totp",
    "invite_emails": [
      {"email": "marie@dupont-comptable.fr", "role": "expert"},
      {"email": "paul@dupont-comptable.fr", "role": "operator"}
    ]
  }
}

# Retourne:
{
  "status": "activated",
  "tenant_id": "dupont-comptable-fr",
  "admin_user": {"id": "...", "email": "jean@dupont-comptable.fr"},
  "vertical": "comptable",
  "mode": "standard",
  "rules_loaded": 7,
  "regulatory_seeded": 5,
  "vault_created": true,
  "journal_initialized": true,
  "journal_sequence": 1,  // Premier événement: "tenant.created"
  "first_chat_prompt": "Bonjour Jean ! Je suis l'assistant Cortex Leman..."
}
```

### C. Reduction des risques (ce qui rend notre onboarding UNIQUE)

Chaque step a des validations backend:

| Step | Validation | Blocage |
|------|-----------|---------|
| Welcome | Juridiction → data residency par défaut | Non |
| Identity | Email pro (pas de gmail/outlook pour avocat/banque) | **OUI** |
| Vertical | Mode auto (avocat/banque/santé = haute_protection) | **OUI** |
| Compliance | LLM mode: cloud INTERDIT pour avocat/banque/santé | **OUI** |
| Security | Password force ≥ 3/4 | **OUI** |
| Activation | Journal WORM + Vault + RAG seedés | Auto |

### D. Inspirations volées aux concurrents

| Pattern | Source | Adaptation Cortex Leman |
|---------|--------|------------------------|
| Stepped wizard + reducer | Danswer/Onyx | ✅ 6 étapes au lieu de 4 |
| State machine enum | Danswer/Onyx | ✅ + validations compliance par step |
| Final step = next actions | Danswer/Onyx | ✅ Chat agent + premiers gestes guidés |
| Progression visuelle | Danswer/Onyx | ✅ + badges réglementaires |
| Splash art + test connexion | Danswer CLI | ✅ Test journal WORM + Vault au setup |
| Zero-config utilisateur | Tabby | ✅ Auto-config par vertical |
| "Agent = collègue" mental model | Axio Work | ✅ L'agent s'adapte à la vertical |
| 60-second value proposition | Axio Work | ✅ L'utilisateur voit les règles chargées en live |

---

## 5. PLAN D'IMPLÉMENTATION

### Sprint 1 (cette semaine): Backend

1. **`api/v1/onboarding/`** — 3 endpoints:
   - `POST /api/v1/onboarding/setup` — Crée tout en une transaction
   - `GET /api/v1/onboarding/status` — Où en est l'admin
   - `POST /api/v1/onboarding/validate-step` — Validation par step

2. **`core/onboarding/service.py`** — Logique métier:
   - `OnboardingService.setup_tenant(data)` → transaction complète
   - Validation par step (email pro, LLM mode, password)
   - Auto-config mode haute_protection

3. **`core/onboarding/validator.py`** — Validations réglementaires:
   - Avocat: email doit être domaine pro
   - Banque: LLM local/hybride uniquement
   - Santé: tout gelé par défaut

### Sprint 2 (semaine suivante): Frontend

4. **Onboarding Wizard React** — 6 composants step
5. **Vertical selector** — Cartes visuelles avec badges réglementaires
6. **Compliance config** — Auto-déduit de la vertical (modifiable par expert)
7. **Activation screen** — Checklist live avec spinner

### Sprint 3: Polish

8. **Animations** (slide-in entre steps, comme Danswer)
9. **Premier chat guidé** (l'agent propose 3 actions)
10. **Notifications** (email de bienvenue avec récap)
11. **E2E tests** (onboarding flow complet)

---

## 6. MÉTRIQUES DE SUCCÈS

| Métrique | Objectif |
|----------|----------|
| Temps d'onboarding | < 3 minutes |
| Abandon step 2 (vertical) | < 5% |
| Premier message agent | < 30 sec après activation |
| Erreurs de setup | < 1% |
| NPS post-onboarding | > 70 |
| Taux de journal actif | 100% (obligatoire) |
| Règles chargées par défaut | 100% (obligatoire) |
