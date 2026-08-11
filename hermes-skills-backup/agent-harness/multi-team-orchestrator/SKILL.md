---
name: multi-team-orchestrator
category: agent-harness
trigger: /workflow <name> [params]
description: Pilote les workflows multi-equipes (orchestrateur/leads/workers) definis dans ~/.hermes/agent-harness/multi-team-config.yaml. Also covers heavy-duty rapid multi-agent development pattern (JSON configs, async orchestration, kill switch) — see references/heavy_duty_rapid_pattern.md
---

# Multi-Team Orchestrator Skill

## ROLE
Tu es le cortex "cortex-harness". Tu charges `multi-team-config.yaml`, selectionnes le workflow (ex generate_ui, mairie_report), et orchestras la sequence complete :
1. Lire les variables utilisateur
2. Charger PROMPT/TILL_DONE spécifiques
3. Mettre à jour `TILL_DONE.md`
4. Déléguer aux leads -> workers
5. Lancer validators soft puis hard
6. Logguer l'execution

## INSTRUCTIONS
- Jamais d'exécution de code ou d'écriture directe: tu planifies/coordonnes.
- Utilise les leads uniquement pour déléguer.
- Chaque delegation documentée (lead, worker, objectif, modèle).
- Si un worker échoue → reroute vers un autre worker/modèle.
- Toujours déclencher validator soft puis hard avant completion.
- Utilise `scripts/generate_run_log.py` pour tracer start/complete.

## WORKFLOW COMMAND
```
/workflow <name> key1=value1 key2=value2
```
- name doit exister dans `workflows`.
- Les key=value alimentent Variables.

## CHECKLIST
1. Workflow chargé + variables validées
2. TILL_DONE initialisé et assigné
3. Délégations effectuées (teams)
4. Validator soft OK
5. Validator hard OK + log complet
6. Résumé final (décisions, livrables)

## OUTPUT FINAL
- Résumé mission
- Détails TILL_DONE (état)
- Livrables générés
- Anomalies/kill-switch si activé

---

## CRÉATION DE NOUVEAUX WORKFLOWS

### Pattern de Structure

Chaque workflow doit avoir la structure suivante:

```
~/.hermes/agent-harness/workflows/<workflow_name>/
├── PROMPT.md          # Instructions pour l'orchestrateur
├── TILL_DONE.md       # Checklist de completion
├── config.yaml        # Configuration détaillée du workflow
└── README.md          # Documentation utilisateur
```

### Étape 1: Créer le répertoire workflow

```bash
mkdir -p ~/.hermes/agent-harness/workflows/<workflow_name>
cd ~/.hermes/agent-harness/workflows/<workflow_name>
```

### Étape 2: Créer PROMPT.md

Format:
```markdown
# Workflow: <Nom Du Workflow>

## Variables
- variable1: Description
- variable2: Description

## Instructions
1. Orchestrateur => Lead : clarifier objectifs
2. Lead => Workers : assigner les tâches
3. Workers => Exécution
4. Validators => Validation

## Workflow Keywords
- delegate(team-name, objective)
- till_done(update)
- escalate(validator_name)
```

### Étape 3: Créer TILL_DONE.md

Format:
```markdown
# TILL DONE - <Nom Du Workflow>

- [ ] Mission comprise + variables verrouillées (Orchestrateur)
- [ ] Plan multi-team validé (Lead)
- [ ] Team X livrable {deliverable} (Lead -> Worker)
- [ ] Validator Soft OK
- [ ] Validator Hard + publication
```

### Étape 4: Créer config.yaml

Format:
```yaml
name: <workflow_name>
description: <Description du workflow>
category: <category>
version: 1.0.0

variables:
  - name: <variable1>
    type: <string|integer|enum>
    required: <true|false>
    default: <default_value>
    description: <Description>

teams:
  - name: <team_name>
    lead: <lead_id>
    workers:
      - <worker_id>
      - <worker_id2>

validators_required: <true|false>
kill_switch: <worker_id>

output:
  deliverables:
    - <deliverable1>
    - <deliverable2>
```

### Étape 5: Créer README.md

Format:
```markdown
# <Nom Du Workflow>

## Description
<Brief description>

## Utilisation

```bash
/workflow <workflow_name> <variables>
```

## Variables
[Tableau des variables]

## Équipes
[Description des équipes]

## Livrables
[Liste des livrables]
```

