# Skill: Agent Médiateur — Œil de Cortex
# Version: 1.0.0
# Type: PROGRAMMATIQUE PUR — AUCUN LLM
# Raison: Le Médiateur est le composant de sécurité le plus critique.
#          Un LLM probabiliste dans ce rôle est irresponsable en métier régulé.

## RÔLE
Appliquer les règles métier, détecter les conflits, geler les intentions.

## IMPLÉMENTATION
Voir: `core/mediator/mediator.py` + `core/mediator/rules/*.json`

## MOTEUR DE RÈGLES
22 règles JsonLogic déterministes:
- comptable: 7 règles (gel sur déduction >50K, conflit de sources, etc.)
- avocat: 4 règles (secret professionnel, data residency)
- sante: 3 règles (données patient, hébergement HDS)
- banque: 3 règles (secret bancaire, infrastructure CH)
- rh: 3 règles (anti-discrimination, décision automatique)
- startup: 2 règles (RGPD, DPIA)

## PAS DE SKILL LLM — RAISONS
1. Non-déterminisme: un LLM peut ne pas geler une intention qu'il devrait geler
2. Latence: le Médiateur intercepte CHAQUE résultat d'agent
3. Auditabilité: JsonLogic est reproductible, un LLM ne l'est pas
4. Certification: aucun auditeur LSTI/SGS/AFNOR n'acceptera un gel probabiliste

## GEL PAR DÉFAUT
Si vertical sensible (comptable, avocat, banque, santé) ET montant ≥ 10K
ET aucune règle explicite ne couvre le cas → gel préventif par précaution.
