---
name: Cortex Leman MOC
category: cortex-leman
version: 1.0.0
description: |
  Map of Content pour l'ecosysteme Cortex Leman.
  Carte des connexions entre skills, pipelines, et connaissances compilees.
  Reference centrale pour naviguer l'architecture.

triggers:
  - "MOC"
  - "carte skills"
  - "map of content"
  - "ecosysteme cortex"
  - "connexions skills"

---

# Cortex Leman - Map of Content

## VUE D'ENSEMBLE

```
                        ┌─────────────────────┐
                        │  CORTEX LEMAN MOC    │
                        │  (Ce fichier)        │
                        └──────────┬──────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
    ┌─────▼─────┐          ┌──────▼──────┐         ┌───────▼───────┐
    │ PIPELINE  │          │  AGENTS     │         │  INFRA &      │
    │ COMMERCIAL│          │  METIER     │         │  OUTILS       │
    └─────┬─────┘          └──────┬──────┘         └───────┬───────┘
          │                        │                        │
  SocialPulse          Gardien des Normes        Docker Infra
  Agent Impl.          L'Architecte              Security Audit
  Marketing            L'Ingenieur de Flux       Command Risk
  Narrateur            L'Oeil de Cortex          Knowledge Compiler
```

## CLUSTER 1: PIPELINE COMMERCIAL

Le pipeline de generation de revenu, du lead a la retention.

```
SocialPulse (lead gen)
    │ leads qualifies
    │ risk_indicator = "high"
    ▼
Email d'approche (personalise)
    │ reponse positive
    ▼
Diagnostic gratuit 30min
    │ micro-engagements (oui)
    │ quantification douleur
    ▼
Audit RGPD-IA (Gardien des Normes)
    │ recommandations priorisees
    ▼
Agent Implementation Service
    │ programme 4 semaines
    │ Starter / Business / Enterprise
    ▼
Conformite Continue
    │ monitoring mensuel
    │ guardrails updates
    ▼
Flywheel: nouveau besoin → SocialPulse
```

### Skills du cluster

| Skill | Role | Connexions |
|-------|------|-----------|
| **SocialPulse** | Lead gen B2B multi-vertical | → Agent Implementation, → Gardien, → Knowledge Compiler |
| **Agent Implementation Service** | Implementation agents IA conformes | ← SocialPulse, ← Gardien, → Narrateur |
| **Hybrid Marketing Package** | Packages marketing hybrides | → SocialPulse (materials), → Narrateur |
| **Compliance Content Generator** | Generateurs de contenu conformes | ← Gardien (validation), → Agent Impl. |
| **Cortex Leman Compliance Generator** | SaaS hybride texte+images conforme | ← Gardien, → Narrateur |

### Flux de donnees

```
SocialPulse ──leads──> Agent Implementation
     │                       │
     │ insights              │ templates
     ▼                       ▼
compiled/              templates/
sector-insights.md     vertical configs
objection-map.md       agent-config.yaml
pricing-sensitivity.md workflows n8n
compliance-gaps.md
     │
     ▼
Knowledge Compiler ──persist──> skills/references/
```

## CLUSTER 2: AGENTS METIER

Les agents specialises qui executent le travail client.

```
                    ┌─────────────────────┐
                    │  L'ARCHITECTE       │
                    │  LEMANIQUE (CSO)    │
                    │  Strategie, ROI,    │
                    │  Go/No-Go           │
                    └──────────┬──────────┘
                               │ orchestre
          ┌────────────────────┼────────────────────┐
          │                    │                    │
    ┌─────▼─────┐      ┌──────▼──────┐      ┌──────▼──────┐
    │  GARDIEN  │      │  INGENIEUR  │      │  NARRATEUR  │
    │  DES      │      │  DE FLUX    │      │  AUGMENTE   │
    │  NORMES   │      │             │      │             │
    │ Compliance│      │ Automation  │      │ Brand/UX    │
    │ RGPD/AI   │      │ Workflows   │      │ Reporting   │
    └─────┬─────┘      └──────┬──────┘      └──────┬──────┘
          │                    │                    │
          │ validation         │ execution          │ livraison
          ▼                    ▼                    ▼
    Kill Switch          n8n/Python           PDF/HTML/Slides
    Guardrails           APIs/MCP             Infographies
    Precedents           Monitoring           Presentations
```

