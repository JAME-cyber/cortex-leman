---
name: Agent Implementation Service
category: cortex-leman
version: 4.0.0
description: |
  Enterprise-grade AI Agent Implementation Service for FR-CH SMEs.
  Architecture-by-design: Agent Squad model, compliance-first, zero client friction.
  3 pillars: Equipe d'agents specialises | Conformite RGPD-IA integree | Zero friction client.
  Integrated with SocialPulse (lead gen), Gardien des Normes (audit), Security Audit (OWASP+LLM Top 10).
  Includes Cortex Leman ecosystem map — see references/ecosystem_map.md

triggers:
  - "implementer un agent"
  - "agent IA professionnel"
  - "configurer un agent"
  - "agent implementation"
  - "deployer agent"
  - "parametrer agent IA"
  - "equipe d'agents"
  - "agent squad"
  - "agent conforme"

prerequisites:
  - Templates verticals dans templates/ directory
  - Apify API token (discovery)
  - OpenRouter API key (agent config + personalization)
  - Kie.ai API key (infographics)
---

# Agent Implementation Service v4.0

## POSITIONNEMENT

**"Cortex Leman: Votre equipe d'agents IA conformes, cle-en-main."**

> Les autres vous disent d'installer un agent. Nous le faisons pour vous -- et il est conforme.

**3 piliers de valeur:**

1. **Equipe d'agents specialises** -- pas un chatbot, pas un agent generique. Un squad orchestre.
2. **Conformite RGPD-IA integree** -- pas un audit a cote. C'est dans l'architecture.
3. **Zero friction client** -- on installe, on configure, on documente, on forme. Le client n'ouvre jamais un terminal.

**Cible:** PME 50-200 employes, Suisse Romande et Haute-Savoie.

**Differentiateur vs Accio/Alibaba:** Accio vend de la productivite (plug-and-play e-commerce). Nous vendons de la **legalite + productivite**. L'AI Act rend notre proposition non-optionnelle. Accio = self-service zero friction. Nous = **service** zero friction. Meme promesse, livraison sur-mesure.

---

## ARCHITECTURE DU SERVICE: BY DESIGN

**Principe directeur:** Architecture-first, pas feature-first. Chaque decision technique est tracee, justifiable devant un auditeur CNIL/PPDT, et documentee avant implementation.

**Duree reelle: 6-8 semaines.** Sous-promettre, sur-livrer.

