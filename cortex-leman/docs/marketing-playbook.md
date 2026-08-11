# Cortex Leman — Marketing Playbook

> Version 1.2 — 7 août 2026
> Source : synthèse des patterns marketing récupérés (VibeMarketer_, iamsupersocks, Cody Schneider, Campaign Graph) appliqués au stack réel Cortex Leman.
> Révision 1.1 : audit contradictoire GPT-5.6 (7 août 2026) — correction nLPD, reframing "diagnostic" vs "audit", stratégie 1 média signé au lieu de 3 comptes anonymes, métriques pipeline, garde-fous juridiques.
> Révision 1.2 : contre-analyse GPT-5.6 tweet Ventalon (7 août 2026) — Cortex Leman = service managé productisé (PAS SaaS scalable), pitch réécrit (pilot-then-commit), test de productisation (onboarding <5j / <20% custom / <1-2j maint), point de bascule régie vs abonnement (6-8 clients), "autonome" = mot qui dessert, FAQ anti-objections (Ventalon/Copilot/statu quo/n8n).

---

## 1. POSITIONNEMENT

### Le hook principal

**"Le partenaire opérationnel IA des PME romandes."**

Tu ne vends pas du contenu. Tu ne vends pas de l'automatisation. Tu vends une **transformation de posture** :

> Le client cesse d'être la queue et devient le directeur.

C'est exactement le framing de @VibeMarketer_ ("stops being the queue and starts directing it"), mais tu as un avantage qu'il n'a pas : **tu le fais vraiment**. Lui vend un guide théorique sur Codex. Toi tu as un stack opérationnel qui produit du contenu réel, conforme, multi-canal, en autonomie.

### Le narratif "For the 99%" — L'IA pour ceux qui n'ont pas d'agents

> **Volé de Polsia (@polydao, août 2026) et retourné contre eux.**

Le marché IA se coupe en deux :

| Segment | Qui | Outils | Problème |
|---|---|---|---|
| **1%** | Power users | Hermes, Cursor, n8n, agents custom | Aucun — ils se débrouillent |
| **99%** | PME, artisans, fiduciaires | Rien (ou ChatGPT en copier-coller) | Personne ne leur a montré |

Polsia dit: *"Building for the 99%."* On dit la même chose, mais avec un avantage qu'ils n'ont pas: **on parle leur langue, on connaît leurs lois, on est ici.**

#### Le narratif Cortex Leman

> **"L'IA pour les 99% en Suisse romande."**

Pas de prompts. Pas d'agents. Pas de workflows. Pas de 14 tabs Cursor.

La PME romande n'a pas besoin d'apprendre le prompt engineering. Elle a besoin de quelqu'un qui:
1. **Parle français** (pas de support en anglais)
2. **Connaît la nLPD et le RGPD** (pas de fuite de données)
3. **Est là en cas de problème** (pas un chatbot au Texas)
4. **Montre ce que l'IA peut faire pour ELLE** (pas un cours théorique)

#### Le pitch en 3 phrases

> *"Vous payez déjà Google Workspace, Microsoft 365, des outils que vous n'exploitez pas à 10%. L'IA est dedans. Personne ne vous l'a montré.*
>
> *On vous le montre en 2h. Et si vous voulez aller plus loin, on construit des automatisations sur-mesure qui respectent le droit suisse.*
>
> *Pas besoin d'apprendre le prompt engineering. C'est notre travail."*

#### Pourquoi ça marche contre Polsia (le moat)

| Polsia (le concurrent) | Cortex Leman (nous) |
|---|---|
| SaaS générique mondial | Sur-mesure PME romande |
| Pas de RGPD/nLPD | Compliance native FR-CH |
| Support en anglais | On parle français, on est à Genève |
| "AI co-founder" (effrayant pour un patron de PME) | "Partenaire opérationnel" (rassurant) |
| Le client doit apprendre la plateforme | On fait tout, le client valide |
| Data residency: cloud US | Data residency: CH/UE |

#### Le persona "Magalie de la compta"

> Volé de @LeDindonFiscal (194 likes, 75 replies, août 2026) : *"Je plains les mecs qui ont fait 5 ans d'études pour faire en 10 mois ce que Magalie de la compta fait désormais en 10 minutes."*

Magalie = notre client idéal. Elle est comptable dans une fiduciaire FR-CH. Elle ne sait pas coder. Mais avec Gemini dans Google Sheets, NotebookLM sur ses docs, et un quick audit de 2h, elle peut:
- Automatiser des reconciliations (Sheets + Gemini)
- Q&A sur 1000 pages de doctrine fiscale (NotebookLM)
- Répondre aux clients depuis Gmail sans tout retaper

