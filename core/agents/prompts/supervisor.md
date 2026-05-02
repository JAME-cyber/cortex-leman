# Skill: Agent Superviseur — Observateur Continu
# Version: 1.0.0
# Type: PROGRAMMATIQUE PUR — AUCUN LLM
# Raison: Le health board est du calcul numérique, pas de l'interprétation.

## RÔLE
Observateur continu du graphe. Health board par intention. Alertes de dégradation.

## IMPLÉMENTATION
Voir: `core/agents/supervisor_agent.py`

## PAS DE SKILL LLM — RAISONS
1. Le health board est des calculs de confiance et des compteurs
2. La détection de staleness est une comparaison de timestamps
3. Un LLM n'ajouterait aucune valeur ici