```
┌─────────────────────────────────────────────────────────────────────┐
│        AGENT IMPLEMENTATION SERVICE v4.0                           │
│        Architecture by Design | Compliance-First                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  PHASE 0: BETA ONBOARDING (si 0 references)                       │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │ Prix: CHF 1'500-2'000                                   │       │
│  │ Contrepartie: temoignage + case study + referral         │       │
│  │ Garantie: 4 sem gratuites ou 50% rembourse              │       │
│  │ Objectif: 3-5 beta clients avant lancement commercial   │       │
│  └────────────────────────┬────────────────────────────────┘       │
│                           ▼                                         │
│  PHASE 1: ARCHITECTURE & DISCOVERY (S1-S2)                        │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │ 1. Entretien strat(1h) -- objectifs, processus, data    │       │
│  │ 2. Cartographie flux donnees (DAG)                       │       │
│  │ 3. Classification risque IA Act (Low/Medium/High)        │       │
│  │ 4. Data residency mapping (CH/UE/autre)                 │       │
│  │ 5. Selection Agent Squad (3 agents specialises)          │       │
│  │ 6. Output: Architecture Document + agent-config.yaml     │       │
│  └────────────────────────┬────────────────────────────────┘       │
│                           ▼                                         │
│  PHASE 2: BUILD & HARDEN (S3-S5)                                  │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │ 1. Deploiement staging (Docker, infra CH si requis)      │       │
│  │ 2. Configuration Agent Squad + guardrails par agent       │       │
│  │ 3. Integrations (CRM, email, documents, n8n)             │       │
│  │ 4. Security hardening (OWASP Top 10 + LLM Top 10)        │       │
│  │ 5. State verification (anti-faux-rapport, arXiv:2602.20021)│    │
│  │ 6. Tests: nominaux + guardrails + injection + perf       │       │
│  │ 7. Output: Agent Squad operationnel en staging           │       │
│  └────────────────────────┬────────────────────────────────┘       │
│                           ▼                                         │
│  PHASE 3: COMPLIANCE & GO LIVE (S6-S8)                            │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │ 1. Audit RGPD-IA complet (Gardien des Normes)            │       │
│  │ 2. DPIA si high-risk (AI Act Annexe III)                 │       │
│  │ 3. Documentation legale (registre, procedures incident)  │       │
│  │ 4. Formation equipe (3 sessions, pas 2h)                 │       │
│  │ 5. Go live + periode observation 2 sem                    │       │
│  │ 6. Output: Agent conforme + live + docs completes         │       │
│  └────────────────────────┬────────────────────────────────┘       │
│                           ▼                                         │
│  PHASE 4: CONFORMITE CONTINUE (CHF 1'000-1'500/mois)             │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │ - Monitoring mensuel automatise (dashboard + alertes)     │       │
│  │ - Mises a jour guardrails (AI Act evolue)                 │       │
│  │ - Audit trimestriel light                                │       │
│  │ - Support prioritaire                                    │       │
│  │ - Nouveaux agents = nouveau cycle                        │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## AGENT SQUAD MODEL

**Principe:** Un agent unique = un point de defaillance. Un squad = redondance, specialisation, isolation.

Chaque vertical deploye 3 agents specialises qui travaillent en orchestration:

```
┌─────────────────────────────────────────────┐
│           AGENT SQUAD (3 specialistes)      │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Agent A  │  │ Agent B  │  │ Agent C  │  │
│  │ Tri &    │  │ Analyse &│  │ Action & │  │
│  │ Routage  │  │ Synthese │  │ Suivi    │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       │             │             │         │
│       ▼             ▼             ▼         │
│  ┌─────────────────────────────────────┐    │
│  │       ORCHESTRATEUR (Hermes)        │    │
│  │  - Routage contextuel              │    │
│  │  - Guardrails globaux              │    │
│  │  - State verification              │    │
│  │  - Audit trail                     │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  Securite: Isolation inter-contexte          │
│  (jamais cross-dossiers, cross-clients)      │
│                                             │
└─────────────────────────────────────────────┘
```

**Pourquoi 3 agents et pas 1:**

| 1 agent monolithique | 3 agents specialises |
|---|---|
| Prompt geant = hallucinations | Prompt focused = precision |
| 1 contexte = surcharge | Contextes isoles = clarte |
| 1 point de defaillance | Redondance fonctionnelle |
| Guardrails globaux difficiles | Guardrails par agent = granulaires |
| Debug = foret de prompts | Debug = agent isole |
| Audit = boite noire | Audit = traces par agent |

---

## 3 NIVEAUX DE SERVICE

| Niveau | Agent Squad | Contenu | Prix |
|---|---|---|---|
| **Starter** | 1 agent (1 specialiste) | 1 processus, RAG basique, template vertical, conformite standard | CHF 5'000 |
| **Business** | 3 agents (squad complet) | Multi-processus, integrations CRM, workflows n8n, DPIA si high-risk | CHF 12'000 |
| **Enterprise** | 3+ agents + orchestrateur | Architecture complete, agents autonomes, monitoring, conformite continue 12 mois | CHF 20'000+ |

**Pricing rationale:** Expertise RGPD-IA FR-CH specialisee = CHF 200+/h. Starter = ~25h = CHF 5'000 minimum. Business = ~60h. Enterprise = ~100h+.

---

## TEMPLATES PAR VERTICAL

Chaque template pre-configure 3 agents specialises + guardrails + workflows. Le template accelere le diagnostic et la structure (50% du travail). Si client veut 50%+ de custom = c'est Enterprise.

### 1. Cabinet Comptable
**Agent Squad:**
- **Tri-Assist:** Classification documents, tri automatique, routage
- **Synthese-Assist:** Syntheses mensuelles, rapprochements, alerts echeances
- **Rappel-Assist:** Relances clients, echeances fiscales, deadlines

**Spec:** Donnees financieres, fiscalite FR-CH | **Risk IA Act:** Limited | **Guardrails:** Pas de conseil fiscal definitif, anonymisation logs, session_timeout 30min

### 2. Cabinet d'Avocats
**Agent Squad:**
- **Dossier-Assist:** Tri dossiers, indexation, isolation inter-dossiers
- **Jurisprudence-Assist:** Recherche jurisprudence, analyse precedents
- **Audience-Assist:** Rappels audiences, prep conclusions, suivi deadlines

**Spec:** Secret professionnel (Art. 321 CP), data residency CH obligatoire | **Risk IA Act:** High | **Guardrails:** Jamais acces inter-dossiers, chiffrement AES-256, PGP emails, state_verification obligatoire

### 3. Clinique / Sante
**Agent Squad:**
- **Admin-Assist:** Rappels RDV, suivi administratif, gestion plannings
- **Facturation-Assist:** Facturation Tarmed, relances, rapprochements
- **Suivi-Assist:** Suivi post-consultation (administratif uniquement)

**Spec:** Donnees sante Art. 9 RGPD + LPM, data residency CH | **Risk IA Act:** High (Annexe III) | **Guardrails:** BLOCAGE total dossiers medicaux, jamais de diagnostic, anonymisation PII obligatoire

### 4. Banque / Finance
**Agent Squad:**
- **KYC-Assist:** Automatisation KYC, screening AML, verification identite
- **Conformite-Assist:** Rapports conformite, SAR automatique, suivi reglementaire
- **Rapport-Assist:** Generation rapports, synthese portefeuille (lecture seule)

**Spec:** Secret bancaire Art. 47 LB, FINMA | **Risk IA Act:** High | **Guardrails:** Jamais conseil investissement, SAR automatique, human_decision_required sur transactions

### 5. Startup Tech
**Agent Squad:**
- **Triage-Assist:** Triage bugs, categorisation, routage equipe
- **Deploy-Assist:** Checklists deploiement, verification pre-prod
- **Standup-Assist:** Synthese standup, suivi sprint, metrics

**Spec:** Support technique, deploiement | **Risk IA Act:** Limited | **Guardrails:** Masquage secrets/API keys, blocked_actions: [deploy_production, billing_changes]

### 6. Cabinet RH / Recrutement
**Agent Squad:**
- **Accueil-Assist:** Accueil candidats, planification entretiens, suivi pipeline
- **Rapport-Assist:** Rapports consultation, synthese feedbacks
- **Alerte-Assist:** Detection biais, alertes discriminatoires, suivi Art. 22 RGPD

**Spec:** Profilage/biais algorithmique | **Risk IA Act:** High (Annexe III emploi) | **Guardrails:** JAMAIS selection autonome, detection biais obligatoire, human_oversight: true

---

## PROCESS D'IMPLEMENTATION DETAILLE

### Phase 1: Architecture & Discovery (S1-S2)

**Principe:** On ne code rien avant d'avoir un Architecture Document valide par le client.

**1.1 Entretien strategique (1h)**
- Processus qui prennent le plus de temps?
- Quelles donnees sont traitees (sensibles ou non)?
- Qui utilise l'outil final?
- Integrations existantes?
- Contraintes legales specifiques (secret professionnel, bancaire, medical)?

**1.2 Cartographie des flux (DAG)**
- Diagramme flux actuels avec sources de donnees
- Identification goulets d'etranglement
- Mapping data residency (ou vont les donnees?)

**1.3 Classification risque IA Act**
```
Niveau d'autonomie (Source: Stanford CS230):
┌────────┬─────────────────────────┬──────────────┬────────────────────┐
│ Niveau │ Description             │ Risque RGPD  │ Action audit       │
├────────┼─────────────────────────┼──────────────┼────────────────────┤
│ Low    │ Humain approuve chaque  │ Minimal      │ Standard           │
│        │ action                  │              │                    │
│ Medium │ Agent agit, humain      │ Tracabilite  │ Verifier logs +    │
│        │ reveise                 │ obligatoire  │ reseau humain      │
│ High   │ Agent autonome, alertes │ DPIA         │ DPIA + traces +   │
│        │ exceptions             │ OBLIGATOIRE  │ Kill Switch        │
└────────┴─────────────────────────┴──────────────┴────────────────────┘
```
Commencer a basse autonomie. Ne pas valider haute autonomie sans DPIA.

**1.4 Selection Agent Squad**
- Choisir template vertical (6 disponibles)
- Definir 3 agents specialises
- Mapper guardrails par agent
- Confirmer data residency
- Definir niveau autonomie par agent

**1.5 Architecture Document (livrable)**
```yaml
# architecture-document.yaml (template)
client:
  name: ""
  sector: ""
  risk_level: ""  # Low/Medium/High
  data_residency: ""  # CH/UE/autre
  legal_constraints: []  # secret_professionnel, bancaire, medical

