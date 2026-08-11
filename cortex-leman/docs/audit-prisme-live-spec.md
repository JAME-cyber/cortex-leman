# AUDIT PRISME LIVE — Spec produit

> Version 1.0 — 6 août 2026
> Concept : le diagnostic n'est pas un PDF, c'est une démonstration agentique en temps réel.

---

## LE PROBLÈME

Les concurrents (@coreyganim, @mathieuhq) vendent des diagnostics statiques :
- PDF de 999$ que personne ne lit en entier
- "Assessment" = checklist générique appliquée à tous les clients
- Le prospect paie pour qu'on lui vende la suite

Le prospect ressort avec un document et zéro sensation de ce que l'IA *fait* réellement.

## LA DIFFÉRENCE PRISME

**Le Diagnostic PRISME Live est un scout agentique qui tourne sous les yeux du prospect.**

Le prospect ne reçoit pas un rapport. Il regarde les agents scanner son business, découvrir ses problèmes, et formuler des recommandations — en direct. Il *voit* PRISME avant de l'acheter.

C'est le principe du restaurant à cuisine ouverte : tu vois comment c'est fait avant de commander.

---

## DÉROULÉ (45 min)

### Phase 1 — Intake (10 min, en visio)
Le prospect donne 3 choses :
1. **Son URL** (site web existant)
2. **Un processus manuel qu'il exécute régulièrement** (devis, onboarding client, newsletter, suivi de stocks, etc.)
3. **Ses outils actuels** (Excel, Mailchimp, Zendesk, etc.)

### Phase 2 — Scan live (20 min, prospect regarde)

Le prospect regarde les agents travailler sur un écran partagé :

```
┌─────────────────────────────────────────────────────┐
│  🟢 SCOUT-1   Scan site web                         │
│  → SEO local, vitesse mobile, structure, contenu    │
│  → 47 problèmes détectés                            │
│                                                     │
│  🟢 SCOUT-2   Scan processus manuel                 │
│  → "Combien de temps pour générer un devis ?"       │
│  → Process: 8 étapes, 3 goulots identifiés          │
│  → Automatisable à 60%                              │
│                                                     │
│  🟢 SCOUT-3   Diagnostic conformité             │
│  → RGPD: 3 manquements détectés                     │
│  → Pas de mentions légales IA, pas de DPO           │
│  → Risque: AI Act si automatisation client          │
│                                                     │
│  🔵 RESEARCH  Compilation en cours...               │
│  → Cross-référence avec 200+ case studies           │
└─────────────────────────────────────────────────────┘
```

**L'effet** : le prospect voit 3 agents tourner simultanément, en parallèle. C'est viscéral. Personne d'autre ne fait ça.

### Phase 3 — Rapport généré (10 min, livraison immédiate)

Le rapport arrive en direct, pendant la visio. Pas de "je vous l'envoie sous 48h". Contenu :

1. **Score PRISME** (0-100) sur 6 axes :
   - Présence digitale
   - Efficacité opérationnelle
   - Maturité IA
   - Conformité (RGPD/AI Act)
   - Potentiel d'automatisation
   - ROI estimé

2. **Top 3 opportunités** (classées par impact × facilité) :
   - Chacune avec : heures économisées/mois, coût d'implémentation, délai

3. **Cartographie des risques conformité** :
   - Ce qui est en infraction aujourd'hui
   - Ce qui le sera si ils automatisent sans garde-fous

4. **Démo PRISME** : une mini-boucle exécutée live (ex: un tweet généré à partir de leur site, un devis-type pré-rempli)

### Phase 4 — Recommandation (5 min)
"L'audit montre 3 opportunités à fort impact. On peut les implémenter avec PRISME. Voici ce que ça donne en abonnement mensuel vs one-shot."

---

## STACK TECHNIQUE

### Ce qui existe déjà (skills Hermes)
- `seo-local-audit` → SCOUT-1 (scan site + SEO local)
- `lec-scout` → SCOUT-2 (évaluation signal/process)
- `cortex-leman-compliance-agent` → SCOUT-3 (RGPD/AI Act)
- `Knowledge Compiler` → RESEARCH (compilation + cross-référence)
- `Le Narrateur Augmenté` → rapport visuel

