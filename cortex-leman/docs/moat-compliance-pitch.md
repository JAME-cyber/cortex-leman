# Moat Compliance: Pourquoi l'AI Act est notre avantage concurrentiel

> Version 1.1 — 22 août 2026 (correction horloge réglementaire: report Digital Omnibus, Règlement UE 2026/1744 — cf. `competitor-registry.md` §3)  
> Document de positionnement stratégique pour Cortex Leman  
> Audience: Tars (propriétaire), pas le client final

---

## 1. LE PROBLÈME — L'AI Act change la donne pour les PME FR-CH

### 1.1 État des lieux réglementaire

**L'AI Act EU (Article 50) est en vigueur depuis le 2 août 2026.** Il impose des obligations concrètes qui touchent directement les PME romandes:

| Obligation | Échéance | Sanction | Impact PME FR-CH |
|---|---|---|---|
| **Labeling contenus IA réalistes** | Immédiate (2 août 2026) | Jusqu'à 35M€ ou 7% CA mondial | Vidéos marketing, posts social, newsletters automatisées |
| **Transparence des systèmes d'IA générale** | 2 août 2026 | Jusqu'à 15M€ ou 3% CA | Tous usages OpenAI/Claude en production |
| **Évaluation d'impact IA** | 2 décembre 2027 (report Digital Omnibus 07/2026 — était 02/02/2027) | Suspend l'activité | Automatisation de processus clients |
| **Registre des usages IA** | 2 août 2028 (Annexe I embarqué — était 02/08/2027) | 10M€ ou 2% CA | Documentation obligatoire de tous les workflows IA |

### 1.2 Réalité terrain

**90% des PME romandes utilisent déjà l'IA sans le savoir:**
- Mailchimp (Subject line optimizer) = IA générative
- Canva (Magic Design) = IA générative  
- Salesforce Einstein = système d'IA à usage général
- Même Microsoft 365 Copilot = soumis à l'Article 50

**Conséquence:** Ces PME sont **déjà en infraction** depuis le 2 août 2026.

### 1.3 Le piège des amendes

| Scénario | Amende maximum | Probabilité 2026-2027 |
|---|---|---|
| PME 5M€ CA utilisant Canva Pro sans labeling | 1,75M€ | Faible (pas de contrôles systématiques) |
| PME exportatrice UE avec contenus non-labelés | 35M€ ou faillite | Moyenne (concurrents peuvent signaler) |
| Agence marketing client UE sans conformité | Perte clients + sanctions | **Forte** (clients exigent compliance) |

**Le risque n'est pas l'amende — c'est la perte de marchés.**

---

## 2. L'ANGLE MORT — Pourquoi les concurrents ne sont pas prêts

### 2.1 Landscape concurrentiel

| Concurrent | Offre IA | Mention compliance | Status conformité |
|---|---|---|---|
| **Vercel "V"** | AI Templates, Agent deployment | ❌ Aucune | **Non conforme** |
| **OpenAI Enterprise** | GPT-4, Custom models | ❌ "Responsible AI" générique | **Non conforme** |
| **Wrappers OpenAI** (90% des agencies) | ChatGPT rebrandé | ❌ Jamais mentionnée | **Non conforme** |
| **Agencies digitales** | "Solutions IA sur-mesure" | ❌ Évitent le sujet | **Non conforme** |
| **Microsoft Copilot** | Integration Office 365 | ❌ Délègue compliance au client | **Non conforme** |

### 2.2 Pourquoi cet angle mort?

**Raisons techniques:**
- Aucun routing multi-provider natif
- Pas de moteur de règles séparé du LLM
- Modèle SaaS global incompatible avec réglementations locales

**Raisons commerciales:**
- Marché US = pas d'AI Act
- Scaling global vs conformité locale = contradiction
- Compliance = complexité = anti-scalabilité

**Raisons stratégiques:**
- Clients enterprise attendent que le vendor résolve la compliance
- Vendor global délègue au client local
- **Résultat: personne ne prend la responsabilité**

### 2.3 La preuve

Recherche exhaustive (7 août 2026) sur les sites de:
- OpenAI, Anthropic, Vercel, Replicate, Hugging Face
- 50+ agencies digitales FR-CH
- **Aucune mention d'AI Act, labeling, ou C2PA**

---

## 3. NOTRE MOAT — Ce qu'on a que les autres n'ont pas

### 3.1 Architecture technique différenciante