agent_squad:
  - name: ""
    role: ""  # Tri, Analyse, Action
    autonomy_level: ""  # Low/Medium/High
    data_access: []  # liste des donnees accessibles
    guardrails: []
    integrations: []

  - name: ""
    role: ""
    autonomy_level: ""
    data_access: []
    guardrails: []
    integrations: []

  - name: ""
    role: ""
    autonomy_level: ""
    data_access: []
    guardrails: []
    integrations: []

orchestration:
  routing_logic: ""
  global_guardrails: []
  state_verification: true
  audit_trail: true
  human_oversight: true  # toujours true par defaut

timeline:
  phase1_end: ""
  phase2_end: ""
  phase3_end: ""
  go_live: ""

compliance:
  dpia_required: false  # true si high-risk
  register_entry: true  # toujours
  art22_compliant: true  # toujours
  ai_act_category: ""  # minimal/limited/high
```

**Validation client:** Le client valide l'Architecture Document AVANT Phase 2. Pas de code sans architecture approuvee.

### Phase 2: Build & Harden (S3-S5)

**Principe:** Security-first. Chaque agent est durci AVANT integration.

**2.1 Deploiement staging**
- Instance Docker (infra CH si data residency CH requis)
- Base de connaissances (documents client anonymises)
- Modele LLM configure (model-agnostic: Claude/GPT/GLM)

**2.2 Configuration Agent Squad**
```yaml
# agent-config.yaml (template par vertical)
squad:
  name: ""
  vertical: ""
  agents:
    - id: "tri-assist"
      role: "Tri & Routage"
      system_prompt: ""
      autonomy: "low"  # toujours low par defaut
      data_access:
        - "documents_entrants"
        - "metadata"
      data_restrictions:
        - "jamais_acces_dossiers_fermes"
      guardrails:
        human_decision_required: ["classification_fiscale", "transfert_dossier"]
        max_requests_per_hour: 100
        session_timeout_minutes: 30
        content_filter: true
        state_verification:
          enabled: true
          methods:
            - "checksum_fichier_attendu"
            - "log_confirmation"
          alert_on_mismatch: true
      log_all_interactions: true
      register_entry: true
      data_controller: ""

    - id: "synthese-assist"
      role: "Analyse & Synthese"
      # ... (idem structure)

    - id: "rappel-assist"
      role: "Action & Suivi"
      # ... (idem structure)

  orchestration:
    routing: "contextual"  # par sujet/contexte
    isolation: "strict"   # jamais cross-contexte
    fallback: "human"    # toujours fallback humain