**Magalie n'a pas besoin d'un dev. Elle a besoin de quelqu'un qui lui montre ce qui est déjà là.**

C'est Cortex Leman.

#### Angle anti-hype (volé de @mathieuhq, conservé)

> *"Pas de promesse ridicule sur une IA qui dirigera votre business toute seule pendant que vous dormez. On ne remplace pas vos employés. On leur enlève la corvée pour qu'ils fassent ce qui compte."*

#### Les 3 levels du narratif "99%"

1. **Sensibilisation** (Quick Audit Google, 500-1K CHF): *"L'IA est dans vos outils. On vous la montre."*
2. **Transformation** (Audit RGPD-IA + Build, 2-15K CHF): *"On automatise vos process. Conforme."*
3. **Libération** (Retainer mensuel, 500-3K CHF/mois): *"On gère tout. Vous dirigez."*

### Le framing éditorial

> **IA opérationnelle et gouvernée pour PME romandes.**

Les PME n'achètent pas spontanément de la "conformité IA". Elles achètent : moins de risque, une décision claire, un déploiement plus rapide, une validation de leurs outils, un gain opérationnel sans fuite de données. La conformité est une **composante de la promesse**, pas le produit éditorial entier.

### Matrice de différenciation

| Dimension | Concurrents (VibeMarketer, ÉLYSIA, Lead Mapping) | Cortex Leman |
|---|---|---|
| Nature du produit | Guide / Template / Outil clic-bouton | Harness agentique autonome |
| Boucle de production | Manuelle (Obsidian, Lovable) | Automatisée (scout→delivery) |
| Conformité | Absente | Native (nLPD, RGPD, AI Act) |
| Coût client | 99€/mois outil + temps manuel | Service clé en main ou licence harness |
| FR-CH | Non | Natif (Suisse romande, droit suisse) |
| Multi-canal | 1 canal à la fois | Pipeline multi-canal natif |

> **Note conformité (révision 1.1) :** La nLPD (loi suisse sur la protection des données, révisée) est le socle réglementaire central pour les PME suisses. Le RGPD s'applique aux activités transfrontalières (clients UE). L'AI Act est pertinent pour les entreprises exposées au marché européen. MiCA et ZertES sont réservés aux **verticals spécifiques** (fintech/crypto, signature électronique) et ne doivent pas apparaître dans le messaging principal sauf ciblage vertical explicite.

### Les 3 marchés cibles

1. **PME FR-CH** (primary) — besoin contenu + conformité, pas de team marketing
2. **Agencies & freelances** (secondary) — veulent ton harness pour servir leurs clients
3. **Créateurs de contenu** (tertiary) — veulent la boucle de production automatisée

---

## 2. LA MÉTHODE — Nommage & Branding

### Problème
Ta boucle existe mais n'est pas nommée. Un workflow non-nommé ne se vend pas. @iamsupersocks l'a compris : PKM standard → "méthode ACE" = vendable.

### Propositions de noms (à valider)

**Option A — SPECTRE** (le plus mémorisable)
```
S → Scout        (signal detection, trend monitoring)
P → Produce      (research → script → assets → render)
E → Extract      (apprentissages capturés automatiquement)
C → Capitalize   (session → skill → template réutilisable)
T → Transmit     (multi-canal delivery + distribution)
R → Repeat       (cron-driven, autonome)
E → Evaluate     (QA vision + cross-validation + compliance gate)
```

**Option B — ORBIT**
```
O → Observe    (scout)
R → Research   (knowledge compiler)
B → Build      (production)
I → Iterate    (QA + feedback)
T → Transmit   (delivery)
```