### Ce qui manque
1. **Dashboard live** — interface web temps réel qui montre les agents travailler (logs qui défilent, scores qui se remplissent, icônes par agent)
2. **Template rapport audit** — format PRISME standardisé (PDF + HTML interactif)
3. **Scoring engine** — formules des 6 axes du score PRISME

### Implémentation du dashboard
Option la plus pragmatique : **HTML statique + WebSocket** ou **terminal-to-web** (ce que fait déjà Hermes desktop via inspecting-hermes-desktop-dom).

Ou plus simple : **une page web qui poll un fichier JSON** que les agents écrivent en temps réel. Pas besoin de WebSocket.

```
scout-1.log  →  /tmp/audit-{client}/status.json  →  page HTML
scout-2.log  →        ↑                           ←  refresh 2s
scout-3.log  →        ↑
```

---

## MODÈLE ÉCONOMIQUE

| Niveau | Prix | Contenu | Objectif |
|---|---|---|---|
| **Diagnostic Express** | Gratuit (30 min) | Scan site + score PRISME + 1 recommandation | Hook d'acquisition, lead magnet |
| **Diagnostic Complet** | 500-1,500 CHF | 45 min live + rapport complet + démo mini-boucle | Conversion en abonnement |
| **Diagnostic + Implémentation** | Sur devis | Diagnostic complet + 1 opportunité implémentée live | Upsell direct |

**Funnel** : Diagnostic Express (gratuit) → 40% convertissent en Diagnostic Complet → 50-60% convertissent en abonnement PRISME.

Cible de Corey Ganim : 50-60% de conversion assessment → implémentation.
**Cible PRISME : 70%+** parce que le prospect *voit* les agents travailler. Le produit se vend lui-même.

---

## POURQUOI ÇA MARCHE (psychologie)

1. **Transparence = confiance** — les PME FR-CH sont sceptiques face à l'IA. La voir travailler en direct lève la peur.
2. **Instantanéité = valeur perçue** — un rapport en 48h = "ils ont pris du temps". Un rapport en 10 min en direct = "c'est surpuissant".
3. **Conformité visible = différenciateur** — aucun concurrent ne montre un scan RGPD en direct. C'est ton moat rendu tangible.
4. **Parallélisme = "équipe"** — voir 3 agents en parallèle au lieu d'un humain séquentiel = la promesse "agence d'une personne qui en vaut dix" démontrée physiquement.

---

## DIFFÉRENCIATION vs CONCURRENTS

| | Corey Ganim ($999) | @mathieuhq (Boost) | **PRISME Live** |
|---|---|---|---|
| Format | PDF statique | Formation vidéo | **Live agentique** |
| Délai | 48h | Instant (mais asynchrone) | **10 min en direct** |
| Personnalisé | Template générique | Pas un audit | **100% sur-mesure** |
| Conformité | ❌ | ❌ | **✅ RGPD/AI Act en direct** |
| Démo produit | ❌ | ❌ | **✅ mini-boucle PRISME** |
| Conversion cible | 50-60% | N/A | **70%+** |

---

## CHECKLIST D'IMPLÉMENTATION

- [ ] Définir les formules de scoring des 6 axes
- [ ] Créer le template HTML du dashboard live (logs qui défilent)
- [ ] Créer le template rapport PRISME (PDF + HTML)
- [ ] Script orchestrateur : lance 3 scouts en parallèle → compile → rapport
- [ ] Tester sur cortex-leman.ch lui-même (dogfooding)
- [ ] Créer la landing page "Diagnostic PRISME Live" (CTA booking)
- [ ] Premiers diagnostics pilotes (3 prospects FR-CH gratuits → case studies)

---

## PROCHAIN STEP

Le **MVP techniquement réalisable aujourd'hui** :

1. Lancer `seo-local-audit` + `cortex-leman-compliance-agent` en parallèle sur l'URL du prospect
2. Capturer les outputs dans un JSON
3. Générer le rapport HTML à partir du JSON
4. Partager l'écran pendant que ça tourne

Pas besoin de dashboard fancy pour la V1. Le terminal Hermes qui défile sur un écran partagé en visio suffit pour l'effet "wow". Le dashboard HTML vient en V2.