```

**2.3 Security Hardening (OWASP + LLM Top 10)**

Obligatoire pour chaque agent avant integration:

| Check | OWASP Ref | Methode |
|---|---|---|
| Prompt injection protection | LLM01 | Test red-team 5 scenarios |
| Output validation | LLM02 | Schema validation, jamais exec/eval |
| Rate limiting | LLM04 | max_requests_per_hour |
| Sensitive info disclosure | LLM06 | PII scan dans prompts et logs |
| Excessive agency prevention | LLM08 | human_decision_required sur actions critiques |
| State verification | arXiv:2602.20021 | Anti-faux-rapport |
| Access control | A01 | Routes avec auth, CORS strict |
| Crypto | A02 | AES-256, TLS 1.3, pas de MD5/SHA1 |
| Injection prevention | A03 | Parametrized queries, jamais eval() |
| Logging | A09 | Logs sans PII, audit trail complet |

**2.4 Integrations**
- Email (IMAP/SMTP)
- CRM (si applicable)
- Documents (stockage chiffre)
- n8n workflows

**2.5 Tests (4 categories obligatoires)**
1. **Nominaux:** 5-10 cas d'usage metier
2. **Guardrails:** Tentatives de contournement (10+ scenarios)
3. **Injection:** Prompt injection + social engineering
4. **Performance:** Latence, throughput, failover

### Phase 3: Compliance & Go Live (S6-S8)

**Principe:** Conformite integree, pas ajoutee. L'audit confirme, il ne corrige pas.

**3.1 Audit RGPD-IA (Gardien des Normes + Compliance Agent)**
- Charger skill: `le-gardien-des-normes` pour audit Hermes-native
- OU charger skill: `cortex-leman-compliance-agent` pour audit agent-agnostique (Codex/Cursor/Claude Code)
- Le compliance-agent est le même contenu réglementaire, packagé pour consommation par n'importe quel agent
- Audit complet de l'Agent Squad deploye
- Verifier conformite AI Act
- DPIA si high-risk
- Security audit: charger skill `security-audit-cortex-leman`

**3.2 Documentation legale (livrables obligatoires)**
- Guide d'utilisation (pour l'equipe)
- Documentation technique (pour l'auditeur)
- Registre des traitements (Art. 30 RGPD)
- Procedures d'incident (notification 72h)
- Architecture Document (mis a jour post-implementation)
- DPIA (si high-risk)

**3.3 Formation (3 sessions, pas moins)**
- Session 1: Demo live + cas d'usage (2h)
- Session 2: Guardrails + que faire quand l'agent refuse (1h)
- Session 3: Monitoring + alertes + support (1h)

**3.4 Go Live**
- Deploiement production
- Monitoring active (dashboard + alertes)
- Periode observation 2 semaines
- Support prioritaire 30 jours

---

## SYNERGIE PIPELINE COMPLET

```
SocialPulse (lead gen)
  │
  │ PME detectee avec IA non conforme
  │
  ▼
Email d'approche
  │ "38 chercheurs ont prouve que les agents IA autonomes fuient
  │  des donnees, obbeissent a des inconnus, et mentent sur l'etat
  │  du systeme. Votre agent est-il protege?"
  │
  ▼
Audit RGPD-IA (diagnostic gratuit 30min)
  │
  │ "Votre IA n'est pas conforme. Voici les risques."
  │ Upsell: "On peut vous deployer une equipe d'agents conformes."
  │
  ▼
Agent Implementation (service payant)
  │
  │ Agent Squad deploye + conforme + documente
  │
  ▼
Conformite Continue (CHF 1'000-1'500/mois)
  │
  │ Monitoring mensuel + audit trimestriel
  │ Nouveaux agents = nouveau cycle
  │
  ▼