**Option C — PRISME** (FR, évoque la décomposition de la lumière = décomposition d'un brief en canaux)
```
P → Pilotage     (brief → orchestration)
R → Recherche    (scout + research)
I → Ingénierie   (production multi-modal)
S → Scoring      (QA + compliance gate)
M → Multi-canal  (delivery)
E → Évaluation   (feedback loop → learning)
```

### Recommandation
**PRISME**. Raisons :
- 100% français (cohérent FR-CH)
- Métaphore visuelle forte (prisme = 1 entrée → spectre = 1 brief → multi-canal)
- "Évaluation" en fin = compliance + QA = ton différentiateur unique
- Searchable, brandable, personne ne l'utilise dans ce contexte

---

## 3. LA BOUCLE — Comment la présenter publiquement

### Version pitch (10 secondes)
> "PRISME : un brief entre, un spectre de contenu conforme sort. Scout, recherche, production, scoring RGPD, distribution multi-canal. Le client dirige, les agents exécutent."

### Version détaillée (pour site / proposal)

```
                    ┌─────────────────────────────────┐
                    │         BRIEF CLIENT             │
                    │  (objectif, audience, canaux)    │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │   P — PILOTAGE (orchestrateur)   │
                    │  Découpe le brief en workloads   │
                    │  indépendants → fan-out agents    │
                    └──────────────┬──────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                     │
    ┌─────────▼─────────┐ ┌────────▼─────────┐ ┌────────▼─────────┐
    │ R — RECHERCHE     │ │ I — INGÉNIERIE    │ │  (parallèle)     │
    │ Scout + Knowledge │ │ Script + Assets   │ │  Sub-agents      │
    │ Compiler          │ │ + Render (video)  │ │  indépendants    │
    └─────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
              │                    │                     │
              └────────────────────┼────────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │   S — SCORING (compliance gate)  │
                    │  QA vision externe + validateur  │
                    │  RGPD/AMF/MiCA + moteur de       │
                    │  règles dures (override LLM)     │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │ M — MULTI-CANAL (delivery)       │
                    │  Telegram, email, social, web,   │
                    │  podcast — auto-adapté par canal │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │   E — ÉVALUATION (learning)      │
                    │  Métriques → skills → templates  │
                    │  → feed-back dans le prochain    │
                    │  cycle (cron-driven)             │
                    └─────────────────────────────────┘
```

### Les 3 éléments qu'aucun concurrent n'a

1. **Compliance gate natif** — pas un add-on, un étage du pipeline. RGPD, AMF L541-1, MiCA. Le LLM génère, le moteur de règles valide ou veto.
2. **QA vision externe** — chaque output passe par validation visuelle croisée. Pas de sortie sans feu vert.
3. **Self-hosted, souverain** — tes données restent chez toi. En Suisse, c'est un argument de vente, pas un détail technique.

---

## 4. STRATÉGIE DE CONTENU — "Un média vertical signé"

### Principe directeur (révision 1.1)

Le concept de "page-thème" (Greg Isenberg / Julian Shapiro) s'applique à Cortex Leman, **mais pas sous forme de comptes anonymes**. En Suisse romande B2B, la confiance est déterminante. Une page opaque sur la conformité IA pose question : qui est responsable ? est-ce un cabinet juridique ? est-ce automatisé ?

**Architecture recommandée : 1 média vertical signé, pas 3 comptes anonymes.**

- **Profil personnel du fondateur** = moteur de distribution principal (LinkedIn organique > page entreprise)
- **Newsletter thématique** = rendez-vous éditorial et audience possédée
- **Cortex Leman** = opérateur transparent (pas caché, pas/clandestin)
- **PRISME** = méthodologie en arrière-plan, démontrée par les résultats

> Transparence : "Média édité par Cortex Leman. Nous aidons les PME romandes à déployer des workflows IA gouvernés."

### Pourquoi pas 3 comptes-thèmes ?

3 comptes = 3 audiences, 3 lignes éditoriales, 3 offres, 3 parcours de conversion, 3 systèmes de vente. Pour un bootstrapper solo, c'est **3 entreprises**, pas une stratégie de contenu. L'automatisation réduit le coût de production, pas le coût de validation, d'interaction, de confiance, de vente et de support.

### Pourquoi pas un compte anonyme ?

Le modèle Julian Shapiro fonctionne avec 100k+ followers sur un marché US massif. En FR-CH (marché petit, confiance = critère #1), l'anonymat produit l'effet inverse :
- Qui valide les affirmations réglementaires ?
- Est-ce un compte automatisé brandissant des termes juridiques ?
- Funnel implicite = bait-and-switch quand Cortex Leman apparaît

### Calendrier de contenu (automatisé via cron, validation humaine obligatoire)

| Canal | Format | Fréquence | Source |
|---|---|---|---|
| LinkedIn (profil perso) | Post analytique | 2x/sem | Apprentissage session → extraction |
| Newsletter | Email long-form | 1x/2sem | Knowledge Compiler output |
| YouTube | Video essay (5-10min) | 1x/mois | Script → Seedance/ComfyUI render |
| Site web | Case study / benchmark | 1x/mois | Session complète documentée |

### Les 4 piliers éditoriaux

1. **Cas d'usage opérationnels** — automatiser une qualification commerciale, préparer des propositions, traiter des documents, produire du contenu avec validation humaine. (Preuve pratique)
2. **Gouvernance et données** — nLPD, évaluation des fournisseurs IA, règles internes, transferts et conservation, contrôle humain. (Moat éditorial)
3. **Tests et benchmarks** — comparaison cloud/self-hosted, coûts réels, précision, temps économisé, risques observés. (Données originales = vrai différenciateur)
4. **Retours terrain** — avant/après, erreurs, limites, cas où l'automatisation ne vaut pas la peine. (Authenticité = confiance)

### Règle de validation contenu réglementaire (obligatoire)

Tout contenu touchant au droit (nLPD, RGPD, AI Act) doit :
- Citer les **sources primaires** (loi, ordonnance, ligne directrivée)
- **Dater** les analyses (le droit évolue)
- Distinguer **droit en vigueur** vs calendrier d'application vs propositions
- Indiquer la **juridiction** concernée (CH, UE, transfrontière)
- Passer par **validation humaine** avant publication
- Corriger publiquement les erreurs

---

## 5. ARCHITECTURE MARKETING AGENTIQUE

### Inspiré du modèle Cody Schneider (Companies Graph)

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA WAREHOUSE                            │
│  (ClickHouse ou SQLite selon phase)                         │
│  Sources: analytics sites, engagement social,               │
│  conversions Stripe/Resend, cron outputs                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
    ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
    │  SCOUT      │ │  CRÉATIF    │ │  DISTRIB.   │
    │  Signal     │ │  Génération │ │  Publish    │
    │  detection  │ │  contenus   │ │  + promote  │
    │  + scoring  │ │  multi-fmt  │ │  + kill     │
    └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
           │               │               │
           └───────┬───────┘───────┬───────┘
                   │               │
            ┌──────▼──────┐ ┌──────▼──────┐
            │  COMPLIANCE │ │  LEARNING  │
            │  GATE       │ │  LOOP      │
            │  (RGPD/AMF) │ │  (métriques│
            │             │ │  → skills) │
            └─────────────┘ └─────────────┘
```

### Phase 1 (immédiat) — Manuel + cron
- Cron watchdogs : monitoring signaux (tweets, arXiv, actualité)
- Cron production : génère brouillons, tu valides avant publication
- Pas de warehouse encore — SQLite + session logs suffisent

### Phase 2 (Q3 2026) — Semi-autonome
- Airbyte → SQLite/Postgres pour unifier les data sources
- Agent créatif génère + publie sur canaux secondaires sans validation
- Learning loop : engagement par post → feed-back dans le scout

### Phase 3 (Q4 2026) — Pleinement autonome
- ClickHouse warehouse
- Agent décide du calendrier, du format, du canal
- Kill losers, promote winners automatiquement
- Compliance gate reste hard-rule (jamais délégué au LLM seul)

---

## 6. MODÈLE ÉCONOMIQUE

### 3 niveaux de monétisation

| Niveau | Produit | Prix | Cible |
|---|---|---|---|
| **Entry** | Diagnostic de gouvernance IA (1 workflow, 1 rapport, 1 plan d'action) | 500-1'500 CHF | PME one-shot |
| **Core** | Abonnement service mensuel (contenu auto + gouvernance) | 1'500-5'000 CHF/mois | PME récurrent |
| **Scale** | Licence harness PRISME (self-hosted) | 500-2'000 CHF/mois | Agencies, freelances |

### Périmètre du Diagnostic (obligatoire — éviter le mot "audit")

> ⚠️ Le mot **"audit"** implique méthodologie formelle, preuves, responsabilité et potentiellement un rapport opposable. Sans statut de cabinet juridique, DPO certifié ou auditeur agréé, ce terme est juridiquement dangereux en Suisse.

**Nom officiel : Diagnostic de gouvernance IA et données**

Périmètre explicite :
- Cartographie d'un workflow IA
- Données utilisées et outils impliqués
- Identification des principaux risques (nLPD/RGPD)
- Contrôles recommandés
- Décision : lancer, modifier ou arrêter

Exclusions explicites (à inclure dans tout livrable) :
- **Ceci n'est pas un avis juridique**
- Non-opposable ; ne remplace pas l'avis d'un avocat ou DPO certifié
- Recommandation de validation par un juriste suisse lorsque nécessaire
- Idéalement : partenariat formel avec un avocat/DPO suisse pour les cas qui dépassent le diagnostic

### Produits dérivés (valeur perçue = méthode nommée)

| Produit | Format | Prix | Inspiration |
|---|---|---||---|
| Guide PRISME (méthode complète) | PDF + templates | 49-99 CHF | ÉLYSIA (Obsidian vault) |
| Skills pack Cortex Leman | Pack de skills Hermes | 199-499 CHF | VibeMarketer "complete setup" |
| Formation vidéo PRISME | 5-10 modules | 299-799 CHF | Cody Schneider playbook |
| Template vault Obsidian/Notion | Config + workflows | 79-149 CHF | ACE method |

### Principe de pricing
Le concurrent le plus cher dans l'espace FR-CH = Lead Mapping à 99€/mois pour un scanner Google Maps. Ton stack fait 10x plus. Ne pas brader — positionner premium et justifier par la conformité + la supervision incluse.

> ⚠️ À ce stade, Cortex Leman n'est pas un SaaS scalable. C'est un **service managé productisé** reposant sur un harness agentique. Chaque client demande intégration, connecteurs et validation. Le coût marginal n'est pas zéro — il est de 0,5 à 3 jours humains par mois et par client stabilisé, plus 2 à 5 jours/mois pour le socle mutualisé. Le vrai risque est la **variance** : un incident peut absorber 3 jours non planisés.

### Pitch de vente (révisé — GPT-5.6, 7 août 2026)

**JAMAIS dire :**
> *"Des agents qui se maintiennent eux-mêmes, 24/7, pour le coût d'une licence mensuelle."*

Cette promesse est **deshonnête** (le coût de maintenance existe), **juridiquement risquée** (qui est responsable d'une action autonome ?), et **inadaptée au marché** (les PME veulent des résultats supervisés, pas de l'autonomie non contrôlée).

**TOUJOURS dire (pilot-then-commit) :**
> *"Nous automatisons le traitement de [processus précis] sans remplacer votre système actuel. Objectif : réduire le délai de X à Y et économiser Z heures par mois. Les actions sensibles restent validées par un humain. L'abonnement inclut la supervision, les mises à jour, la gestion des incidents et un rapport mensuel de performance. Si les objectifs convenus ne sont pas atteints pendant le pilote, vous ne passez pas en abonnement."*

**Règle : vendre le résultat, pas l'agent.** Le patron veut savoir : quel processus amélioré, combien d'heures économisées, quel délai réduit, quel risque éliminé, qui répond en cas d'erreur. Pas "agents autonomes".

---

## 7. PLAYBOOK D'ACQUISITION

### Tactiques par phase

**Phase 1 — Validation & Preuve (mois 1-3)**

> ⚠️ Avant de produire du contenu : valider l'ICP (Ideal Customer Profile) par 12-15 entretiens terrain avec des dirigeants de PME romandes, COO, responsables marketing, DPO/RSSI. Questions clés : quels outils IA utilisent-ils réellement ? Quelles données y entrent ? Qui bloque les projets ? Quel livrable justifierait 1'000 CHF ?

- Média vertical signé sur LinkedIn (profil perso du fondateur) : 2 posts/sem
- Newsletter bi-mensuelle (rendez-vous éditorial, audience possédée)
- SEO local FR-CH (skill seo-local-audit sur villes clés : Genève, Lausanne, Montreux, Annecy, Fribourg)
- 3 diagnostics payants = premiers case studies
- Modèle de registre des usages IA gratuit (lead magnet — pas PDF théorique, outil pratique)
- **Critère de réussite 90 jours** : 10-15 conversations avec profils cibles, 2-3 diagnostics payants, ≥1 conversion vers mission récurrente. Si l'audience est surtout des consultants/freelances → mauvaise alignment, ajuster le thème.

**Phase 2 — Distribution (mois 2-3)**
- Newsletter hebdo (Resend, déjà en stack)
- YouTube (pipeline vidéo vertical existant, adapter pour long-form)
- LinkedIn (adaptation threads X)

**Phase 3 — Acquisition (mois 3-4)**
- Lead capture : skill inbound-lead-capture-system (formulaire + ads + harvester + dispatcher)
- Social proof : témoignages clients, métriques publiques
- Partnerships : complémentaires (comptables, avocats d'affaires FR-CH qui réfèrent)

**Phase 4 — Scale (mois 4+)**
- Le harness PRISME comme produit (licence)

### Test de productisation (gate avant Phase 4)

> ⚠️ Avant de scaler : un framework n'est pas un produit. PRISME améliore la livraison, mais tant que chaque client demande du sur-mesure, Cortex Leman est un **cabinet de services avec un bon framework interne**, pas un produit scalable.

**3 conditions à remplir avant de pousser la Phase 4 :**

| Condition | Seuil | Mesure |
|---|---|---|
| Onboarding standardisé | **< 5 jours** pour un nouveau client | Du contrat à la première exécution agent |
| Personnalisation limitée | **< 20% de modifications spécifiques** par client | Ratio code/config custom vs socle commun |
| Maintenance contrôlée | **< 1-2 jours humains/mois** par client stabilisé | Support + incidents + mises à jour |

Si ces seuils ne sont pas tenus, le "MRR" est en réalité de la régie agentique déguisée en abonnement. Ne pas scaler un modèle qui ne standardise pas — d'abord standardiser, ensuite scaler.
- Formation / certification partenaires
- Marketplace de skills communautaires

---

## 8. TECHNIQUES MARKETING EMPRUNTÉES (et adaptées)

### De @VibeMarketer_
| Technique | Comment l'adapter |
|---|---|
| Authority hijack | Ne pas emprunter l'autorité d'un autre — utiliser la tienne (case studies réels) |
| Shift de posture | "Cesse d'être la queue" = ton pitch central |
| Abstraction ascendante | Toujours présenter le stack comme un paradigme (PRISME), pas une liste de features |
| CTA différé | Chaque contenu → "le setup complet PRISME → [lien]" |

### De @iamsupersocks / méthode ACE
| Technique | Comment l'adapter |
|---|---|
| Branding par acronyme | PRISME — 100% français, searchable |
| Boucle visible | Diagramme PRISME = ta boucle rendue visible et vendable |
| Co-branding | Partenariats avec complémentaires FR-CH (réciprocité de visibilité) |
| Quote-retweet comme socle | Récupérer le travail des autres → ajouter ton cadre PRISME par-dessus |

### De Cody Schneider (Marketing Agent Architecture)
| Technique | Comment l'adapter |
|---|---|
| Data warehouse unifié | Phase 2-3 de ton architecture |
| Kill losers, promote winners | Learning loop dans PRISME étape E |
| Entropy injection | Scout PRISME scanne signaux externes en continu |
| "Facebook = meilleur canal B2B" | Tester Ads pour PME FR-CH locale |

### Du Campaign Graph pattern (@shannholmberg)
| Technique | Comment l'adapter |
|---|---|
| Graphe swappable | PRISME = graphe où chaque nœud (scout, research, render) est une skill remplaçable |
| Model routing par nœud | Déjà en place (GLM pour reasoning, Claude pour rewriting, etc.) |
| Pipeline complet idea→delivery | C'est littéralement PRISME |

---

## 9. CHECKLIST D'EXÉCUTION IMMÉDIATE

- [ ] Valider le nom PRISME (ou choisir alternative)
- [ ] Créer le diagramme PRISME en assets de marque (Le Narrateur Augmenté)
- [ ] Premier thread X "Build in the open" : montrer le harness PRISME en action
- [ ] Page de destination : cortex-leman.ch/prisme (ou équivalent)
- [ ] Configurer cron watchdogs : monitoring signaux marché FR-CH
- [ ] Premier case study (Cortex Leman comme propre client)
- [ ] MVP du guide PRISME PDF (lead magnet)
- [ ] SEO local : 5 villes FR-CH (Genève, Lausanne, Montreux, Annecle, Fribourg)

---

## 10. MÉTRIQUES À SUIVRE

> Les impressions et followers sont des indicateurs intermédiaires, pas des résultats. Le calcul "$22/1000 impressions" (Greg Isenberg) est trompeur : une impression organique ≠ une impression ciblée payante, et 500 followers ne garantissent pas 1000 impressions. Mesurer ce qui mène à du chiffre d'affaires.

### Métriques principales (pipeline, pas vanité)

| Métrique | Cible 3 mois | Cible 6 mois | Cible 12 mois |
|---|---|---|---|
| Conversations avec profils cibles (ICP) | 10-15 | 30-50 | 100+ |
| Diagnostics payants | 2-3 | 5-8 | 15-20 |
| Conversion diagnostic → mission récurrente | ≥1 | 3-5 | 8-12 |
| Abonnés newsletter (qualifiés) | 100 | 400 | 1'500 |
| Inbound leads / mois | 3-5 | 10-15 | 30-40 |
| Clients payants | 2 | 8 | 20 |
| MRR | 2'000 CHF | 10'000 CHF | 30'000 CHF |

### Indicateurs de alerte (à surveiller)

| Signal d'alerte | Interprétation | Action |
|---|---|---|
| Audience = surtout consultants/freelances | Mauvais alignement ICP | Ajuster le thème éditorial |
| Beaucoup d'impressions, peu de conversations | Le contenu intéresse mais ne convertit pas | Renforcer CTA, tester lead magnet |
| Demandes de "conseil gratuit" | Positionnement perçu comme gratuit | Clarifier périmètre payant |
| CAC contenu > marge générée | Stratégie non rentable | Réduire cadence, concentrer effort |

### Formule de coût d'acquisition contenu

> **CAC contenu = (temps fondateur × taux horaire + outils + production) / nombre de clients attribuables**

> **Valeur éditoriale = marge du pipeline influencé − coût total de production**

Si un post prend 3h mais ne produit aucune conversation qualifiée, ses impressions ne sont pas "de l'argent en poche".

---

## 11. GARDE-FOUS & AVERTISSEMENTS (Audit GPT-5.6, 7 août 2026)

### 11.1 Risque juridique — "Audit" vs "Diagnostic"

Le terme "audit" implique en droit suisse une méthodologie formelle, des preuves, une responsabilité et potentiellement un rapport opposable. Sans statut de cabinet juridique, DPO certifié ou auditeur agréé, ce terme est **juridiquement dangereux**.

**Toujours utiliser :** Diagnostic, diagnostic de gouvernance, revue limitée, screening, cartographie.
**Jamais :** Audit, certification, validation conforme, attestation.

### 11.2 Risque réputationnel — Contenu réglementaire automatisé

Un seul post erroné sur la nLPD, l'AI Act ou l'applicabilité du RGPD peut détruire le positionnement. Le scoring compliance de PRISME est un filtre production, **pas une preuve de fiabilité juridique**.

Obligations (voir Section 4, règle de validation) : sources primaires, dates, juridictions, validation humaine.

### 11.3 "Self-hosted" ≠ "souverain"

Le mot "souverain" est facilement contestable. Un acheteur sérieux demandera :
- Où sont hébergés les modèles ?
- Les appels passent-ils par OpenAI, Anthropic ou un autre fournisseur ?
- Où sont stockés les logs ?
- Qui a accès aux données ?
- Les données servent-elles à l'entraînement ?
- Quelles garanties contractuelles existent ?

**Positionnement prudent :** "self-hosted, données stockées en Suisse" (démontrable) plutôt que "souverain" (contestable).

### 11.4 Le contenu n'est pas un moat

Un compte qui résume l'actualité peut être copié rapidement. Les actifs défendables réels :

| Actif défendable | Comment le construire |
|---|---|
| Données originales (usages IA PME romandes) | Benchmark local, sondages, cas documentés |
| Cas clients documentés | Avant/après avec métriques |
| Partenariats juridiques | Avocat/DPO suisse référent |
| Communauté locale | Événements, permanences mensuelles |
| Liste email qualifiée | Audience possédée, pas louée |
| Modèles et outils | Checklists, registres, templates adaptés CH |

### 11.5 Risque de capacité

Un solo peut automatiser l'acquisition mais pas indéfiniment : diagnostics, personnalisation, support, mises à jour, intégrations, incidents. **Standardiser avant d'accélérer :**
- Périmètre des offres (défini, borné)
- Livrables types (templates)
- Critères d'éligibilité (qui accepter/refuser)
- Délais (SLA réaliste)
- Support inclus (et ce qui ne l'est pas)

### 11.6 Risque de mauvaise audience

Le contenu conformité attire naturellement : consultants, juristes, étudiants, fournisseurs de logiciels, concurrents — **pas nécessairement les décideurs qui achèteront un diagnostic**.

Mesurer la **part de l'audience correspondant à l'ICP**, pas le total d'abonnés. Si après 90 jours l'audience est >70% non-ICP, le thème est mal aligné.

### 11.7 Régie agentique vs produit — le point de bascule

L'objection de Ventalon ("régie GCP = 12-20k/mois vs agents = difficilement 5k") est **valide à court terme**. La régie génère plus de cash, plus vite, avec moins de risque commercial.

**Mais :**
- La régie plafonne avec le temps humain (20j/mois × TJM). Scalabilité = 0.
- L'abonnement peut scale si — et seulement si — le service est standardisé.

**Point de bascule (quand l'abonnement dépasse la régie) :**
- Régie à 15k€/mois de contribution économique (après temps non facturé, prospection, intercontrats)
- Abonnement à 5k CHF/mois → contribution réelle ~2'500-3'000 CHF par client (après modèles, infra, 1,5j maintenance)
- **Il faut 5 à 8 clients stables** pour égaler la régie
- En intégrant le développement du socle, la prospection, le churn et les pilotes gratuits : **6 à 8 clients**

**Plafond opérationnel réaliste pour un solo :**

| Niveau de standardisation | Clients max | MRR correspondant |
|---|---|---|
| Offre très répétitable, peu de support | 8-12 | 20-60k CHF |
| Service managé borné | 4-6 | 10-30k CHF |
| Agents personnalisés ou critiques | 2-4 | 5-20k CHF |

**Stratégie recommandée (non binaire) :** la régie peut financer le produit. Utiliser des missions consulting pour identifier les problèmes récurrents → transformer ces problèmes en offre standardisée → réduire progressivement la régie au fur et à mesure que le MRR contributif monte.

### 11.8 Le mot "autonome" te dessert

Pour une PME, "agent autonome" déclenche peur et méfiance : Qui est responsable ? Où vont les données ? Peut-il envoyer quelque chose au mauvais client ? Comment auditer ? Que se passe-t-il si l'entreprise disparaît ?

**L'autonomie n'est pas un bénéfice pour le dirigeant. C'est un risque.**

Les premiers cas d'usage PME doivent être : bornés, réversibles, observables, à faible impact, avec validation humaine.

**Vocabulaire à utiliser :** automatisation supervisée, automatisation fiable, traitement automatisé avec validation humaine.
**Vocabulaire à éviter :** autonome, agent intelligent, agent qui décide seul, agent 24/7 sans intervention.

---

## 12. FAQ ANTI-OBJECTIONS (GPT-5.6, 7 août 2026)

### "Pourquoi pas un consultant GCP / cloud ?" (objection Ventalon)

> Un consultant GCP vous facture 800-1'200€/jour pour construire quelque chose que vous devrez maintenir vous-même. Nous automatisons un processus précis avec supervision incluse : mises à jour, gestion des incidents et rapport mensuel. Vous ne payez pas pour de l'infrastructure — vous payez pour un résultat maintenu.

**Si le prospect comparecash immédiat :** ne pas nier que la régie est plus rapide à encaisser. Argumenter sur la **valeur à 3 ans** (accumulation d'actifs, rétention client, MRR cumulé) vs le **cash à 3 mois** (intercontrat, prospection, dépendance à un donneur d'ordre).

### "Microsoft Copilot fait déjà ça"

> Copilot est excellent pour des tâches individuelles dans Microsoft 365. Nous automatisons des **processus métier complets** qui traversent plusieurs outils (ERP, CRM, email, conformité) avec validation humaine et auditabilité. Copilot est un copilote ; nous fournissons un processus complet surveillé.

### "On va attendre que les agents soient inclus dans [Salesforce/SAP/Google]"

> Les agents natifs de ces plateformes seront limités à leur écosystème. Si tout votre SI est chez un seul fournisseur, c'est pertinent. Si vous utilisez plusieurs outils (la majorité des PME romandes), vous avez besoin d'une couche d'orchestration indépendante. C'est exactement ce que nous fournissons.

### "C'est trop cher pour nous" (5'000 CHF/mois)

> À 5'000 CHF/mois, soit 60'000 CHF/an, l'automatisation doit vous économiser au moins 80-120kCHF de valeur annuelle (temps, délais, erreurs évitées). Si nous ne pouvons pas démontrer ce ROI pendant le pilote, vous ne passez pas en abonnement. Le pilote est conçu pour prouver la valeur avant l'engagement.

### "Qu'est-ce qui garantit que vous ne disparaissiez pas ?"

Répondre honnêtement : le harness repose sur Hermes Agent (open-source). Si Cortex Leman disparaît, les configurations et le code restent. Le client n'est pas enfermé dans un binaire propriétaire.

### "Et n8n / Make / Power Automate ?"

> Ces outils excellent pour des automatisations déterministes (si A alors B). Nous traitons des processus qui nécessitent du **raisonnement** : qualifier un lead, prioriser une alerte, rédiger un diagnostic conformité, décider si un contenu respecte la nLPD. Pour les deux, c'est complémentaire, pas concurrent.

### "Pourquoi pas attendre 12-18 mois que le marché mûrisse ?"

> Les PME qui commencent maintenant auront 18 mois de données d'usage, de gouvernance testée et de processus éprouvés. Celles qui attendent rattraperont un retard réglementaire (AI Act entre en application) et opérationnel. Le coût de l'inaction est réel, particulièrement en conformité.
