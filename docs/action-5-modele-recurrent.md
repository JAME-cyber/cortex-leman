# ACTION 5: Modèle Récurrent Conformité — Conception Complète

## Pourquoi le récurrent est notre arme secrète

ZénithIA vend du **projet ponctuel** (5K-50K€). S'ils arrêtent de prospecter, le CA chute.
Cortex Leman vend de la **conformité continue**. L'abonnement = revenus prévisibles.

### Le problème du projet ponctuel
```
Mois 1: Projet A (15K€) ████████████ 
Mois 2: Rien            ░░░░░░░░░░░░
Mois 3: Projet B (8K€)  ██████
Mois 4: Rien            ░░░░░░░░░░░░
Mois 5: Projet C (20K€) ████████████████
→ CA irrégulier, stress de trésorerie, dépendance au pipeline
```

### Notre modèle récurrent
```
Mois 1: Audit A (3K€) + 3 abonnés (1.5K€/mois) = 4.5K€
Mois 2: Audit B (3K€) + 5 abonnés (2.5K€/mois) = 5.5K€
Mois 3: Audit C (5K€) + 8 abonnés (4K€/mois)   = 9K€
Mois 4: 0 audit     + 12 abonnés (6K€/mois)     = 6K€  ← TRÉSORERIE STABLE
Mois 5: Audit D (3K€) + 15 abonnés (7.5K€/mois) = 10.5K€
→ MRR croissant, revenus prévisibles, audit = acquisition client, pas revenu principal
```

---

## Structure des 3 offres

### Tier 1: DIAGNOSTIC (gratuit → acquisition)

**Objectif:** Convertir en audit payant. Pas de revenu direct.

- Analyse automatique OWASP GenAI (questions ciblées)
- Score de risque: FAIBLE / MOYEN / ÉLEVÉ / CRITIQUE
- Top 3 des gaps identifiés
- Rapport PDF généré automatiquement (workflow n8n Action 1)
- **Durée:** 15 min (appel ou formulaire)
- **Livré en:** < 24h (automatisé)

**Stack:** Landing page formulaire → n8n → Claude → PDF → Email

---

### Tier 2: AUDIT COMPLET (one-shot — acquisition client)

**Objectif:** Premier revenu + qualifier pour l'abonnement.

| Formule | Prix | Taille entreprise | Délai |
|---------|------|-------------------|-------|
| **Startup** | CHF 2,500 | 5-15 employés | 2 semaines |
| **Growth** ⭐ | CHF 4,000 | 16-35 employés | 3 semaines |
| **Enterprise** | CHF 6,500 | 36-50+ employés | 3-4 semaines |

**Livré:**
- Rapport complet OWASP Top 10 + ASVS v4.0
- Rapport OWASP GenAI (9 phases Agentic AI + 12 menaces Data Security)
- Mapping AI Act (Articles 9-16)
- Mapping LPerD (si Suisse)
- AIPD/DPIA draft (auto-généré via `audit_generator.py`)
- Plan d'action priorisé avec timeline
- **Certificate of Compliance** (valable 12 mois)

**Up-sell naturel:** "Votre certificat expire dans 10 mois. Souscrivez au plan Conformité pour rester conforme en continu."

---

### Tier 3: CONFORMITÉ CONTINUE (récurrent — revenue engine)

**Objectif:** MRR, lock-in client, LTV maximale.

| Plan | Prix/mois | Ce qui est inclus |
|------|-----------|-------------------|
| **Sentinelle** | CHF 500 | Monitoring continu, alertes, rapport mensuel |
| **Garde** ⭐ | CHF 900 | Sentinelle + re-audit trimestriel + support DPO |
| **Forteresse** | CHF 1,500 | Garde + consulting stratégique + hotline priorité |

#### Détail des plans

**Sentinelle (CHF 500/mois)**
- Monitoring OWASP GenAI en continu (nouvelles menaces)
- Alerte si nouveau CVE sur votre stack IA
- Rapport de conformité mensuel auto-généré
- Mise à jour du certificat de conformité (valide tant que abonné)
- Dashboard de conformité (read-only)
- Email: rapport mensuel + alertes temps réel

**Garde (CHF 900/mois)** — *Le sweet spot*
- Tout Sentinelle +
- Re-audit trimestriel complet (OWASP Top 10 + GenAI)
- Mise à jour AIPD/DPIA automatique
- Support DPO (questions illimitées, réponse < 24h)
- Revue des nouveaux outils IA avant déploiement
- Veille réglementaire FR-CH personnalisée
- Mise à jour du plan d'action chaque trimestre

**Forteresse (CHF 1,500/mois)**
- Tout Garde +
- Consulting stratégique IA (2h/mois)
- Hotline priorité (réponse < 4h)
- Accès anticipation réglementaire (AI Act Phase 2, NIS2)
- Audit ad-hoc pour tout nouvel outil IA déployé
- Co-pilotage DPO (on devient votre compliance partner)
- Rapport exécutif trimestriel pour le board

---

## Unitaire economics

### Hypothèses conservatrices (12 mois)