### Skills du cluster

| Skill | Role | Connexions |
|-------|------|-----------|
| **Le Gardien des Normes** | Compliance Officer FR-CH | → Agent Impl. (guardrails), → Knowledge Compiler (precedents) |
| **L'Architecte Lemanique** | CSO strategique | ← tous les agents (rapports), → decisions go/no-go |
| **L'Ingenieur de Flux** | Automation & code | ← Gardien (validation), → Narrateur (output), → n8n |
| **Le Narrateur Augmente** | Brand & UX | ← Ingenieur (donnees), ← Gardien (conformite contenu) |
| **L'Oeil de Cortex** | Vision numerique | → Gardien (anomalies), → Knowledge Compiler (veille) |
| **Command Risk Classification** | Safety layer | ← Gardien (escalation), → kill switch |

### Chaines de commande typiques

**Audit RGPD-IA complet:**
```
SocialPulse (detecte lead) → Gardien (audit) → Ingenieur (automatisation corrections) → Narrateur (rapport)
```

**Implementation agent conforme:**
```
Gardien (validation guardrails) → Ingenieur (implementation) → Gardien (re-validation) → Narrateur (doc client)
```

**Veille technologique:**
```
L'Oeil de Cortex (ArXiv scan) → Knowledge Compiler (compile) → Gardien (update precedents) → Architecte (strategie)
```

## CLUSTER 3: INFRASTRUCTURE & OUTILS

Le socle technique qui supporte tout l'ecosysteme.

```
┌────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE                     │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │  Docker   │  │ Security │  │   Knowledge      │ │
│  │  Infra    │  │  Audit   │  │   Compiler       │ │
│  │           │  │          │  │                  │ │
│  │ Compose   │  │ OWASP    │  │ Research→Ref     │ │
│  │ Stack     │  │ LLM Top10│  │ Anti-halluc.     │ │
│  │ Deploy    │  │ CVSS     │  │ Cross-refs       │ │
│  └──────────┘  └──────────┘  └──────────────────┘ │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │ Pi       │  │ Single   │  │   FastAPI        │ │
│  │ Integr.  │  │ Purpose  │  │   (dev)          │ │
│  │          │  │ Tool     │  │                  │ │
│  │ Multi-   │  │ Design   │  │ Best practices   │ │
│  │ provider │  │ Pattern  │  │ Conventions      │ │
│  └──────────┘  └──────────┘  └──────────────────┘ │
│                                                     │
└────────────────────────────────────────────────────┘
```

### Skills du cluster

| Skill | Role | Connexions |
|-------|------|-----------|
| **Docker Infrastructure** | Stack Docker, deploy, debug | → tous les agents (runtime) |
| **Security Audit** | OWASP + LLM Top10 + RGPD | ← Gardien (compliance), → Knowledge Compiler |
| **Knowledge Compiler** | Persistance des connaissances | ← tous les skills (source), → MOC (index) |
| **Pi Integration** | Framework Pi multi-provider | → Ingenieur (skills runtime) |
| **Single Purpose Tool Design** | Decomposition micro-outils | → Ingenieur (architecture) |
| **FastAPI** | Conventions de dev | → Ingenieur (APIs) |

## CLUSTER 4: RECHERCHE & VEILLE

Les pipelines de recherche qui alimentent les connaissances.

```
ArXiv ──papers──> L'Oeil de Cortex ──veille──> Knowledge Compiler
                                    │
                                    ▼
                              Gardien des Normes
                              (update precedents)

Feynman Research ──results──> Knowledge Compiler ──refs──> Skills

Enterprise Research ──scraping──> SocialPulse (enrichment)
                                │
                                ▼
                          compiled/ sector-insights
```

### Skills hors category Cortex Leman mais connectes