Flywheel: lead → audit → implementation → monitoring → nouveau besoin
```

---

## ARCHITECTURE PAR DESIGN: PRINCIPES

### 1. Compliance-First (pas Compliance-After)

L'audit ne corrige pas, il confirme. Les guardrails sont dans l'architecture, pas rajoutes apres coup.

**Manifestation:**
- Architecture Document avant code
- Guardrails dans agent-config.yaml avant prompts
- Data residency mapping avant deploiement
- DPIA avant Go Live (si high-risk)

### 4. Agent-Consumable Context (pas Website-First)

Les clients n'iront pas sur un website pour uploader leurs documents. L'avenir = l'agent a déjà le code, le config, l'architecture — il a besoin du **contexte réglementaire** pour auditer. Le produit doit être consommable par n'importe quel agent (Codex, Cursor, Claude Code, Hermes), pas seulement via une UI web.

**Manifestation:**
- Skills agent-agnostiques avec prompts templates (ex: `cortex-leman-compliance-agent`)
- `.cursorrules` et `CLAUDE.md` templates pour les autres agents
- API-first, skill-first, website-second
- "Less UI, more context" — l'agent est l'interface

**Référence:** Vidéo Pietro/MagicPath (David Andre Podcast, juin 2026) — "The future is less about doing the thing but more about supervising the thing. Build context that agents can consume."

### 5. Model-Agnostic (pas Vendor Lock-In)

Le client achete le RESULTAT, pas le modele. Le modele est interchangeable sans impact service.

**Manifestation:**
- Templates compatibles Claude, GPT, GLM
- Config modele dans agent-config.yaml (swap sans toucher prompts)
- Prompts ecrits pour generalisation, pas pour un modele specifique
- Benchmark modele uniquement si latence/cout critique

### 3. Isolation par Defaut (pas Acces par Defaut)

Chaque agent n'accede qu'aux donnees strictement necessaires. Jamais cross-contexte.

**Manifestation:**
- Avocat: jamais cross-dossiers
- RH: jamais cross-candidats
- Sante: jamais dossiers medicaux (admin uniquement)
- Finance: lecture seule sur portefeuilles

### 4. Human-in-the-Loop (pas Human-After-the-Loop)

L'humain approuve, l'agent execute. Pas l'inverse.

**Manifestation:**
- human_decision_required sur actions critiques
- human_oversight: true par defaut
- Autonomie Low par defaut, Medium uniquement avec tracabilite
- High uniquement avec DPIA + Kill Switch

### 5. State Verification (pas Trust-but-Verify)

L'agent ne peut pas rapporter "completion" sans preuve verifiable.

**Manifestation:**
- state_verification: enabled dans chaque agent-config.yaml
- Checksum/fichier attendu apres action
- Log de confirmation systematique
- Cross-check par second agent si action critique
- Alerte si rapport ≠ etat reel

---

## POSITIONNEMENT VS CONCURRENTS

### vs LobsterAI (NetEase Youdao, open-source, 5.1k stars, avril 2026)

| | LobsterAI | Cortex Leman |
|---|---|---|
| **Segment** | B2C personnel (desktop Electron) | B2B PME FR-CH |
| **Promesse** | Productivite 24/7 | Legalite + productivite |
| **Architecture** | 1 agent monolithique + OpenClaw | Agent Squad (3+ agents isoles) |
| **Conformite** | Absente | RGPD-IA integree par design |
| **Data residency** | Locale uniquement | CH obligatoire si high-risk |
| **IM** | WeChat/DingTalk/Feishu/QQ/Telegram/Discord | Telegram (extensible) |
| **Skills** | 29 built-in (bureautique, recherche) | 6 verticals metier (comptable, avocat, sante, finance, RH, tech) |
| **Monitoring** | Aucun | Dashboard + audit trimestriel |
| **Memoire** | MEMORY.md + USER.md + SOUL.md | Identique (Hermes natif) |
| **Modele** | OpenClaw (agent engine) | Model-agnostic (Claude/GPT/GLM) |
| **Cout** | Gratuit (MIT) | CHF 5'000-20'000+ (service) |

**Insight:** LobsterAI valide la demande (agent desktop 24/7 + IM + skills + memoire). Notre differentiel = conformite + service + B2B vertical. Leur architecture OpenClaw/Cowork est une bonne reference UX (permission gating, stream events, scheduled tasks) que nous integrons dans nos Cowork Sessions.

### vs Accio Work (Alibaba International, mars 2026)

| | Accio Work | Cortex Leman |
|---|---|---|
| **Promesse** | Productivite zero-friction (self-service) | Legalite + productivite zero-friction (service) |
| **Format** | Plug-and-play SaaS | Accompagnement cle-en-main 6-8 semaines |
| **Compliance** | VAT/customs (feature produit) | RGPD-IA (architecture) |
| **Data residency** | Non controlee | CH obligatoire si high-risk |
| **Guardrails metier** | Generiques | Par vertical (secret professionnel, bancaire, medical) |
| **Service humain** | Aucun | Accompagnement expert + 3 sessions formation |
| **Monitoring** | Non precise | Dashboard + alertes + audit trimestriel |
| **Ecosysteme** | Alibaba only | Model-agnostic (Claude/GPT/GLM) |
| **Target** | E-commerce B2B global | PME FR-CH (avocat, comptable, sante, finance, RH, tech) |
| **Urgence** | Productivite | Obligation legale (AI Act) |

**Notre avantage structurel:** Accio = productivite optionnelle. Nous = legalite non-optionnelle. L'AI Act cree un marche captive pour les PME europeennes.

### vs Installateurs B2C (side projects FR)

| | Side project B2C | Cortex Leman |
|---|---|---|
| **Format** | Installation one-shot | Implementation complete + conformite |
| **Prix** | CHF 200-500 | CHF 5'000-20'000 |
| **Conformite** | Absente | Integree (Gardien des Normes) |
| **Support** | Peer-to-peer | Accompagnement expert |
| **Templates** | Aucun | 6 verticals pre-configures |
| **Retention** | One-shot | CHF 1'000-1'500/mois |

**Leur side project valide la demande. Il ne cannibalise PAS notre segment B2B.**

---

## REFERENCES ACADEMIQUES

### 1. "Agents of Chaos" (arXiv:2602.20021, fevrier 2026)
Shapira et al. (38 auteurs). Red-teaming d'agents IA autonomes en environnement reel.

**Conclusion:** Les agents autonomes presentent des vulnerabilites securite/vie privee/gouvernance en conditions reelles.

**Mapping vers nos guardrails:**

| Vulnerabilite | Notre guardrail |
|---|---|
| Compliance non-autorisee | human_decision_required |
| Divulgation infos sensibles | data_restrictions + anonymisation logs |
| Actions destructrices | blocked_actions |
| Consommation incontrolee | max_requests_per_hour + budget alerts |
| Usurpation d'identite | session_timeout + auth renforcee |
| Propagation cross-agent | Isolation inter-dossiers |
| Faux rapports de completion | state_verification |
| Prise de controle partielle | operational limits + human_oversight |

### 2. Stanford CS230 Study Guide
Integre dans Gardien des Normes + Security Audit. 3 dimensions:
- **Autonomie IA:** Niveau Low/Medium/High → DPIA si High
- **RAG > Fine-Tuning:** Donnees dans index controlable, auditable, supprimable (Art. 17)
- **Tracabilite IA:** Sans traces LLM = impossible justifier decision (Art. 22)

Ces 3 dimensions = notre differenciateur vs auditeurs RGPD classiques.

---

## HYPOTHESES CLES

**H1:** Les PME preferent un package cle-en-main vs apprendre (70%)
**H2:** Les templates vertical reduisent le temps d'implementation de 50% (60%)
**H3:** Taux conversion audit → implementation > 30% (50%)
**H4:** Les cabinets paient 5-12K CHF pour un Agent Squad implemente (55%)
**H5:** "Agent Squad" vend mieux que "1 agent RAG" (70%)

**Test MVP:** Proposer a 5 PME auditees. Si 2+ acceptent → H1+H4 valides.

---

## PITFALLS

**Architecture:**
- Sur-customisation: Resister. Template = 50%, pas 80%. Si client veut 50%+ custom → Enterprise.
- Timeline irréaliste: 4 semaines = chimeres. Vendre 6-8 semaines.
- Data residency: Toujours verifier AVANT Phase 1. Client CH qui exige data CH + modele US = conflit.
- High-risk AI Act: DPIA obligatoire → ajouter 2-3 jours au planning.
- Secret professionnel/bancaire: Infrastructure CH non-negociable. Pas de workaround.

**Securite:**
- Pas de state_verification: L'agent peut mentir sur l'etat. Obligatoire depuis arXiv:2602.20021.
- Guardrails apres coup: Si on rajoute les guardrails apres implementation, c'est du patchwork. Architecture by design = guardrails AVANT code.
- Modele unique: Si le client depend d'un seul modele, un changement d'API = arret. Model-agnostic par defaut.

**Business:**
- Zero references: Sans client beta + temoignage, le premier client achete sur parole. Faire 3-5 beta AVANT lancement commercial.
- Pas de demo live: Le client doit VOIR l'agent travailler. Demo RAG sur donnees anonymisees = 5 min qui vend mieux que 50 slides.
- Pas de garantie: Offrir 4 sem gratuites ou 50% remboursement si non-fonctionnel.
- Monitoring sous-pricé: CHF 500/mois = pas assez. Minimum CHF 1'000-1'500. Ou automatiser avec dashboard + alertes.
- Formation insuffisante: 2h = trop peu. Minimum 3 sessions. Le client qui comprend pas l'agent churn apres 2 mois.

---

## VOCABULAIRE PROFESSIONNEL

| Ne pas dire | Dire | Pourquoi |
|---|---|---|
| "agent" (seul) | "equipe d'agents specialises" | Vend une equipe, pas un outil |
| "chatbot" | "Agent Squad" | Chatbot = depreciatif |
| "audit" | "conformite integree" | Audit = peur, integree = feature |
| "guardrails" | "protections metier" | Guardrails = technique, protections = metier |
| "RAG" | "base de connaissances verifiee" | RAG = jargon, base verifiee = concret |
| "zero setup" | "zero friction client" | On setup POUR eux |
| "plug-and-play" | "cle-en-main" | FR-CH, pas Silicon Valley |
| "anti-hallucination" | "sources verifiees FR-CH" | Pas negatif, positif |
| "sandbox" | "agent isole + protections" | Plus precis |
| "skills" | "competences metier" | Pas anglicisme |
| "data sovereignty" | "data residency CH" | Technique, pas politique |

---

## INFRASTRUCTURE: DESIGN FOR K8S, DEPLOY DOCKER

**Principe:** Architecture K8s-compatible deployee sur Docker Compose aujourd'hui. Migration k3s quand la scale l'exige. L'auditeur ne juge pas l'outil, il juge la tracabilite et l'isolation.

### Pourquoi pas K8s maintenant

| Raison | Fait |
|---|---|
| 0-5 clients | 3-9 containers. K8s gere 1000+. Overkill. |
| Team de 1 | K8s = 3+ mois maitrise. Ops burden sur le consulting. |
| Cout minimum K8s | 3 nodes HA = CHF 150-300/mois. Pour 0 clients. |
| Client PME s'en fout | Veulent "ca marche", pas "c'est du K8s" |
| Single point of failure | Si seul Thierry comprend l'infra = risque |

### Pourquoi K8s demain (quand signal depasse)

| Signal | Seuil | Action |
|---|---|---|
| Clients simultanes | > 8-10 | Un VPS/client = chaos de gestion |
| Agents par client | > 5 | Docker Compose scale mal au-dela |
| Auto-scaling necessaire | Oui | K8s HPA = la reponse |
| Audit client exige isolation infra | Oui | NetworkPolicy > bridge network |
| Team > 1 personne | Oui | Plus de mains pour l'ops |
| Certification ISO 27001 | Oui | K8s + policies documentees |

### Cible de migration: k3s

k3s = K8s certifie, meme API, single binary, 512MB RAM. Parfait pour VPS. Migration Docker→k3s progressive: un namespace a la fois, un client a la fois.

```
AUJOURD'HUI (0-5 clients)              DEMAIN (8-10+ clients)
┌──────────────────────────┐           ┌──────────────────────────┐
│ Docker Compose            │           │ k3s (lightweight K8s)     │
│ + 7 regles K8s-compatibles│    →      │ ou managed K8s            │
│                           │           │ (Exoscale SKS, OVH)      │
│ 1 VPS par client          │           │ Namespace par client      │
│ Traefik reverse proxy     │           │ Ingress + NetworkPolicy   │
│ Docker secrets            │           │ K8s Secrets + etcd encrypt│
│ docker-compose.yaml       │           │ Helm charts               │
│ Backup script             │           │ Velero + CRDs             │
└──────────────────────────┘           └──────────────────────────┘
     CHF 20-50/mois/client                 CHF 50-100/mois/client
