# Skill: Agent Action — Exécuteur Fidèle
# Version: 1.0.0
# Type: PROGRAMMATIQUE PUR — AUCUN LLM
# Raison: L'exécution d'actions (paiements, écritures, workflows) doit être
#          100% déterministe. Un LLM probabiliste dans ce rôle serait dangereux.

## RÔLE
Exécuter de manière transactionnelle les actions validées.

## IMPLÉMENTATION
Voir: `core/agents/action_agent.py`

## GARDE-FOUS (dans le code, pas dans un prompt)
- Vérification du gel avant exécution (intention.status != "frozen")
- Verrou distribué sur chaque intention
- Saga avec compensation pour chaque action
- Circuit breaker contre les échecs répétés

## PAS DE SKILL LLM — RAISONS
1. Un LLM peut "oublier" une étape de compensation
2. Un LLM peut exécuter une action gelée
3. Un LLM ajoute 500ms-5s de latence par action
4. Aucun auditeur ne certifiera un exécuteur probabiliste
