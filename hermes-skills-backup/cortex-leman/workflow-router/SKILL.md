---
name: workflow-router
description: "Scope architecture before building. Use for new automation."
version: 1.0.0
author: Hermes Agent (Tars)
license: MIT
metadata:
  hermes:
    tags: [triage, architecture, scoping, cortex-leman, automation]
    related_skills: [bounded-agent-execution, stage-execution-loop, plan]
---

# Workflow Router — Triage d'Architecture

## Quoi

**Gate de scoping obligatoire** avant tout build d'automatisation. Pose les bonnes questions, recommande l'architecture la plus simple, sépare le déterministe du contextuel.

## Pourquoi

**Problème** (@mathieuhq, août 2026 + expérience Cortex Leman):
- On choisit l'outil (prompt, skill, cron, n8n, agent) **avant** d'avoir cadré la tâche
- Résultat: LLM sur étapes déterministes (overkill), 40 branches n8n pour décision contextuelle (cauchemar), agent autonome sur tâche à gate humaine (risque client)

**Solution:** 5 questions + matrice de décision. Le triage prend 5 min. Le mauvais choix coûte des semaines.

---

## Le Gate — 5 Questions

### Q1: DÉCLENCHEUR ?

| Réponse | Architecture |
|---|---|
| Événement externe (email, webhook, form) | **Event-driven** |
| Horodatage (tous les jours à 8h) | **Cron** |
| Action humaine | **On-demand** (skill, CLI) |
| Continue (monitoring) | **Daemon/Watchdog** |

### Q2: DÉTERMINISTE ou CONTEXTUEL ?

**Test:** "Un script Python avec if/else exacts marche à 100%?"

| Réponse | Architecture |
|---|---|
| Oui | **Script/Cron** — PAS de LLM |
| Partiellement | **Script + LLM post-processing** |
| Non (contexte, ton, jugement) | **Agent/LLM** |

**Règle d'or:** Si un `if/else` suffit, NE PAS utiliser un LLM.

### Q3: Tolérance aux ERREURS ?

| Réponse | Contraintes |
|---|---|
| Zéro (compliance, finance, légal) | **Validation humaine obligatoire** + dry-run |
| Faible (client-facing) | **Gate validation** + LLM verdict + règles dures |
| Moyenne (internal) | **Auto + notification** |
| Haute (R&D) | **Plein autonome** + log |

### Q4: Validation humaine ?

| Réponse | Architecture |
|---|---|
| Avant chaque exécution | **On-demand** |
| Avant envoi externe | **Draft → Review → Approve** |
| Post-exécution | **Auto + log** |
| Jamais | **Plein autonome** (rare) |

### Q5: RÉCURRENCE → Prix ?

| Réponse | Modèle |
|---|---|
| One-shot | **Projet** 2K-15K CHF |
| Récurrent | **Retainer** 500-3K CHF/mois |
| Événementielle | **Pay-per-use** |
| Continue | **Infogérance** mensuel |

---

## Matrice de Décision

| Combo | Architecture | Outils Hermes |
|---|---|---|
| Cron + Déterministe + Zéro erreur + Gate | Script + cron + dry-run | `terminal` + `bounded-agent-execution` |
| Event + Contextuel + Faible tolérance + Draft→Approve | Agent + gate validation | `delegate_task` + `signal-deliberation` |
| On-demand + Contextuel + Tolérance moyenne | Skill interactif | Skill + `plan` |
| Cron + Contextuel + Faible tolérance + Auto+notify | Agent cron + LLM verdict | `cronjob` + `signal-deliberation` |
| On-demand + Déterministe + Gate humaine | Script CLI simple | `terminal` — PAS de LLM |
| Event + Déterministe + Auto+log | Webhook + script | `a2a-webhook-pipeline` |
| Continue + Contextuel + Auto+notify | Daemon + watchdog | `service-watchdog-cron` |

---

## Les 3 Couches (à séparer)

```
COUCHE 1: Déterministe (script/cron) → if/else, bash, Python → JAMAIS de LLM
COUCHE 2: Contextuel (LLM/agent)     → jugement, ton, ambiguïté → L'IA brille
COUCHE 3: Accord humain (gate)       → validation, approbation → Rien ne sort sans
```

**Exemple Google Reviews Agent:**
- Couche 1: Cron 8h → fetch GMB API → trier (note ≥4 = positif, ≤2 = négatif)
- Couche 2: LLM génère la réponse selon le ton
- Couche 3: Draft → owner approuve via Telegram → envoi

---

## Anti-patterns

| Anti-pattern | Correctif |
|---|---|
| LLM pour trier emails par expéditeur | Script Python — déterministe |
| n8n 40 branches pour gérer le ton | Agent — le ton est contextuel |
| Agent autonome pour publier avis | Draft → Approve gate |
| Cron pour tâche one-shot | Script CLI on-demand |
| Script parse du langage naturel | LLM extraction |

---

## Output: Blueprint (1 page max)

```markdown
# Architecture Blueprint — [Projet]

## Triage
- Déclencheur: [type]
- Nature: [Déterministe/Contextuel/Hybride]
- Tolérance erreur: [Zéro/Faible/Moyenne/Haute]
- Validation humaine: [Où]
- Récurrence: [One-shot/Récurrent/Event/Continue]

## Architecture
[Couches 1-2-3 + outils]

## Stack Hermes
- Déterministe: [script/cron/webhook]
- LLM: [skill/agent/delegate_task]
- Validation: [gate/telegram]

## Prix
- Setup: [X CHF]
- Retainer: [X CHF/mois]

## Risques
- [Risque + mitigation]
```

---

## Intégration Pipeline B2B — Funnel 3 Tiers

Ce gate s'insère dans un funnel d'acquisition à 3 niveaux:

```
1. PROSPECT (scraper, MimikFlow)
       ↓
2. QUICK AUDIT Google Workspace AI (500-1K CHF) ←← LOW-TICKET ENTRY
   → Montre ce que Gmail/Sheets/NotebookLM peuvent déjà faire
   → Pas de build, juste de la sensibilisation + config rapide
   → Hook: "Vous payez Google Workspace mais n'utilisez pas l'IA incluse"
       ↓
3. AUDIT RGPD-IA COMPLET (2-4K CHF) ←← MID-TICKET
   → Diagnostic conformité + opportunités automatisation
   → Map chaque process manuel → $ économisé
   → Forwardable au associé/board
       ↓
4. → WORKFLOW ROUTER ← (CE SKILL — scoping technique)
       ↓
5. PROPOSITION (blueprint + prix)
       ↓
6. BUILD (stage-execution-loop + bounded-agent-execution)
       ↓
7. LIVRAISON + RETAINER (500-3K CHF/mois)
```

### Quick Audit Google — Checklist (500-1K CHF, ~2h)

| Vérifie | Ce qu'on montre au client |
|---|---|
| Gmail → Gemini search | "Pose une question, obtiens une réponse pas juste un email" |
| Gmail → réponses auto | "Le client n'écrit plus ses emails" |
| Sheets → Gemini | "Analyse tes données en langage naturel" |
| NotebookLM | "Upload vos docs → Q&A grounded + podcast auto" |
| Avatars vidéo | "Vidéos sans caméra" (si pertinent pour le secteur) |
| AI Studio | "Vibe-coder un outil interne" (si équipe technique) |

**Angle vente:** "Vous payez déjà Google Workspace. L'IA est incluse mais personne ne vous l'a montré."

---

## Sources

- @mathieuhq "workflow-router" (11 août 2026)
- Adapté FR-CH: 5 questions au lieu de 10
- Stack Hermes réelle, Pipeline B2B (Fact #99)
