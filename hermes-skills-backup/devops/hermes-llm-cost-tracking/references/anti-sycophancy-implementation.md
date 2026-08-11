# Anti-Sycophancy Protocol — Implementation Details

## Architecture

Deux couches indépendantes, chaînables:

### Couche 1: Rule-based (sans LLM)

Détecte 5 catégories de patterns problématiques:

| Catégorie | Patterns détectés | Severity |
|---|---|---|
| Langage promotionnel | révolutionnaire, game-changer, disrupt, inédit, toujours/jamais | 1-3 |
| Faux dilemmes | soit...soit, la seule option, si vous ne...alors | 3 |
| Conflit d'intérêts | notre produit, on lance, invest, sponsor | 3 |
| Chiffres non sourcés | nombres/percentages sans source citée | 3 |
| Prescription impérative | il faut, on doit, il est indispensable | 1 |

Le score de risque (0-100) est calculé par:
```
risk = min(30, promotional * 3)
     + min(25, dilemmas * 8)
     + min(30, coi * 10)
     + min(20, unsourced * 4)
     + min(15, unsourced_claims * 5)
```

### Couche 2: LLM Adversarial

Le prompt system instruit le LLM de:
1. Classer chaque claim comme FAIT / INTERPRÉTATION / RECOMMANDATION
2. Produire ≥2 objections fortes (severity 1-5)
3. Identifier les hypothèses non démontrées
4. Lister les données vérifiables manquantes
5. Estimer les conséquences si les claims sont faux
6. Vérifier les contraintes légales/réglementaires
7. Attribuer un niveau de confiance par claim
8. Donner un verdict: confirmé / partiellement / invalidé / données insuffisantes

Le prompt interdit explicitement la flatterie et autorise le refus de conclure.

## API endpoints utilisés

| Provider | Base URL | Modèle testé |
|---|---|---|
| Z.ai | `https://api.z.ai/api/coding/paas/v4` | glm-5.2 |
| OpenRouter | `https://openrouter.ai/api/v1` | openai/gpt-5.6-luna, anthropic/claude-* |

Le script détecte automatiquement quel provider utiliser selon le nom du modèle:
- Si `glm` dans le nom → Z.ai avec `GLM_API_KEY`
- Sinon → OpenRouter avec `OPENROUTER_API_KEY`

## Résultats de validation (27/07/2026)

### Texte avec erreurs volontaires (analyse Khan)
- **Couche 1:** Score 27/100 (CAUTION)
  - 3 patterns promotionnels détectés
  - 2 chiffres non sourcés ($3,000, $10K)
- **Couche 2 (GLM-5.2):** Verdict "données insuffisantes"
  - 3 objections (severity 4-5/5)
  - Conflit d'intérêts identifié
  - 3 contraintes dures (accréditation, RGPD, droit du travail)
  - Refus de conclure ✅

### Texte neutre (rapport comptable factuel)
- **Couche 1:** Score 0/100 (LOW)
- Zéro faux positif ✅

## Limites connues

1. **Regex francophone:** les patterns sont optimisés pour le français. Pour l'anglais, adapter `PROMOTIONAL_MARKERS` et `FALSE_DILEMMA_MARKERS`.
2. **Couche 2 coût:** ~$0.01-0.05 par analyse selon le modèle. La couche 1 seule suffit pour un premier filtre.
3. **Faux positifs possibles:** un texte qui cite légitimement des chiffres sans source (ex: données internes) peut être marqué. Le seuil CAUTION (15+) évite la plupart des faux positifs bénins.
4. **Le LLM peut toujours être sycophantique** malgré le prompt — c'est pourquoi la couche 1 rule-based existe en parallèle. Les deux couches sont complémentaires, pas redondantes.
