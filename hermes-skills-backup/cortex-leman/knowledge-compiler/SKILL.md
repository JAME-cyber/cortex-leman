---
name: Knowledge Compiler
category: cortex-leman
version: 1.0.0
description: |
  Workflow generique pour compiler les resultats de recherche en fichiers references structurees.
  Transforme les donnees jetables (sessions, RAG) en connaissances persistantes et interconnectees.
  Anti-hallucination integre avec fact-checking et statut de verification.

triggers:
  - "compiler connaissance"
  - "knowledge compile"
  - "compile research"
  - "sauver insights"
  - "persister recherche"
  - "compiled knowledge"

prerequisites:
  - Acces filesystem pour ecrire dans skills/

---

# Knowledge Compiler v1.0

## ROLE

Transformer les resultats de recherche et d'analyse en connaissances persistantes, structurees et interconnectees. Eviter que les insights se dissolvent entre les sessions.

## PRINCIPE

```
RAG jetable: recompute a chaque requete, non navigable, non cumulatif
Wiki compile: compute une fois, navigable, cumulatif, interconnecte
```

Chaque sortie de pipeline = entree potentielle d'un autre pipeline. Rien ne se dissout. Tout se compile.

## ARCHITECTURE

```
┌──────────────────────────────────────────────────────┐
│               KNOWLEDGE COMPILER                      │
├──────────────────────────────────────────────────────┤
│                                                       │
│  INPUT (sources de connaissance)                      │
│  ├── SocialPulse leads & insights                     │
│  ├── Feynman research results                         │
│  ├── ArXiv papers                                     │
│  ├── Gardien des Normes validations                   │
│  ├── Security audit findings                          │
│  └── Sessions passees (session_search)                │
│                                                       │
│  PIPELINE                                             │
│  ┌──────────────────────────────────────┐            │
│  │ 1. EXTRACTION                        │            │
│  │    Identifier les insights cles      │            │
│  │    dans les donnees source           │            │
│  └──────────────┬───────────────────────┘            │
│                 ▼                                     │
│  ┌──────────────────────────────────────┐            │
│  │ 2. STRUCTURATION                     │            │
│  │    YAML frontmatter + markdown       │            │
│  │    Tags, categories, liens           │            │
│  └──────────────┬───────────────────────┘            │
│                 ▼                                     │
│  ┌──────────────────────────────────────┐            │
│  │ 3. ANTI-HALLUCINATION                │            │
│  │    Fact-check points sensibles       │            │
│  │    Web search verification           │
│  │    Statut verified/to_verify         │            │
│  └──────────────┬───────────────────────┘            │
│                 ▼                                     │
│  ┌──────────────────────────────────────┐            │
│  │ 4. CROSS-REFERENCING                 │            │
│  │    Liens vers skills existants       │            │
│  │    Liens vers autres references      │            │
│  │    Mise a jour du MOC Cortex Leman   │            │
│  └──────────────┬───────────────────────┘            │
│                 ▼                                     │
│  ┌──────────────────────────────────────┐            │
│  │ 5. PERSISTENCE                       │            │
│  │    Sauver dans skill/ ou references/ │            │
│  │    Updater compiled/ si SocialPulse  │            │
│  │    Commit si git repo                │            │
│  └──────────────────────────────────────┘            │
│                                                       │
│  OUTPUT                                               │
│  ├── Fichiers references dans skills/                 │
│  ├── Section compiled/ dans SocialPulse               │
│  ├── MOC Cortex Leman mis a jour                     │
│  └── fact-check-log.md avec statuts                  │
│                                                       │
└──────────────────────────────────────────────────────┘
```

## FORMAT STANDARD

Chaque fichier compile suit ce format:

```yaml
---
# YAML FRONTMATTER (obligatoire)
title: "Titre descriptif"
compiled_date: 2026-04-19
source: "feynman-research|socialpulse|arxiv|session|manual"
source_ref: "reference vers la source originale"
category: "rgpd-ia|security|compliance|vertical|methodology"
tags: [tag1, tag2, tag3]
verified: true|false|partial
verified_date: 2026-04-19
cross_refs:
  - skill: nom-du-skill
    section: "section concernee"
  - skill: autre-skill
    section: "section concernee"
---

# Titre

## Resume
[1-3 phrases. Que dit ce fichier?]

## Contenu
[Le contenu compile, structure avec headers]

## Sources
[Liste des sources avec URLs/references]

## A verifier
[Points non verifies, si verified != true]
```

## TYPES DE COMPILATION

### 1. Research → Reference

Quand Feynman research ou ArXiv search produit des resultats:

```
Input: Resultats de recherche sur "AI Act obligations PME"
Output: references/ai-act-pme-obligations.md dans le skill concerne
```

Processus:
- Extraire les points cles de la recherche
- Structurer en format standard
- Fact-check: verifier les references legislatives avec web search
- Cross-ref: lier au Gardien des Normes et Agent Implementation
- Sauver dans le skill le plus pertinent

### 2. SocialPulse → Sector Insights