```

### LES 7 REGLES K8S-COMPATIBLES (appliquees en Docker aujourd'hui)

Respecter ces 7 regles = migration k3s est un `kubectl apply`, pas une refonte.

**Regle 1: Un container = un agent (jamais de monolithe)**
```yaml
# MAUVAIS (non-K8s-compatible):
#   container: "cortex-all-agents"  → 3 agents + orchestrateur + DB

# BON (K8s-compatible):
tri-assist:
  image: cortex-leman/agent:${AGENT_VERSION}
synthese-assist:
  image: cortex-leman/agent:${AGENT_VERSION}
rappel-assist:
  image: cortex-leman/agent:${AGENT_VERSION}
orchestrator:
  image: cortex-leman/orchestrator:${AGENT_VERSION}
postgres:
  image: postgres:16
```

**Regle 2: Configuration via environnement, pas hardcoded**
```yaml
tri-assist:
  image: cortex-leman/agent:${AGENT_VERSION}
  environment:
    - AGENT_ROLE=tri
    - AGENT_SQUAD=${SQUAD_NAME}
    - LLM_PROVIDER=${LLM_PROVIDER}
    - LLM_MODEL=${LLM_MODEL}
    - DATA_RESIDENCY=${DATA_RESIDENCY}
    - LOG_LEVEL=${LOG_LEVEL}
    - GUARDRAILS_CONFIG=/config/guardrails.yaml
  # K8s: ConfigMap + Secrets = meme pattern
  # Jamais de valeurs en dur. Tout en .env ou secrets.
