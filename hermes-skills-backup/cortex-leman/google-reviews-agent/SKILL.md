---
name: google-reviews-agent
description: Use when replying to Google reviews for local shops.
---

# Google Reviews Agent

Service récurrent de gestion d'avis Google Business Profile pour commerces locaux FR-CH. L'agent Hermes répond aux avis automatiquement avec un ton humain et personnalisé, alerte le patron pour les avis négatifs, et produit un rapport mensuel.

## Architecture

```
Cron quotidien (6h)
  → Google My Business API: fetch nouveaux avis
  → LLM classifie (positif/négatif/moyen)
    → POSITIF: draft réponse personnalisée → file validation
    → MOYEN: draft réponse "invite à revenir" → file validation
    → NÉGATIF: alerte Telegram patron + ton suggéré → attente approbation
  → Webhook: publish réponse approuvée sur Google
  → Délai aléatoire 1-3h avant publication (humain)

Cron mensuel (1er du mois)
  → Synthèse: note moyenne, évolution, problèmes récurrents, NPS
  → Email/Telegram au patron
```

## Configuration client

Chaque client a un profil JSON:

```json
{
  "business_name": "Café du Marché",
  "owner_name": "Marc",
  "tone": "chaleureux, informel, tutoiement",
  "language": "fr",
  "signature_facts": ["terrasse ensoleillée", "cuisine maison", "spécialité: fondue"],
  "menu_items": ["fondue moitié-moitié", "filet de perche", "tarte aux pommes"],
  "staff_names": ["Sophie (serveuse)", "Luca (chef)"],
  "negative_alert_chat": "telegram:client:cafe_marche",
  "auto_publish_positive": true,
  "auto_publish_medium": true,
  "auto_publish_negative": false
}
```

## Règles de réponse

### Avis positif (4-5 étoiles)
- Remercier par nom si disponible
- Citer UN détail spécifique de l'avis (plat mentionné, ambiance, serveur)
- Refermante chaleureuse (reviennez bientôt)
- **Jamais de template** — chaque réponse est unique
- Ton calqué sur le profil client

### Avis moyen (3 étoiles)
- Remercier pour le retour
- Acknowledger le point négatif sans se justifier
- Proposer une solution ou invitation concrète ("venez nous en parler la prochaine fois")
- Pas de promesse vague

### Avis négatif (1-2 étoiles)
- **JAMAIS de réponse automatique**
- Alert Telegram au patron avec:
  - Texte de l'avis
  - Ton suggéré (empathique, pas défensif)
  - Draft de réponse proposé
  - Le patron approuve/modifie/rejette
- Si pas de réponse patron sous 48h → relance

## Anti-détection (paraître humain)

1. **Délai aléatoire** 1-3h entre avis et réponse
2. **Variation de longueur** — pas toutes les mêmes tailles
3. **Pas de réponses la nuit** (22h-7h)
4. **Phrases uniques** — le LLM reçoit l'historique des 20 dernières réponses pour éviter les répétitions
5. **Erreurs naturelles** — parfois une minuscule en début, un "..." (configurable, off par défaut)

## API Google My Business

### Authentification
```
Service Account JSON → Google Business Profile API v1
Scopes: https://www.googleapis.com/auth/business.manage
```

### Endpoints utilisés
```bash
# Lister les avis
GET https://mybusiness.googleapis.com/v4/accounts/{account}/locations/{location}/reviews

# Répondre à un avis
POST https://mybusiness.googleapis.com/v4/accounts/{account}/locations/{location}/reviews/{review}/reply
  Body: { "comment": "Merci beaucoup pour votre avis..." }
```

### Setup client (onboarding)
1. Client crée/claim sa fiche Google Business Profile
2. Client ajoute l'agent comme manager (email service account)
3. Récupérer `account_id` et `location_id` via API
4. Créer le profil JSON
5. Premier run: fetch tous les avis non répondus des 30 derniers jours

## Rapport mensuel

```markdown
# 📊 Rapport Avis Google — {business_name}
## {Mois Année}

### Note globale: 4.3⭐ (↑0.2 vs mois dernier)

### Avis reçus: 23
- Positifs: 18 (78%)
- Moyens: 3 (13%)
- Négatifs: 2 (9%)

### Réponses publiées: 21/23 (91%)
- Temps moyen de réponse: 2.5h

### Points positifs mentionnés:
1. Filet de perche (12 mentions)
2. Terrasse (8 mentions)
3. Accueil Sophie (5 mentions)

### Problèmes récurrents:
1. Attente le samedi soir (3 mentions)
2. Parking difficile (2 mentions)

### Action recommandée:
Communiquer sur le parking (post Google, site web).
```

## Cron Hermes

```yaml
# Cron quotidien — fetch et traitement des avis
schedule: "0 6 * * *"
prompt: |
  Récupère les nouveaux avis Google Business pour tous les clients actifs.
  Pour chaque avis:
  1. Classifie (positif/moyen/négatif)
  2. Génère une réponse selon le profil client
  3. Publie si auto-publié, sinon alerte
  Attends un délai aléatoire avant de publier.
skills:
  - google-reviews-agent
deliver: local  # silent, pas de spam Telegram

# Cron mensuel — rapport
schedule: "0 8 1 * *"
prompt: |
  Génère le rapport mensuel d'avis pour chaque client actif.
  Envoie le rapport par Telegram au client.
skills:
  - google-reviews-agent
deliver: origin
```

## Pricing

| Niveau | Prix | Inclus |
|---|---|---|
| **Solo** | 150€/mois | 1 commerce, auto positif/moyen, alerte négatif, rapport mensuel |
| **Multi** | 120€/mois/commerce | 3+ commerces, même features, dashboard groupé |
| **Agence** | 2000€/mois | Illimité pour fiduciaire qui revend à ses clients |

## Upsell chain

```
Avis Google (150€/mois)
  → SEO Local Audit (one-shot 2-4K CHF)
    → Audit PRISME RGPD-IA (one-shot 2-4K CHF)
      → Hermes Stack PME (build 15-50K CHF)
        → Maintenance récurrente (1.5-3K CHF/mois)
```

## Pitfalls

1. **Rate limit Google API** — max 200 req/min, batch les requêtes
2. **Répétition de ton** — feed les 20 dernières réponses au LLM
3. **Langues multiples FR-CH** — détecter langue de l'avis, répondre dans la même langue (fr, de, it)
4. **Avis supprimés** — gérer le cas où l'avis n'existe plus au moment de publier
5. **Multi-locations** — un client peut avoir plusieurs restaurants, gérer par location_id
6. **Privacy** — ne jamais citer le nom complet du client dans la réponse (prénom seulement)

## Onboarding checklist

- [ ] Client claim sa Google Business Profile
- [ ] Service account ajouté comme manager
- [ ] Test API: fetch avis existants OK
- [ ] Profil client JSON créé et validé
- [ ] Premier batch: réponses aux avis non répondus (validation manuelle)
- [ ] Activation cron quotidien
- [ ] Configuration alerte Telegram patron
- [ ] Premier rapport mensuel programmé
