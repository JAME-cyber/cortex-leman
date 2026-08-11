# Evidence Ledger — Cortex Leman

> MVP v1.0 — 7 août 2026
> Basé sur: pattern Comp CRM "Evidence Ledger" + contre-analyse GPT-5.6 du tweet @antpalkin "Failure Ledger"

## Principe

> *"Transformer les expérimentations et diagnostics en mémoire opérationnelle, afin que chaque nouvelle décision bénéficie des preuves accumulées — y compris des résultats négatifs et inconclusifs."*

**Pas un failure ledger.** Un experiment ledger. On enregistre succès, échecs ET résultats inconclusifs. Le but n'est pas de lister ce qui rate, mais de **changer la décision suivante**.

## Règle d'or

> Si personne ne consulte le ledger avant d'agir, ce n'est pas une mémoire — c'est un cimetière documentaire.

**Consultation obligatoire** avant toute expérience significative (nouvelle campagne, nouveau signal, nouveau diagnostic, nouveau pitch).

---

## Schéma universel

Une entrée = une expérience ou décision testée.

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `id` | auto | ✅ | UUID séquentiel |
| `date` | date | ✅ | Date de l'expérience |
| `domaine` | enum | ✅ | `kronos` \| `sales` \| `diagnostic` \| `prisme` |
| `hypothese` | text | ✅ | Ce qu'on croyait vrai **avant** le test |
| `contexte` | object | ✅ | Variables spécifiques au domaine (voir ci-dessous) |
| `action` | text | ✅ | Ce qui a été réellement exécuté |
| `critere_succes` | text | ✅ | Défini **ex ante**. Pas de rétro-storytelling. |
| `resultat` | text | ✅ | Chiffres et faits bruts |
| `statut` | enum | ✅ | `valide` \| `invalide` \| `inconclusif` \| `abandonne` |
| `cause_probable` | text | ✅ | En distinguant: observation factuelle / interprétation |
| `confiance` | enum | ✅ | `faible` \| `moyenne` \| `forte` |
| `source_diagnostic` | enum | ✅ | `humain` \| `machine` \| `mixte` |
| `conditions_reessai` | text | ✅ | "Retester uniquement si X, Y ou Z change" |
| `date_expiration` | date | ✅ | Date de réévaluation (défaut: +6 mois) |
| `tags` | array | ❌ | Mots-clés libres pour recherche |
| `liens` | array | ❌ | Code, campagne CRM, rapport, conversation |
| `auteur` | text | ✅ | Qui a enregistré l'entrée |

---

## Contextes par domaine

### `kronos` (crypto/signaux)

```
contexte: {
  actif: "BTC/USDT",
  timeframe: "4h",
  regime_marche: "trend_bull" | "range" | "trend_bear" | "high_vol",
  periode_backtest: "2025-01-01 → 2025-06-30",
  in_sample: "2025-01-01 → 2025-04-30",
  out_of_sample: "2025-05-01 → 2025-06-30",
  couts_inclus: true,
  slippage_estime: "0.05%",
  version_donnees: "v2.3"
}
```

### `sales`

```
contexte: {
  segment: "fiduciaire" | "cabinet_juridique" | "pmes_services" | "ecommerce",
  taille: "1-5" | "6-20" | "21-50" | "50+",
  canal: "linkedin" | "cold_email" | "referral" | "evenement",
  pitch: "diagnostic_prisme" | "pilote_ia" | "audit_compliance",
  prix_propose: "CHF/mois",
  phase_funnel: "awareness" | "interest" | "consideration" | "proposal" | "closed",
  raison_declaree: "Ce que le prospect a dit",
  cause_supposee: "Ce qu'on pense vraiment"
}
```

### `diagnostic`