```

**Regle 3: Health checks obligatoires**
```yaml
tri-assist:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 10s
  # K8s: livenessProbe + readinessProbe = meme concept
  # Audit: "Comment detectez-vous un agent defaillant?" → health checks.
```

**Regle 4: Resource limits par container**
```yaml
tri-assist:
  deploy:
    resources:
      limits:
        cpus: "1.0"
        memory: 512M
      reservations:
        cpus: "0.25"
        memory: 128M
  # K8s: requests/limits = identique
  # Anti-DoS (LLM04 OWASP): un agent ne peut pas consommer tout le serveur
  # Audit: "Comment prevenez-vous le debordement?" → resource limits documentees.
```

**Regle 5: Reseau isole par client**
```yaml
networks:
  client-${CLIENT_ID}-net:
    driver: bridge
    internal: true  # Pas d'acces externe sauf via Traefik
  proxy-net:
    driver: bridge  # Traefik seul sur ce reseau

services:
  traefik:
    networks: [proxy-net, client-${CLIENT_ID}-net]
  tri-assist:
    networks: [client-${CLIENT_ID}-net]  # Isole dans son reseau client
  # K8s: NetworkPolicy = meme isolation
  # Audit RGPD: "Comment isolez-vous les clients?" → "Reseau isole par client, documente."
```

**Regle 6: Secrets separes du code**
```yaml
tri-assist:
  environment:
    - LLM_API_KEY_FILE=/run/secrets/llm_api_key
    - DB_PASSWORD_FILE=/run/secrets/db_password
  secrets:
    - llm_api_key
    - db_password

secrets:
  llm_api_key:
    file: ./secrets/llm_api_key.txt  # Pas dans git, pas dans compose
  # K8s: Secrets + etcd encryption = meme pattern
  # Jamais dans docker-compose.yaml, jamais dans .env versionne
```

**Regle 7: Logs structures JSON**
```json
{"ts":"2026-04-22T10:30:00Z","agent":"tri-assist","squad":"acme-comptable","client":"acme","action":"classify","result":"invoice","risk":"low","latency_ms":120,"guardrail_triggered":false}
```
```yaml
tri-assist:
  environment:
    - LOG_FORMAT=json
    - LOG_LEVEL=info
  logging:
    driver: json-file
    options:
      max-size: "10m"
      max-file: "3"
  # K8s: Fluentd/Promtail → Loki/Elasticsearch = meme format
  # Docker: idem. Format identique = migration transparente.
  # Audit Art. 30 RGPD: traces LLM obligatoires. Format JSON = auditable.