| Capacité | Cortex Leman | Concurrents |
|---|---|---|
| **Routing multi-provider** | ✅ GLM/Claude/GPT selon cas d'usage | ❌ Lock-in single provider |
| **Moteur de règles dures** | ✅ Compliance gate = hard override LLM | ❌ Prompt engineering fragile |
| **C2PA signing natif** | ✅ Signature cryptographique automatique | ❌ N'existe pas |
| **QA vision externe** | ✅ Validation croisée systématique | ❌ Auto-évaluation LLM |
| **Self-hosted option** | ✅ Données restent en Suisse | ❌ Cloud global obligatoire |

### 3.2 Expertise juridique FR-CH

**Avantage réglementaire:**
- nLPD suisse (protection données) = natif
- RGPD transfrontalière = maîtrisé
- AI Act = anticipé et intégré
- **Combinaison unique:** aucun concurrent n'a les 3

**Avantage opérationnel:**
- Diagnostic de gouvernance (pas "audit" = risque juridique)
- Validation par expertise locale, pas template global
- Partenariats DPO/avocats suisses

### 3.3 Méthodologie PRISME

**Ce que PRISME résout que les autres ne voient pas:**

```
Brief client → Compliance Gate → Production → Signature C2PA → Delivery

         Pilotage (orchestration)
              ↓
Recherche + Ingénierie (production parallèle)
              ↓
    Scoring (RGPD/AI Act validation)
              ↓
    Multi-canal (distribution adaptée)
              ↓
     Évaluation (learning loop)
```

**Différence clé:** Le compliance gate intervient **pendant** la production, pas après. Un LLM génère, le moteur de règles accepte/refuse/modifie.

---

## 4. LE PITCH CLIENT — 3 angles selon le profil

### 4.1 PME qui produit du contenu

**Profil:** Restaurant, cabinet dentaire, agence immo, e-commerce  
**Pain point:** "On utilise IA pour nos posts, mais on ne sait pas si on respecte la loi"

**Pitch:**
> "Diagnostic PRISME Live: on scanne vos outils actuels pendant que vous regardez. En 45 minutes, vous savez exactement ce qui est conforme, ce qui ne l'est pas, et comment corriger. Pas un PDF de 50 pages — une démonstration en temps réel de ce que l'IA peut faire pour vous, en respectant l'AI Act."

**Levier:** Peur de l'amende + démonstration viscérale de la valeur

### 4.2 Agence qui veut offrir de la conformité

**Profil:** Agence digitale, freelance marketing, intégrateur  
**Pain point:** "Mes clients demandent de l'IA, mais je ne peux pas garantir la conformité"

**Pitch:**
> "Licence PRISME harness: vos clients obtiennent leurs contenus IA + la certification C2PA automatique. Vous facturez la compliance comme un service additionnel. Nous fournissons le moteur, vous gardez la relation client. Revenue share ou licence mensuelle."

**Levier:** Nouvelle ligne de revenus + différenciation vs concurrence

### 4.3 Créateur qui veut se protéger

**Profil:** Influenceur, consultant, coach  
**Pain point:** "Si j'utilise IA, comment je prouve que c'est labelé correctement?"

**Pitch:**
> "Service de signature C2PA: tout votre contenu IA sort avec certification cryptographique. Vous respectez l'AI Act, vous protégez votre réputation, et vos clients savent qu'ils travaillent avec quelqu'un de sérieux sur la compliance."

**Levier:** Protection réputationnelle + proof of compliance

---

## 5. LE C2PA COMME PRODUIT — Signer les contenus IA = service facturable

### 5.1 C2PA Coalition: la future norme

**C2PA (Content Authenticity Initiative)** = Adobe, Microsoft, OpenAI, BBC, NYTimes

**Standard:** Signature cryptographique dans les métadonnées du fichier
- Qui a créé le contenu
- Quels outils ont été utilisés  
- Quelles modifications ont été apportées
- **Si de l'IA a été utilisée** (Article 50 AI Act)

### 5.2 Positionnement produit

**Le service:** "Signature C2PA automatique"

| Package | Prix/mois | Contenu | Cible |
|---|---|---|---|
| **Creator** | 49 CHF | 100 signatures/mois + badge conformité | Influenceurs, consultants |
| **Agency** | 199 CHF | 1000 signatures/mois + API | Agences, freelances |
| **Enterprise** | 499 CHF | Signatures illimitées + audit trail | PME production volume |

### 5.3 Avantage first-mover

**Timing:** C2PA support natif arrive dans:
- Adobe CC: Q4 2026
- Canva Pro: Q1 2027  
- OpenAI API: "Bientôt"

**Notre fenêtre:** 6-12 mois pour établir le marché FR-CH avant que les outils grand public intègrent C2PA nativement.