| Métrique | Mois 1-3 | Mois 4-6 | Mois 7-9 | Mois 10-12 |
|----------|----------|----------|----------|------------|
| Nouveaux audits/mois | 2 | 3 | 4 | 5 |
| Prix moyen audit | CHF 3,500 | CHF 3,800 | CHF 4,000 | CHF 4,200 |
| Taux conversion → abonnement | 40% | 50% | 55% | 60% |
| Abonnés cumulés (fin période) | 3 | 8 | 16 | 27 |
| Prix moyen abonnement | CHF 800 | CHF 850 | CHF 900 | CHF 950 |
| **Revenue audit (trim.)** | CHF 21K | CHF 34K | CHF 48K | CHF 63K |
| **MRR récurrent (fin trim.)** | CHF 2.4K | CHF 6.8K | CHF 14.4K | CHF 25.6K |
| **ARR récurrent (fin trim.)** | CHF 29K | CHF 82K | CHF 173K | CHF 308K |

### Break-even

- **Coûts fixes/mois:** ~CHF 3,000 (serveur CH, n8n, outils, LLM API)
- **Break-even MRR:** ~4 abonnés Garde (CHF 3,600/mois)
- **Break-even timeline:** Mois 3-4 avec hypothèses conservatrices

---

## Implémentation technique

### 1. Stripe Checkout (paiement récurrent)

```yaml
# config.yaml addition
stripe:
  products:
    sentinelle:
      price_id: price_sentinelle_chf500
      amount: 50000  # cents CHF
      interval: month
    garde:
      price_id: price_garde_chf900
      amount: 90000
      interval: month
    forteresse:
      price_id: price_forteresse_chf1500
      amount: 150000
      interval: month
  webhook_url: https://api.cortexleman.ch/api/v1/billing/webhook
```

### 2. n8n Workflow: Monitoring Conformité Continu

```json
{
  "name": "Cortex Leman — Monitoring Conformité Continu",
  "trigger": "Tous les 1er du mois",
  "pipeline": [
    "Récupérer liste abonnés actifs (Stripe → API)",
    "Pour chaque abonné:",
    "  → Scanner stack IA (nouvelles vulnérabilités OWASP)",
    "  → Vérifier nouvelles réglementations FR-CH",
    "  → Générer rapport mensuel personnalisé",
    "  → Mettre à jour certificat conformité",
    "  → Envoyer rapport par email (+ dashboard)",
    "  → Si alerte critique: notification immédiate Slack + email"
  ]
}
```

### 3. Dashboard client (frontend)

Route: `cortexleman.ch/dashboard/{client_id}`

- Score de conformité en temps réel
- Historique des audits
- Alertes actives
- Prochaines échéances réglementaires
- Bouton "Demander un re-audit" (plan Garde+)
- Téléchargement certificat PDF

### 4. API endpoints à ajouter

```
POST   /api/v1/billing/checkout     → Créer session Stripe
POST   /api/v1/billing/webhook      → Webhook Stripe
GET    /api/v1/billing/subscription  → Statut abonnement client
POST   /api/v1/monitoring/scan       → Déclencher scan conformité
GET    /api/v1/monitoring/report     → Dernier rapport mensuel
GET    /api/v1/certificate/{id}      → Certificat de conformité
POST   /api/v1/certificate/renew     → Renouveler certificat
```

---

## Argumentaire de vente: pourquoi le récurrent

### Objection: "Je veux juste un audit ponctuel"

**Réponse:**
> "L'audit ponctuel, c'est comme un contrôle technique auto. Ça prouve que vous étiez 
> conforme le jour J. Mais l'AI Act exige une conformité **continue** — pas un snapshot. 
> En 12 mois, votre stack IA change, de nouvelles vulnérabilités OWASP apparaissent, 
> la réglementation évolue. Le plan Sentinelle à CHF 500/mois, c'est une assurance: 
> vous dormez tranquille, on surveille pour vous."

### Objection: "C'est trop cher mensuellement"

**Réponse:**
> "Une amende AI Act, c'est jusqu'à 6% de votre CA. Pour une PME de CHF 1M, c'est 
> CHF 60,000. Notre plan Garde à CHF 900/mois = CHF 10,800/an. Le ROI est de 5.5x 
> sur la première amende évitée. Et c'est sans compter la perte de réputation, les 
> poursuites clients, et le temps du DPO."

### Objection: "Mon DPO peut le faire en interne"

**Réponse:**
> "Votre DPO connaît le RGPD. Mais OWASP GenAI? Les 9 phases Agentic AI? Les 12 menaces 
> Data Security? Le mapping AI Act Articles 9-16? C'est notre spécialité exclusive. 
> On complète votre DPO, on ne le remplace pas."

---

## Checklist mise en œuvre

- [ ] Configurer Stripe (products + pricing + webhook)
- [ ] Créer le workflow n8n monitoring mensuel
- [ ] Ajouter les endpoints API billing/monitoring
- [ ] Builder le dashboard client (page frontend)
- [ ] Créer le template certificat de conformité PDF
- [ ] Rédiger les email templates: welcome, rapport mensuel, alerte critique, renewal
- [ ] Tester le pipeline complet (audit → conversion → abonnement → premier rapport)
- [ ] Ajouter la section pricing récurrent sur la landing page
- [ ] Mettre à jour la fiche produit avec les 3 plans récurrents