Quand un batch SocialPulse est termine:

```
Input: Leads qualifies + scores + objections
Output: compiled/{campaign}/sector-insights.md, objection-map.md
```

Voir section COMPILED KNOWNOWLEDGE dans socialpulse-lead-gen pour le detail.

### 3. Audit → Template

Quand un audit RGPD-IA ou security-audit est termine:

```
Input: Rapport d'audit complet
Output: templates/vertical/{sector}/audit-findings.md
```

Processus:
- Anonymiser les donnees client
- Extraire les patterns recurrents
- Creer un template de findings par vertical
- Cross-ref avec Gardien des Normes

### 4. Session → Precedent

Quand une session produit des insights reutilisables:

```
Input: session_search resultats
Output: references/ dans le skill concerne
```

Processus:
- Identifier les decisions/insights reutilisables
- Structurer en format standard
- Sauver dans le skill le plus pertinent

## ANTI-HALLUCINATION

### Regles de fact-checking

1. **Personnes**: verifier nom, dates, affiliation avec web search (2 requetes min)
2. **Chiffres precis**: verifier avec source officielle
3. **References legislatives**: verifier numero d'article, date de publication
4. **Controverses**: presenter les deux cotes, ne pas prendre position

### Statuts de verification

| Statut | Signification | Action requise |
|--------|--------------|----------------|
| `verified: true` | Fact-check avec web search, source confirmee | Aucune |
| `verified: partial` | Certains points verifies, d'autres non | Verifier les points manquants |
| `verified: false` | Pas encore fact-check | Fact-check obligatoire |
| `verified: to_verify` | Point specifique a verifier | Verifier ce point |

### fact-check-log.md

Chaque compilation genere ou update un log:

```markdown
# Fact Check Log - [Date]

## [Fichier compile]
- [ ] Point a verifier: "Amende CNIL jusqu'a 4% du CA"
  - Source claim: Regulation EU 2016/679 Art. 83
  - Verification: [URL de verification]
  - Statut: verified
  
- [ ] Point a verifier: "GLM-5V-Turbo sorti en mars 2026"
  - Source claim: Z.ai announcement
  - Verification: non trouve
  - Statut: to_verify
```

## WORKFLOW D'EXECUTION

### Compilation manuelle

```
"Compile les resultats de cette recherche dans le skill X"
"Knowledge compiler: sauve ces insights SocialPulse"
"Compile la session dans les references du Gardien"
```

### Compilation automatique (recommande)

Apres chaque pipeline qui produit des insights:
1. Identifier si les resultats sont reutilisables
2. Si oui, lancer la compilation automatiquement
3. Fact-check les points sensibles
4. Sauver dans le skill concerne
5. Updater le MOC

### Commande rapide

```
"knowledge-compiler: compile [source] into [skill]"
```

L'agent va:
1. Charger ce skill
2. Identifier le type de compilation (research/socialpulse/audit/session)
3. Executer le pipeline correspondant
4. Sauver le resultat
5. Confirmer la compilation

## CROSS-REFERENCING AVEC MOC

Chaque fichier compile doit etre reference dans le MOC Cortex Leman:

1. Identifier dans quel cluster du MOC le fichier appartient
2. Ajouter une entree avec chemin, description, cross-refs
3. Updater les connexions si necessaire

Voir skill `cortex-leman-moc` pour la structure complete. Le MOC est la carte navigable de tout l'ecosysteme. Chaque compilation doit updater la section CONNAISSANCES COMPILEES du MOC.

## INTEGRATION AVEC L'ECOSYSTEME

| Skill | Role dans la compilation |
|-------|-------------------------|
| SocialPulse | Source: leads, insights sectoriels, objections |
| Feynman Research | Source: resultats de recherche structuree |
| Gardien des Normes | Source + Consumer: validations RGPD, precedents compliance |
| Agent Implementation | Consumer: sector-insights pour les templates vertical |
| Security Audit | Source: findings recurrents par type de codebase |
| L'Architecte Lemanique | Consumer: insights strategiques cross-campaign |
| L'Ingenieur de Flux | Consumer: patterns d'automatisation recurrents |
| Le Narrateur Augmente | Consumer: insights pour personnaliser les rapports |
| L'Oeil de Cortex | Source: veille technologique ArXiv |
| cortex-leman-moc | Index de toutes les connaissances compilees |

## PITFALLS

- Ne pas compiler des donnees client sans anonymisation
- Ne pas compiler du contenu non fact-check (statut to_verify = ok, false = non)
- Ne pas dupliquer: verifier si l'info existe deja dans un skill avant de compiler
- Ne pas over-compiler: seulement les insights reutilisables, pas les details de session
- Fact-check coute du temps/credits: prioriser les points sensibles (personnes, chiffres, lois)
- Les fichiers compiles sont dans skills/ = accessibles par tous les skills. Ne pas mettre de donnees confidentielles.

## FICHIERS

```
knowledge-compiler/
├── SKILL.md           ← Ce fichier
└── templates/
    └── compiled-file-template.md  ← Template format standard
```