**Moat technique:** Même quand Canva aura C2PA, il n'aura pas le moteur de règles RGPD ni la validation multi-provider.

---

## 6. ROADMAP — 3 phases sur 6 mois

### Phase 1: Validation (Mois 1-2, Sept-Oct 2026)

**Objectifs:**
- Valider la demande compliance PME FR-CH
- Prouver la conversion Diagnostic Live → abonnement
- Établir les premières références clients

**Deliverables:**
- [ ] 10 Diagnostics PRISME Live gratuits (case studies)
- [ ] 3 conversions diagnostic → abonnement mensuel
- [ ] Landing page cortex-leman.ch/ai-act-compliance
- [ ] Template rapport conformité (PDF + HTML)
- [ ] Partnership 1 avocat/DPO suisse

**Critère go/no-go Phase 2:** ≥30% conversion diagnostic → abonnement

### Phase 2: Déploiement (Mois 3-4, Nov-Déc 2026)

**Objectifs:**
- Industrialiser le processus diagnostic
- Lancer le service C2PA signing
- Acquérir premiers clients récurrents

**Deliverables:**
- [ ] Dashboard diagnostic temps réel (HTML + WebSocket)
- [ ] API C2PA signing (intégration Adobe/Canva)
- [ ] Onboarding client ≤5 jours
- [ ] 8 clients abonnement mensuel
- [ ] Content marketing: 2 posts LinkedIn/semaine + newsletter bi-mensuelle

**Critère go/no-go Phase 3:** 8 clients payants + ≤20% custom par client

### Phase 3: Scale (Mois 5-6, Jan-Fév 2027)

**Objectifs:**
- Licence PRISME harness pour agencies
- Revenue share partnerships
- Leadership marché compliance IA FR-CH

**Deliverables:**
- [ ] Licence harness PRISME (self-service)
- [ ] 3 partnerships agences (revenue share)
- [ ] 20 clients abonnement
- [ ] Thought leadership: 1 intervention/mois (événements, podcasts)
- [ ] Target: 30'000 CHF MRR

---

## 7. MÉTRIQUES & GO/NO-GO

### 7.1 Métriques de traction

| Période | Clients payants | MRR | Diagnostic Live | Conversion % |
|---|---|---|---|---|
| **Oct 2026** | 3 | 4'500 CHF | 10 (gratuits) | 30% |
| **Déc 2026** | 8 | 12'000 CHF | 20 total | 40% |
| **Fév 2027** | 20 | 30'000 CHF | 50 total | 40% |

### 7.2 Indicateurs d'alerte

| Signal | Interprétation | Action |
|---|---|---|
| Conversion diagnostic ≤20% | Produit ne se vend pas | Revoir format/pricing |
| Clients = surtout consultants | Mauvais ICP | Recentrer PME production |
| Demandes "conseil gratuit" | Positionnement perçu gratuit | Clarifier paywall |
| Custom >30% par client | Pas standardisable | Refuser clients non-standard |

### 7.3 Conditions d'abandon

**Si après Phase 1:**
- ≤10% conversion diagnostic → abonnement
- Clients demandent tous du sur-mesure
- Pas de willingness to pay compliance

**Pivot options:**
- Pure services (abandonner le produit)
- Focus C2PA signing only (abandonner diagnostic)  
- Pivot marché (B2C créateurs vs B2B PME)

---

## 8. CONCLUSION — Pourquoi maintenant

### 8.1 Confluence de facteurs

1. **Réglementaire:** AI Act effectif depuis 26 jours
2. **Concurrentiel:** Angle mort total des leaders
3. **Technique:** Stack PRISME opérationnel
4. **Commercial:** PME cherchent des solutions, pas des consultants
5. **Timing:** 6-12 mois avant que les outils grand public rattrapent

### 8.2 Le vrai moat

Ce n'est pas la technologie — c'est **l'intersection unique**:
- Expertise réglementaire FR-CH
- Architecture technique adaptée (multi-provider + règles dures)
- Approche services managés (vs SaaS global)
- Focus PME locales (vs enterprise global)

### 8.3 Fenêtre d'opportunité

**6-12 mois** pour établir:
- Leadership éditorial (seuls à parler compliance IA FR-CH)
- Base clients référence (20+ case studies)
- Partnerships locaux (avocats/DPO/intégrateurs)
- Moat opérationnel (processus standardisé)

Après cette fenêtre, les concurrents rattraperont avec des resources 100x supérieures.

**L'enjeu:** Devenir **LE** référent compliance IA en Suisse romande avant que Microsoft/Adobe/OpenAI prennent ce marché au sérieux.

---

*Document confidentiel — Usage interne Cortex Leman uniquement*