```
contexte: {
  secteur_client: "fiduciaire" | "juridique" | "immobilier" | "retail" | "sante",
  taille_client: "1-5" | "6-20" | "21-50",
  maturite_ia: "aucune" | "basique" | "intermediaire",
  systeme_existant: "odoo" | "salesforce" | "excel" | "autre",
  axe_prisme: "pilotage" | "recherche" | "ingenierie" | "scoring" | "multicanal" | "evaluation",
  objectif_mesure: "ex: réduire temps préparation dossiers de 40%"
}
```

### `prisme` (contenu marketing)

```
contexte: {
  format: "linkedin_post" | "thread" | "video" | "carousel" | "newsletter",
  angle: "ex: case_study" | "contrarian" | "how_to" | "data_insight",
  cible: "fiduciaires" | "pmes_romandes" | "integrateurs_odoo",
  canal_pub: "organique" | "sponsore",
  timing: "matin" | "midi" | "soir",
  jour: "lundi" | "mardi" | ...,
  metriques: {
    impressions: N,
    engagements: N,
    clics: N,
    conversions: N
  }
}
```

---

## Workflow

### Enregistrement (2 min après chaque expérience)

1. Créer une entrée avec tous les champs obligatoires
2. Définir le critère de succès **avant** de regarder le résultat si pas déjà fait
3. Séparer: fait observé vs interprétation vs confiance

### Consultation (avant nouvelle initiative)

1. Rechercher par `domaine` + `tags` + `contexte` pertinent
2. Vérifier les entrées non expirées
3. Si une hypothèse similaire a échoué → lire `conditions_reessai`
4. Ajuster l'approche en conséquence

### Revue hebdomadaire (20 min)

- Nouvelles entrées de la semaine
- Patterns émergents (même échec répété)
- Entrées à expirer / réouvrir
- Décisions modifiées grâce au ledger

### Synthèse mensuelle

- Échecs répétés (même cause, même contexte)
- Hypothèses à retester (conditions de réessai réunies)
- Conclusions devenues obsolètes
- Décisions évitées grâce au ledger
- Taux de consultation réelle (audit d'usage)

---

## Pièges à éviter (GPT-5.6)

1. **Jamais transformer 1 cas isolé en règle** — noter la taille d'échantillon
2. **Pas que des échecs** — succès et inconclusifs aussi
3. **Corrélation ≠ cause** — séparer fait/interprétation/confiance
4. **Date d'expiration obligatoire** — un échec 2025 peut réussir en 2026
5. **"Déjà essayé" = phrase interdite** sans vérifier `conditions_reessai`
6. **Le LLM ne décide jamais seul qu'une cause est établie** — `source_diagnostic` toujours tracé
7. **Pas de données client sensibles en clair** — pseudonymiser (nLPD)

---

## Outil recommandé

**Phase 1 (MVP, maintenant):** Airtable ou Notion
- Une table, 16 colonnes, formulaires de saisie
- Recherche par tags et contexte
- Pas de vector DB, pas d'agents

**Phase 2 (après 50+ entrées):** Migration vers PostgreSQL
- Si le volume justifie
- Si la consultation manuelle devient un goulot

**Phase 3 (après 200+ entrées + preuve d'usage):** Recherche sémantique
- Embeddings pour "cet angle ressemble-t-il à un échec passé?"
- Agent qui consulte automatiquement avant action

---

## Métriques de succès du ledger

Mesurer sur 6-8 semaines:

| Métrique | Comment mesurer |
|---|---|
| Expériences dupliquées évitées | Compter les consultations qui ont modifié l'approche |
| Décisions modifiées après consultation | Auto-déclaré dans l'entrée de la nouvelle expérience |
| Temps gagné | Estimé (heures évitées sur recherches/redondances) |
| Objections récurrentes détectées | Patterns dans `cause_probable` du domaine sales |
| Hypothèses réouvertes avec succès | Entrées où `conditions_reessai` furent réunies → `valide` |
| Taux de consultation réelle | % d'expériences significatives précédées d'une consultation |

**Go/no-go Phase 2:** Si après 8 semaines, <30% des expériences sont précédées d'une consultation → le format ne marche pas, itérer ou abandonner.
