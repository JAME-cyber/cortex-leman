# Multi-Team Orchestrator Skill

## Installation
1. Copier `~/.hermes/agent-harness/` dans context_files (déjà fait).
2. Placer ce skill dans `~/.hermes/skills/agent-harness/multi-team-orchestrator/`.
3. Ajouter la commande `/workflow` dans Hermes (CLI ou messaging).
4. Scripts utilisés :
   - `~/.hermes/agent-harness/scripts/run-workflow.sh`
   - `~/.hermes/agent-harness/scripts/generate_run_log.py`

## Usage
```
/workflow generate_ui brand=Aegis product="Agent Stream" count=3 tree=agents-app
```

## Fonctionnement
- Le skill lit `multi-team-config.yaml` pour construire les équipes.
- Il met à jour les fichiers TILL_DONE.
- Il délègue aux leads/workers via instructions textuelles.
- Il déclenche validators soft puis hard.
- Les run logs sont écrits dans `~/.hermes/agent-harness/logs/`.