### Étape 6: Ajouter à multi-team-config.yaml

Ajouter le workflow à la section `workflows:`:

```yaml
workflows:
  <workflow_name>:
    prompt: ~/.hermes/agent-harness/workflows/<workflow_name>/PROMPT.md
    till_done: ~/.hermes/agent-harness/workflows/<workflow_name>/TILL_DONE.md
    teams:
      - name: <team_name>
        lead: <lead_id>
        workers:
          - <worker_id>
validators_required: <true|false>
```

### Exemple Complet: cortex_leman_audit

**Structure créée:**
```
~/.hermes/agent-harness/workflows/cortex_leman_audit/
├── PROMPT.md          (952 bytes)
├── TILL_DONE.md       (649 bytes)
├── config.yaml        (1.3 KB)
└── README.md          (2.3 KB)
```

**Configuration ajoutée à multi-team-config.yaml:**
```yaml
workflows:
  cortex_leman_audit:
    prompt: ~/.hermes/agent-harness/workflows/cortex_leman_audit/PROMPT.md
    till_done: ~/.hermes/agent-harness/workflows/cortex_leman_audit/TILL_DONE.md
    teams:
      - name: security
        lead: lead-securite
        workers:
          - gardien-des-normes
      - name: research
        lead: lead-service-client
        workers:
          - oeil-de-cortex
      - name: analysis
        lead: lead-production
        workers:
          - ingenieur-de-flux
      - name: documentation
        lead: lead-marketing
        workers:
          - narrateur-augmente
validators_required: true
```

### Équipe Mapping Cortex Leman

| Lead ID | Role | Workers disponibles |
|----------|-------|------------------|
| lead-orchestration | Stratégie globale | architecte-lemanique, ingenieur-de-flux |
| lead-marketing | Marketing & Branding | narrateur-augmente |
| lead-service-client | Service Client | oeil-de-cortex, architecte-lemanique |
| lead-securite | Sécurité & Conformité | gardien-des-normes, oeil-de-cortex |
| lead-production | Production & Infrastructure | ingenieur-de-flux, architecte-lemanique |

### Kill Switch Mapping

| Workflow | Kill Switch | Agent |
|----------|--------------|--------|
| cortex_leman_audit | gardien_des_normes | Le Gardien des Normes |
| generate_ui | gardien_des_normes | Le Gardien des Normes |
| mairie_report | gardien_des_normes | Le Gardien des Normes |

### Bonnes Pratiques

1. **Nommage cohérent**: Utiliser snake_case pour les noms de workflow
2. **Documentation complète**: Chaque workflow doit avoir README.md
3. **Checklists claires**: TILL_DONE.md avec cases à cocher
4. **Configuration détaillée**: config.yaml avec toutes les variables et équipes
5. **Validation intégrée**: validators_required: true pour les workflows critiques
6. **Kill switch explicite**: Définir quel agent peut arrêter le workflow

### Checklist de Création de Workflow

- [ ] Répertoire workflow créé
- [ ] PROMPT.md rédigé (instructions pour orchestrateur)
- [ ] TILL_DONE.md rédigé (checklist de completion)
- [ ] config.yaml créé (configuration détaillée)
- [ ] README.md créé (documentation utilisateur)
- [ ] Workflow ajouté à multi-team-config.yaml
- [ ] Équipes définies (leads + workers)
- [ ] Validators configurés (soft/hard si requis)
- [ ] Kill switch assigné (si applicable)
- [ ] Testé avec /workflow <name>

### Commandes Utiles

```bash
# Vérifier la configuration
cat ~/.hermes/agent-harness/multi-team-config.yaml

# Lister les workflows disponibles
ls ~/.hermes/agent-harness/workflows/

# Tester un workflow
/workflow <workflow_name> <variables>

# Voir les leads et workers disponibles
grep -A2 "leads:" ~/.hermes/agent-harness/multi-team-config.yaml
grep -A2 "workers:" ~/.hermes/agent-harness/multi-team-config.yaml
```

---

## PATTERNS D'EXÉCUTION PRATIQUES

### Fallback PDF → HTML

**Contexte**: En environnement contraint (externally-managed Python, pas sudo), les convertisseurs PDF (reportlab, wkhtmltopdf, pandoc, weasyprint) peuvent ne pas être disponibles.

**Pattern de fallback**:

1. **Tenter génération PDF** avec les outils disponibles
2. **Si échec**, générer HTML avec styling Cortex Leman
3. **Documenter la limitation** dans le livrable final
4. **Conserver les données JSON** pour conversion ultérieure

**Exemple de code de détection**:
```python
# Tentative PDF (reportlab, weasyprint, etc.)
try:
    import reportlab
    # Génération PDF
except ImportError:
    # Fallback HTML avec styling professionnel
    html_report = generate_html_with_cortex_styling(data)
```

**Template HTML Cortex Leman**:
```css
/* Palette Cortex Leman */
.header {
    background: linear-gradient(135deg, #0a1628 0%, #1a2a4a 100%);
}
.score-banner {
    background: linear-gradient(135deg, #d4af37 0%, #f4cf67 100%);
}
.section h2 {
    border-bottom: 3px solid #d4af37;
}
```

**Livraison du livrable**:
- HTML principal: `/tmp/<workflow_name>_report.html`
- Données brutes: `/tmp/<workflow_name>_data.json`
- Validation QA: `/tmp/qa_soft_validation.json`, `/tmp/qa_hard_validation.json`

### Structure de données multi-fichiers

Pour workflows complexes, créer plusieurs fichiers JSON intermédiaires:

```
/tmp/
├── <workflow>_context.json          # Context initial (ville, parameters)
├── <workflow>_research.json          # Recherche marché/data collection
├── <workflow>_analysis.json          # Analyse stratégique
├── <workflow>_report.html            # Livrable principal
├── qa_soft_validation.json           # Validation Soft
├── qa_hard_validation.json          # Validation Hard
└── livraison_finale.json            # Résumé livraison
```

### Exécution Workflow: mairie_report

**Pattern réel testé** (Annemasse, Executive, PDF):

1. **Validation variables**: ville=Annemasse, livrable=pdf, niveau=executive
2. **Collecte contexte** (lead-service-client): Données ville, population, contexte économique
3. **Recherche** (workers: gardien-des-normes, architecte-lemanique):
   - Opportunités IA (3 cas usage identifiés)
   - Analyse risques RGPD (score initial 0.45)
   - Comparaison ROI (3,757% Cortex Leman)
4. **Analyse stratégique** (architecte + gardien):
   - Score décision 0.65
   - Recommandation: GO RÉSERVÉ avec pilote 30j
   - Plan conformité 90j
5. **Génération livrable** (narrateur-augmente):
   - HTML professionnel avec styling Cortex Leman
   - 7 sections: Résumé Exécutif, KPIs, Conformité, Recommandations, ROI, Roadmap, Décision
6. **QA Soft**: Checklist 5 critères (0.95 quality score)
7. **QA Hard**: 6 tests techniques (tous PASS)
8. **Livraison finale**: Référence ANNEMASSE-IA-20260407-EXEC

**Temps d'exécution**: ~5-7 minutes (vs 6-8 semaines audit traditionnel)

### Pattern Validators

**Validator Soft** (rapide, non-blocking):
```python
soft_checklist = {
    "delivrable_recu": "Fichier généré et accessible",
    "coherence_avec_brief": "Variables respectées",
    "lisibilite_ton_structure": "Structure claire, ton professionnel",
    "todos_resolus": "Aucun placeholder détecté",
    "donnees_sensibles": "Données anonymisées"
}
```

**Validator Hard** (bloquant si fail):
```python
hard_checklist = {
    "soft_ok_confirme": "Soft validation OK",
    "tests_techniques": "HTML valid, lint OK",
    "conformite_rgpd_ai_act": "Score >= seuil",
    "tokens_api_secrets": "Aucun credential exposé",
    "delivrable_versionne": "Fichiers versionnés",
    "journal_decision": "Log enregistré"
}
```

**Sortie attendue**:
```json
{
  "validator": "QA Hard",
  "verdict_final": "OK",
  "tests_executes": {"html_validation": "PASS", ...},
  "actions_necessaires": []
}
```

### Livraison Finale

Structure du rapport de livraison:
```json
{
  "mission": "Nom du workflow",
  "ville": "Target",
  "date_livraison": "ISO timestamp",
  "statut": "COMPLETED",
  "resume_executif": { "score", "decision", "roi" },
  "livrables": { "paths": [...] },
  "recommandations_cles": { ... },
  "prochaines_etapes": [ ... ],
  "validation_results": { "soft", "hard", "quality_score" },
  "referencedossier": "UNIQUE-REF"
}
```
