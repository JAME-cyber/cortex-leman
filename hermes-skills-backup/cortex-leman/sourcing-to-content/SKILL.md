---
name: sourcing-to-content
description: "Use when turning sourcing briefs into TikTok scripts."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [content, tiktok, import-export, derivative, repurposing]
    related_skills: [sourcing-agent]
---

# Sourcing-to-Content Pipeline

Transforme un sourcing brief en contenu TikTok/Shorts automatiquement. Chaque recherche de sourcing génère du matériel éditorial en sous-produit.

## Concept

Un sourcing brief contient:
- Des prix réels (intéressant pour l'audience)
- Des noms de fournisseurs (preuve d'expertise)
- Des risques réglementaires (valeur éducative)
- Des coûts landed réels (transparence = trust)

Chaque brief → 3 formats de contenu:

### Format 1: "Révélation prix" (60s)
```
Hook (3s): "Vous savez combien ça coûte VRAIMENT une montre en Chine ?"
Problem (10s): Prix retail trompeur
Reveal (20s): Prix sourcing réel + MOQ + supplier type
Margin reveal (15s): Calcul marge importeur
CTA (12s): "Le sourcing brief complet en bio"
```

### Format 2: "Erreur fatale" (45s)
```
Hook (3s): "L'erreur qui a coûté 5000€ à un importateur"
Story (25s): Cas réel (anonymisé) du brief
Lesson (12s): Ce qu'il fallait faire
CTA (5s): "Évitez ça → sourcing agent en bio"
```

### Format 3: "Top 5 fournisseurs" (60s)
```
Hook (3s): "Top 5 usines pour {product} en Chine"
Countdown (40s): 5→1 avec prix, MOQ, rating
Recommendation (12s): Notre pick + pourquoi
CTA (5s): "Brief complet → link en bio"
```

## Script Generation Rules

1. **Langage**: Français, ton direct, pas jargon
2. **Hook**: Toujours une question ou un chiffre choc
3. **Transparence**: Prix réels du brief, pas d'invention
4. **Pacing**: Cuts ≤2s, jamais statique (standard TikTok)
5. **Hashtags**: 5 max, nichés (#importexport #acheterenchine + 3 spécifiques produit)
6. **VO**: Edge TTS FR, voice masculine, pacing 1.0x
7. **Duration**: 45-60s optimal TikTok algorithm
8. **CTA**: Toujours pointer vers le sourcing agent (lead capture)

## Content Safety

- **Jamais** révéler les URLs/fournisseurs complets dans le contenu gratuit
- Donner le nom du top supplier = valeur premium (gating)
- Toujours ajouter: "Sources vérifiées, données de {date}"
- Anonymiser les cas clients si mentionnés

## Trigger

Ce pipeline se déclenche:
1. Après chaque sourcing brief complet
2. Via webhook `content-from-sourcing` 
3. Ou manuellement avec un brief en input

## Output

Pour chaque brief, générer:
- 3 scripts TikTok (format hook+problem+reveal+CTA)
- Hashtags optimisés
- Description TikTok
- Brief de production vidéo (pour notre pipeline vidéo Cortex Leman)