| Skill | Categorie | Connexion |
|-------|-----------|----------|
| **Feynman Style Research** | research | → Knowledge Compiler |
| **ArXiv** | research | → L'Oeil de Cortex |
| **Enterprise Research Scraping** | software-dev | → SocialPulse |
| **L'Oeil de Cortex ArXiv Integration** | data-science | → L'Oeil de Cortex |
| **LLM Wiki** | research | → Knowledge Compiler (pattern similaire) |

## CLUSTER 5: CONCERNS TRANSVERSAUX

Les preoccupations qui impactent tous les clusters.

```
┌─────────────────────────────────────────────────┐
│              CONCERNS TRANSVERSAUX               │
│                                                  │
│  RGPD / AI Act ──── Gardien des Normes          │
│  Securite ───────── Security Audit              │
│  Souverainete ───── Docker local, pas cloud     │
│  Budget ─────────── Cost-effective tools        │
│  Qualite ────────── Verification before compl.  │
│  Compilation ────── Knowledge Compiler          │
│                                                  │
└─────────────────────────────────────────────────┘
```

## CHEMINS CRITIQUES

Les parcours les plus importants pour le business:

### Chemin 1: Lead → Client (revenu principal)
```
SocialPulse → Diagnostic → Gardien → Agent Implementation → Conformite Continue
```
Cout: ~$11/50 leads | Revenue: CHF 3'000-15'000/client | ROI: 27x-136x

### Chemin 2: Recherche → Differentiation (avantage concurrentiel)
```
ArXiv/Feynman → Knowledge Compiler → Gardien (precedents) → Marketing (argument Stanford)
```
Differentiateur vs auditeurs RGPD classiques: 3 dimensions (Autonomie IA, RAG>fine-tuning, Tracabilite IA)

### Chemin 3: Audit → Template (scalabilite)
```
Gardien/Security Audit → Knowledge Compiler → Templates vertical → Agent Implementation
```
Chaque audit enrichit les templates pour le client suivant. Effet cumulatif.

## CONNAISSANCES COMPILEES

Index des connaissances persistees via Knowledge Compiler:

### SocialPulse compiled/
| Fichier | Vertical | Derniere MAJ | Verified |
|---------|----------|-------------|----------|
| (a peupler apres premier batch) | | | |

### Skills references/
| Skill | Fichiers references | Derniere MAJ |
|-------|-------------------|-------------|
| socialpulse-lead-gen | campaign-template.yaml, campaigns/cortex-leman-rgpd.yaml | 2026-04-19 |
| agent-implementation-service | templates/ (6 verticals) | 2026-04-19 |
| knowledge-compiler | templates/compiled-file-template.md | 2026-04-19 |

### fact-check-log
| Point | Source | Statut | Date verification |
|-------|--------|--------|------------------|
| Amende CNIL 4% CA | EU 2016/679 Art. 83 | verified | 2026-04-19 |
| Agents of Chaos (Shapira 2026) | arXiv:2602.20021 | verified | 2026-04-19 |
| Douleur prix = insula (Knutson 2007) | Neuron 53(1) | verified | 2026-04-19 |

## NAVIGATION RAPIDE

**Je veux...**
- ...generer des leads → SocialPulse → campagne YAML → pipeline
- ...auditer un client → Gardien des Normes → Security Audit
- ...implementer un agent → Agent Implementation Service → templates vertical
- ...compiler de la recherche → Knowledge Compiler → format standard
- ...automatiser un workflow → L'Ingenieur de Flux → n8n
- ...creer un rapport premium → Le Narrateur Augmente → PDF/HTML
- ...decider d'une strategie → L'Architecte Lemanique → ROI/go-no-go
- ...faire la veille techno → L'Oeil de Cortex → ArXiv
- ...comprendre l'ecosysteme → Ce MOC

## MAINTENANCE

Ce MOC doit etre mis a jour quand:
- Un nouveau skill est cree dans la categorie cortex-leman
- Une nouvelle connexion entre skills est identifiee
- Knowledge Compiler compile de nouvelles references
- Un chemin critique est modifie

Derniere mise a jour: 2026-04-19
