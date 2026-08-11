---
name: anti-ia-humanizer
version: 1.0.0
description: Pipeline anti-IA en 7 étapes pour humaniser les textes générés par LLM. Inspiré du thread Paul Young (@PaulYoungX). Appliquer avant tout livrable client.
trigger: Quand un texte généré par IA est destiné à un client, un rapport, un post public, ou tout support où la crédibilité humaine compte.
---

# Anti-IA Humanizer — Pipeline Cortex Leman

## Contexte
Les textes LLM ont des signatures détectables : structures symétriques, transitions prévisibles, ton lisse, conclusions trop rangées. Pour un cabinet d'audit RGPD-IA, un livrable qui "sent l'IA" détruit la crédibilité.

## Pipeline d'exécution

Appliquer les prompts **dans l'ordre**. Chaque étape affine le résultat de la précédente.

### Étape 1 — Réécriture voix humaine
```
Agis comme un éditeur spécialisé dans la chasse aux textes trop lisses, trop parfaits, trop artificiels.

Réécris ce texte comme s'il avait été écrit par quelqu'un qui a réellement vécu ce dont il parle.

Je veux que ça sonne vrai, naturel et authentique, pas comme un texte optimisé par une machine.
```

### Étape 2 — Correcteur de pensée humaine
```
Ce n'est pas une correction grammaticale. C'est une correction de la façon de penser.

Réécris ce texte pour que les idées s'enchaînent comme elles le feraient dans un vrai esprit humain :
• Parfois de façon directe
• Parfois en prenant son temps
• Parfois avec des phrases courtes
• Parfois avec un rythme qui change
• Sans chercher à être parfaitement poli ou calibré

Casse tout ce qui trahit une écriture générée par l'IA :
• Des phrases toutes de la même longueur
• Des structures trop symétriques
• Des transitions prévisibles
• Un ton excessivement maîtrisé
• Des conclusions trop bien rangées

Garde le message de fond, mais fais en sorte qu'on ait l'impression qu'il vient d'une personne, pas d'un modèle.
```

### Étape 3 — Détecteur de schémas IA
```
Agis comme un éditeur obsédé par les indices qui révèlent un texte généré par IA.

Analyse ce texte et élimine tout ce qui le trahit.

Traque et corrige :
• Les formulations trop parfaites
• Les rythmes répétitifs
• Les structures prévisibles
• Le vocabulaire générique
• Le ton trop neutre
• Les transitions artificielles
• Les explications qui ressemblent à un manuel
• Les conclusions trop impeccables

Puis réécris-le avec :
• Plus de variété
• Plus d'intention
• Plus de personnalité
• Plus de naturel
• Plus de spontanéité

Je ne veux pas qu'il paraisse « humanisé ». Je veux qu'il paraisse humain dès la première ligne.
```

### Étape 4 — Test de crédibilité
```
Agis comme un lecteur sceptique.

Ton rôle est de repérer toutes les phrases qui paraissent artificielles, trop travaillées ou trop répétées.

Passe ce texte en revue phrase par phrase et réécris tout ce qui ne donne pas l'impression d'avoir été écrit par une vraie personne.

Je veux que le résultat soit :
• Plus crédible
• Moins lisse et artificiel
• Plus direct
• Plus personnel
• Moins conçu pour plaire à tout le monde

Règles :
• Si une phrase semble trop belle ou trop parfaite, simplifie-la
• Si une idée paraît générique, rends-la plus concrète
• Si le ton rappelle trop une IA, modifie-le
• S'il manque un point de vue, affirme une position claire
• S'il y a trop d'explications, coupe dans le superflu
```

### Étape 5 — Bâtisseur de voix unique
```
Agis comme un éditeur spécialisé dans la voix et le style personnel.

Réécris ce texte pour qu'il ne donne plus l'impression d'avoir été écrit par un observateur neutre qui cherche à plaire à tout le monde.

Je veux qu'il ait une voix plus identifiable et plus personnelle.

Fais en sorte que le texte ait :
• Une opinion claire
• Un véritable point de vue
• Des formulations avec plus de caractère
• Une part de contradiction naturelle si cela a du sens
• Moins de ton "contenu parfait"
• Davantage la sensation qu'une vraie personne se trouve derrière les mots

Règles :
• N'en fais pas trop
• Ne le rends pas agressif sans raison
• Évite les phrases de motivation creuses
• N'ajoute pas une personnalité artificielle
• Préserve l'essence du message
```

### Étape 6 — Nettoyeur de clichés IA
```
Agis comme un éditeur spécialisé dans l'élimination des formulations typiques de ChatGPT, Claude et des autres modèles d'IA.

Analyse ce texte et supprime toutes les tournures qui ressemblent à :
• « Dans le monde d'aujourd'hui... »
• « Il est important de souligner que... »
• « Non seulement..., mais aussi... »
• « En conclusion... »
• « La clé est de... »
• « Transformez votre... »
• « Améliorez votre... »
• « Découvrez comment... »

Puis réécris le texte avec un langage plus humain, plus simple et plus direct.

Je veux qu'on ait l'impression qu'il a été écrit rapidement, avec des idées claires et une intention précise.

Règles :
• Conserve le message d'origine
• Raccourcis le texte si nécessaire
• Remplace les mots compliqués par des mots courants
• Supprime les explications évidentes ou inutiles
• Ajoute une touche plus personnelle si cela améliore le texte
```