```

### SECTION INFRASTRUCTURE DANS L'ARCHITECTURE DOCUMENT

A inclure dans chaque Architecture Document client:

```yaml
infrastructure:
  current: "docker-compose"
  k8s_compatible: true
  migration_path: "k3s"
  migration_trigger: "8+ clients simultanes ou 5+ agents par client"

  isolation:
    method: "network_per_client"
    documented: true
    auditable: true
    verification: "docker network inspect client-{id}-net"

  secrets:
    method: "docker_secrets"
    encrypted_at_rest: false  # true avec k3s + etcd
    rotation: "manual"        # "automated" avec k3s + SealedSecrets
    never_in_code: true
    never_in_git: true

  resources:
    limits_per_container: true
    method: "docker_resource_limits"
    anti_dos: true  # LLM04 OWASP

  health:
    checks: true
    method: "docker_healthcheck"
    interval: "30s"
    alerting: "manual"  # "prometheus" avec k3s

  logging:
    format: "structured_json"
    fields: ["ts","agent","squad","client","action","result","risk","latency_ms","guardrail_triggered"]
    aggregation: "none"        # "loki" avec k3s
    retention_days: 90

  backup:
    method: "script_cron"
    frequency: "daily"
    tested: false             # tester AVANT premier client
    offsite: false            # true avec k3s + Velero

  data_residency:
    vps_location: "CH"        # Exoscale/Infomaniak
    provider: ""              # a specifier par client
    documented: true
    verifiable: true           # IP geolookup = preuve

  networking:
    reverse_proxy: "traefik"
    tls: true
    tls_version: "1.3"
    certificate: "letsencrypt"
    internal_only: true        # agents non accessibles depuis internet
```

### ARGUMENT AUDITEUR

**Docker sans K8s-compatible:**
> Auditeur: "Comment isolez-vous les donnees?"
> → Reponse vague, improvisee.

**Docker K8s-compatible (notre position):**
> "Chaque agent est isole dans son container avec resource limits, reseau isole par client, secrets separes, et health checks. L'architecture est declarative en YAML, versionnee en git. C'est K8s-compatible avec un path de migration documente."
> → Architecture Document + docker-compose.yaml = suffit pour audit.

**k3s demain:**
> "Chaque client a son namespace avec NetworkPolicy, RBAC, ResourceQuota, et AuditLog. Les deploiements sont traces via Helm."
> → L'auditeur n'a rien a redire.

**L'audit ne juge pas l'outil. Il juge la tracabilite et l'isolation.** Docker K8s-compatible = tracabilite et isolation documentees. C'est suffisant.

---

## LIVRABLE: SCHEMA D'ARCHITECTURE CLIENT

**Quand:** Phase 1, apres validation de l'Architecture Document. Avant Phase 2.

**Pourquoi:** Le client doit VOIR l'installation complete avant qu'on code quoi que ce soit. Le schema est le pont entre l'Architecture Document (technique) et la comprehension client (visuelle).

**Comment:** Utiliser le skill `architecture-diagram` pour generer un fichier HTML/SVG autonome.

**Structure du schema (6 couches):**

```
1. CLIENT PME FR-CH          — Point d'entree, secteur vertical
2. ONBOARDING                — 3 etapes: Audit → Classification → Choix vertical
3. AGENT SQUAD v4.0          — 3 agents (Tri/Analyse/Action) + Orchestrateur
4. INFRASTRUCTURE K8s        — 3 containers isoles + 7 regles + n8n + Vector DB + Redis
5. CONFORMITE RGPD-IA        — AI Act + RGPD + Guardrails + Data Residency + Secret pro + Specs vertical
6. INTEGRATIONS              — Email / Documents / Calendrier / n8n / Monitoring / Audit Trail
```

**Palette par couche:**
- Client: cyan (#22d3ee)
- Onboarding: amber (#fbbf24)
- Agent Squad: emerald (#34d399)
- Infrastructure: violet (#a78bfa)
- Conformite: rose (#fb7185)
- Integrations: orange (#fb923c)

**Fichier de reference:** `~/cortex-leman-installation-vision.html` (schema 7 couches, 6 verticals, 6 info cards, tableau comparatif vs LobsterAI/Accio, timeline 6-8 sem, pricing)

**Format:** HTML autonome, zero dependances, ouvrable dans tout navigateur. Imprimable en PDF si besoin.

**Personnalisation par client:** Remplacer les labels generiques par le nom du client et son vertical. Adapter les resource limits et data residency selon l'Architecture Document.

---

## EVOLUTION FUTURE

- Templates supplementaires: immobilier, assurance, education
- Self-service: portail client pour configurer son agent (80% du template)
- Marketplace: vendre les templates seuls (CHF 500-1000/template)
- Certification: label "Cortex Leman Compliant" pour agents audites
- API: endpoints pour integration directe dans les SI clients
- Observatoire: monitorer les communautes IA FR pour signaux de demande
- Migration k3s: quand 8+ clients ou 5+ agents par client