### Étape 7 — Test anti-IA ultime (validation)
```
Agis comme un détecteur humain de textes artificiels.

Lis ce texte et attribue-lui une note de 1 à 10 selon le degré auquel il semble avoir été écrit par une IA.

Ensuite, indique-moi :
• Quelles formulations le trahissent
• Quels schémas se répètent
• Quels passages paraissent trop lisses ou trop travaillés
• Quels mots tu remplacerais
• Quels passages tu supprimerais
• Où il manque une véritable voix humaine

Puis réécris le texte afin de réduire au maximum l'impression qu'il a été généré par une IA.

Le résultat doit être :
• Naturel
• Clair
• Légèrement imparfait
• Porté par un rythme humain
• Doté d'un véritable point de vue
• Débarrassé des formulations toutes faites

À la fin, donne-moi :
• La note initiale
• La note après réécriture
• Les principaux changements effectués
```

## Mode d'emploi par projet

### Cortex Leman — Rapports d'audit RGPD-IA
- Appliquer étapes 1-6 sur le brouillon
- Étape 7 comme validation finale
- **Objectif** : Note finale ≤ 3/10 sur l'échelle anti-IA
- **Spécifique** : Adapter la voix au profil "consultant senior FR-CH" — professionnel mais pas robotique

### Cortex Leman — Briefs hebdo CNIL/EDPB
- Étapes 4, 6, 7 suffisent (format court, l'essentiel est la crédibilité)
- **Objectif** : Note finale ≤ 2/10

### SocialPulse — Contenu B2B
- Étapes 1, 5, 6 pour les posts réseaux sociaux
- Étape 7 pour les articles longs
- **Objectif** : Voix identifiable par client, pas générique

### HELEN — Outputs workflow
- Étapes 4 et 6 en post-processing automatique
- Seulement pour les outputs visibles par l'utilisateur final

## Dictionnaire des clichés IA à bannir (FR)

| Cliché IA | Remplacement |
|-----------|-------------|
| Dans le monde d'aujourd'hui | [Supprimer ou contextualiser] |
| Il est important de souligner que | Dire directement ce qui est important |
| Non seulement... mais aussi | Structurer autrement |
| En conclusion | [Supprimer — le contenu parle] |
| La clé est de | L'essentiel : / Le point critique : |
| Transformez votre | [Verbe concret + objet] |
| Découvrez comment | [Dire ce que c'est] |
| En effet | [Supprimer ou reformuler] |
| Par ailleurs | [Transition naturelle ou supprimer] |
| Il convient de noter que | [Supprimer — si c'est important, le dire directement] |
| De plus | [Enchaînement logique naturel] |

## Support files

| File | Usage |
|------|-------|
| `references/paul-young-7-prompts.md` | Source intégrale des 7 prompts (@PaulYoungX, juin 2026) |
| `templates/n8n-anti-ia-workflow.json` | Workflow n8n standalone (webhook `/cortex-anti-ia`) |

## Intégration n8n

### Workflow standalone
Fichier : `cortex-leman-v5/n8n-workflows/anti-ia-humanizer.json`
Webhook : `POST http://localhost:5678/webhook/cortex-anti-ia`
Payload : `{ text, source, context, target_score }`
Réponse : `{ text, anti_ia_score, anti_ia_flags, anti_ia_patterns, passed }`

### Hook rapport d'audit
Le workflow `audit-report-generator.json` intègre un nœud Anti-IA entre Claude et la génération HTML. Flux : `Claude → Anti-IA Humanizer → Parse → HTML → PDF → Email`

### Client Python
`core/integrations/n8n/client.py` — méthode `humanize_text()` :
```python
result = await n8n_client.humanize_text(text=..., source="claude_audit", context="audit_rgpd_ia", target_score=3)
```
Comportement fail-open : si n8n est down, retourne le texte original sans blocage.

### Import dans n8n
```bash
curl -X POST http://localhost:5678/api/v1/workflows \
  -H "Content-Type: application/json" \
  -d @n8n-workflows/anti-ia-humanizer.json
```

## Pitfalls
- **Sur-humanisation** : Trop forcer le style = texte artificiellement décontracté, aussi repérable. L'étape 5 ("n'en fais pas trop") est cruciale.
- **Perte de précision** : Dans les rapports d'audit, l'exactitude juridique est non-négociable. Ne jamais sacrifier la justesse pour le style.
- **Incohérence** : Appliquer le pipeline morceau par morceau crée des ruptures de style. Toujours appliquer sur le document complet.
- **Audit RGPD** : Les termes juridiques (responsable de traitement, sous-traitant, DPO...) restent inchangés — ce n'est pas du jargon IA, c'est du vocabulaire métier.
