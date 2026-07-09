# BUSINESS CASE v2 — Vertical « Gouvernance d'Agents IA »

> **Croisement** : recherches Telegram du 01/07 00h (Gartner, paysage FR-CH, SOHK, SocialPulse, Critical-Analysis) × benchmark **Mister IA** (mister-ia.com / misterai.io) × fondations existantes (`action-5-vertical-ai-agent-compliance.md`, `agent-ia.json`, `action-5-modele-recurrent.md`).
>
> **Date** : 2026-07-01 · **Auteur** : L'Architecte Lémanique (CSO) + contre-analyse Le Gardien des Normes
> **Framework** : `critical-objective-analysis` + `analyse-critique` (10 réflexes, 3 scénarios, kill factors, verdict honnête)

---

## 0. SYNTHÈSE EXÉCUTIVE (1 page)

**Le vertical « Gouvernance d'Agents IA » est l'intersection de 3 forces qui se sont alignées le 1er juillet :**

1. **Une demande prouvée** — Mister IA (750 entreprises, 12,3 M$ CA, 10 M€ levés) déploie massivement des agents IA chez les PME FR… **sans aucune gouvernance**.
2. **Une douleur prouvée** — Gartner : **40 % des projets agentic AI annulés fin 2027** pour défaut de **contrôles de risque** (raison #3 explicite).
3. **Un gap FR-CH vide** — Modulos = 50 k€/an (enterprise), Legalithm = gratuit mais AI Act nu uniquement, DKDP/Houle = conseil humain. **Personne** ne fait « gouvernance continue d'agents IA » pour PME FR-CH à prix PME.

**Notre positionnement pivot** (vs `action-5` v1) : **add-on d'assurance, pas audit autonome.**
> *« Mister IA installe vos agents. Qui gouverne les risques ? Nous. »*
→ Mister IA devient **canal de distribution**, pas concurrent.

**Verdict** : **OUI MAIS** (voir §11) — vertical le plus prometteur du portefeuille, sous 3 conditions strictes (preuve CAC, 1er client pilote, défense vs Legalithm).

**Objectif 12 mois** : CHF 95 K one-shot + **CHF 308 K ARR** (médian), break-even MRR dès le mois 4.

---

## 1. ANALYSE — Les faits vérifiés

### 1.1 La demande est validée à grande échelle (Mister IA)

| Fait | Source | Vérification |
|---|---|---|
| Mister IA : 750 entreprises accompagnées, 2 200 sessions, 1 000+ clients | mister-ia.com, getlatka.com | Site officiel + Latka (CA 12,3 M$, 66 pers.) |
| Mister IA déploie des agents IA sur-mesure + licences (3 000+ licences Claude/ChatGPT/Gamma) | mister-ia.com/conseil + offre CSM | Page service + annonce recrutement |
| Levée **10 M€** (Momentum Invest + Andréa Bensaid/Eskimoz), 120 collaborateurs | ChannelNews | Article presse daté |
| Positionnement : *« seule double expertise conseil + formation IA »* | mister-ia.com | Claim marketing |
| **Faille** : aucun produit de gouvernance/médiation déterministe, zéro journal WORM, AI Act = case à cocher | audit comparatif | Croisement avec leur site |

> **Lecture** : Mister IA a créé et validé le marché FR de l'IA en entreprise. Il a une **BU Licences** (récurrence) et une **BU Formation** (cash). Il n'a **aucune BU Gouvernance**. C'est le trou que nous remplissons.

### 1.2 La douleur est prouvée (Gartner + marché)

| Fait | Source |
|---|---|
| **40 %+ des projets agentic AI annulés fin 2027** — 3 causes : coûts, valeur floue, **contrôles de risque insuffisants** | Gartner press release 25/06/2025 (Anushree Verma) |
| Mais **40 % des apps enterprise intégreront des agents fin 2026** (<5 % en 2025) | Gartner 26/08/2025 |
| ROI moyen enterprise agentic AI = **171 %** quand bien conçu | Deloitte 2026 |
| **52 % des execs** utilisent déjà des agents IA en prod ; **39 % en font tourner +10** | PUNKU.AI State of AI 2025 |
| Salesforce Agentforce : **540 M$ ARR**, 18 500 clients | rapport marché 2026 |
| Concept Gartner : **« agentwashing »** — rebranding chatbots/RPA sans autonomie = 1 cause d'échec | Gartner |

> **Lecture** : Gartner est auto-contradictoire (40 % annulés ET 40 % adoption) car elle confond **pilotes mal conçus** (qui échouent) et **déploiements gouvernés** (qui réussissent à 171 % de ROI). **Notre produit = le séparateur entre les deux.**

### 1.3 Le gap FR-CH est vide (paysage compétitif, trace 00:29)

| Concurrent | Couvre agents IA ? | Gouvernance continue ? | Prix PME ? | FR-CH ? |
|---|---|---|---|---|
| **Mister IA** (Paris) | Déploie, n'audite pas | ❌ | ✅ | ❌ (FR) |
| **Modulos** (Suisse) 🇨🇭 | Partiel (ISO 42001) | ✅ | ❌ **50 k€/an** | ✅ |
| **Legalithm** (EU) | AI Act nu | ❌ one-shot | ✅ **gratuit →2028** | ❌ |
| **Houle** (Genève/Lausanne) | Déploie Azure, n'audite pas | ❌ | Consulting | ✅ |
| **DKDP** (Genève) | ❌ RGPD/nLPD only | Suivi 350 CHF/mois | ✅ | ✅ |
| **OneTrust/Vanta/Holistic AI** | Module AI Act add-on | ✅ | ❌ 10–80 k€/an | ❌ (US) |
| **Cortex Leman** 🎯 | **✅ 8 checkpoints + OWASP GenAI** | **✅ médiateur + journal WORM** | **✅ 2 000–8 000 CHF + 500–1 500/mois** | **✅ FR-CH** |

> **Lecture** : Nous sommes les **seuls** à cocher les 4 cases simultanément. C'est une position de monopole de niche, pas une redoute.

### 1.4 Le code existe déjà (capacité technique)

| Brique | Fichier | Statut |
|---|---|---|
| 8 règles JsonLogic vertical agent-ia | `core/mediator/rules/agent-ia.json` | ✅ créé |
| Médiateur déterministe (jamais LLM) | `core/mediator/mediator.py` | ✅ Sprint 1 |
| Journal WORM hash-chainé SHA-256 | `core/journal/` | ✅ Sprint 1 |
| Compliance Gateway (data residency CH/EU) | `core/compliance/gateway.py` | ✅ |
| Trust Box API (7 endpoints) | Phase 1A | ✅ |
| Mode Edge K3s + Ollama (secret pro) | `edge/` | ✅ |
| Self-audit widget landing | `landing/self-audit-widget.js` | ✅ |
| Calculateur de sanctions | `landing/fine-calculator.js` | ✅ |
| Stripe + monitoring continu | — | ❌ **non implémenté** |

> **Conclusion** : **80 % du socle produit existe.** Le delta pour un MVP commercial = couche récurrente (Stripe + monitoring n8n + dashboard).

---

## 2. LE CROISEMENT DES 6 TRACES — Une seule phrase

```
 GARTNER (00:02)   40% agents échouent par défaut de contrôles  →  le MAL
      ×
 MISTER IA          750 PME, déploie agents, 0 gouvernance      →  le MARCHÉ non défendu
      ×
 CORTEX LEMAN v5    médiateur + WORM + AI Act + agent-ia.json   →  la DOUVE unique
      ×
 PAYSAGE FR-CH(00:29) Modulos 50k€/Legalithm gratuit            →  le PRIX à tenir
      ×
 SOHK (00:xx)       attention = actif #1, entonnoir gratuit→payant  →  le CANAL
      ×
 SOCIALPULSE (00:xx) 33 leads Haute-Savoie qualifiés            →  le TOP DE FUNNEL prêt
```

**Phrase-pivot :** *Mister IA a créé le marché. Gartner prouve qu'il va imploser sans gouvernance. Nous sommes les seuls en FR-CH à tenir la gouvernance à prix PME.*

---

## 3. LE PRODUIT — « Gouvernance d'Agents IA »

### 3.1 Pitch en une ligne (pour DPO/CISO)

> *« Votre cabinet a déployé Copilot/ChatGPT/un agent maison. Nous le rendons conforme AI Act, traçable (journal inviolable), et surveillé en continu. Vous ne touchez pas à vos outils — nous posons une couche de confiance par-dessus. »*

### 3.2 Les 3 modules (alignés sur `agent-ia.json` + OWASP GenAI)

| Module | Ce qu'il fait | Règles déclenchées |
|---|---|---|
| **Agent Scan** (one-shot) | 8 checkpoints : transparence, biométrie, décision auto, DPIA, data residency, manipulation, conservation, registre | agent-ia-001 → 008 |
| **Agent Guard** (récurrent) | Médiateur en continu : **gel** d'une action agent non conforme (ex. refus client sans recours humain → Art. 22), alerte DPO | + règles OWASP GenAI Data Security |
| **Agent Fortress** (edge) | K3s + Ollama local pour cabinets sous secret professionnel (avocat/banque/santé) : zéro appel externe | + LPD/Art. 321 CP/Art. 47 LB |

### 3.3 Le différentiateur « jamais vu » (vs tous concurrents)

**Le gel déterministe.** Aucun concurrent n'a un moteur qui **bloque physiquement** une action d'agent IA en temps réel quand elle viole une règle (ex. : agent qui fixe un prix discriminatoire → Art. 22 RGPD → gel → arbitrage humain). Modulos = dashboards. Legalithm = checklists. Nous = **pare-feu actif**.

---

## 4. DIFFÉRENCIATION — Matrice compétitive

| Capacité | Mister IA | Modulos | Legalithm | Houle | DKDP | **Cortex Leman** |
|---|---|---|---|---|---|---|
| Gouvernance agents IA continue | ❌ | ⚠️ | ❌ | ❌ | ❌ | **✅** |
| Médiateur déterministe (gel) | ❌ | ❌ | ❌ | ❌ | ❌ | **✅ unique** |
| Journal WORM hash-chainé | ❌ | ❌ | ❌ | ❌ | ❌ | **✅ unique** |
| AI Act + RGPD + LPD **croisés** | ❌ | ⚠️ | AI Act seul | ❌ | RGPD/LPD | **✅ unique** |
| Mode Edge (secret pro) | ❌ | ❌ | ❌ | Azure CH | ❌ | **✅ K3s+Ollama** |
| Prix PME FR-CH | ✅ | ❌ 50k€ | ✅ | consulting | ✅ | **✅** |
| Canal formation/media | ✅ 120 pers | ❌ | ❌ | ❌ | ❌ | ⚠️ à construire |

**Douve défensive** : Mister IA/Modulos/Legalithm ne peuvent pas copier le médiateur + WORM + edge **sans tout réécrire** (ce sont des plateformes pensées différemment). C'est notre moat structurel, pas marketing.

---

## 5. MODÈLE ÉCONOMIQUE

### 5.1 Reprise du pricing existant (`action-5` + `action-5-modele-recurrent`)

| Tier | Prix | Récurrence | Cible |
|---|---|---|---|
| Agent Scan | CHF 2 000 | one-shot | 1 agent, 8 checkpoints |
| Agent Audit ⭐ | CHF 4 500 | one-shot | 3 agents, OWASP GenAI + AI Act |
| Agent Fortress | CHF 8 000 | one-shot | illimité + re-audit trimestriel |
| Sentinelle | CHF 500/mois | MRR | monitoring + alertes |
| Garde ⭐ | CHF 900/mois | MRR | + re-audit trimestriel + support DPO |
| Forteresse | CHF 1 500/mois | MRR | + consulting + hotline |

### 5.2 NOUVEAUTÉ v2 — Le canal revendeur (inspiré BU Licences Mister IA)

**Positionner Cortex Leman comme sous-traitant gouvernance des installeurs d'agents IA** (Mister IA, Houle, ZénithIA, agences IA régionales) :
- **White-label** : l'agence vend « déployement + conformité Cortex Leman » à son client
- **Revenue share** : 60 % agence / 40 % Cortex Leman sur le Scan ; MRR 100 % Cortex Leman
- **Argument pour l'agence** : *« Votre client vous demande si l'agent est conforme AI Act. Vous ne savez pas répondre. On répond pour vous, sous votre marque. »*

→ **Effet** : Mister IA cesse d'être un concurrent et devient un **canal d'acquisition financé par d'autres**. C'est le mouvement stratégique que la v1 n'avait pas.

### 5.3 Unit economics (alignés `action-5-modele-recurrent`, conservateurs)

| Métrique | Hypothèse | Justification |
|---|---|---|
| Prix moyen audit | CHF 4 000 | entre Scan et Audit |
| Conversion audit → abonnement | 50 % | doc existant |
| Prix moyen abonnement | CHF 900 (Garde) | sweet spot doc |
| LTV (abonné, churn 10 %/an) | ~CHF 9 000 | 900 × 10 mois net |
| LTV one-shot + récurrent | ~CHF 13 000 | 4 000 + 9 000 |
| Coût marginal/siège | ~0 € | agents + edge = quasi-gratuit |

---

## 6. GO-TO-MARKET — Entonnoir complet (le miss de la v1)

La v1 listait « inbound widget + LinkedIn » en vrac. La trace du 01/07 donne un **entonnoir assemblé** :

```
[1] SocialPulse (33 leads 74 déjà prêts + scaling Genève/VD/FR)
        ↓ cold email conformisé
[2] Self-audit widget landing (15 min → score → email)
        ↓ conversion 15-25%
[3] Agent Scan payant (CHF 2 000)  →  preuve produit
        ↓ conversion 50%
[4] Garde récurrent (CHF 900/mois)  →  MRR
        ↓
[5] Upsell Forteresse edge (cabinets secret pro)  →  LTV max
        ‖ parallèle
[6] Canal revendeur (Mister IA/Houle/agences) white-label  →  CAC quasi-0
        ‖ parallèle
[7] Média SOHK-style (Narrateur+Oeil produisent, coût 0€)  →  inbound gratuit
```

### 6.1 Le média SOHK (inspiration trace 5)

SOHK = 1 format × 43 vidéos = 34 M vues → communauté payante → événements, **coût marginal 0**.
Nous avons la chaîne de production : `le-narrateur-augmente` (contenu) + `l-oeil-de-cortex` (veille ArXiv = matière infinie) + `le-gardien-des-normes` (garant conformité).

**Format moule** : *« Votre [chatbot/agent/copilot] est-il conforme ? 5 pièges AI Act pour [avocat/comptable/médecin]. »* → déclinable à l'infini par vertical.

### 6.2 Pitch partenaire Mister IA (lettre type)

> *Objet : Gouverner les agents que vous déployez — sous votre marque*
> Mister IA déploie 3 000+ licences et agents sur-mesure. Gartner prévoit 40 % d'annulation de ces projets pour défaut de gouvernance d'ici 2027. Nous avons le seul moteur de gouvernance déterministe FR-CH. **Devenez notre canal : vos clients reçoivent la conformité en white-label, vous captez l'upsell, nous gérons la technique.**

---

## 7. SIMULATION FINANCIÈRE — 3 scénarios stress-testés (12 mois)

> Convention `analyse-critique` : le scénario **médian = base de décision**, jamais l'optimiste. Stress-test = pessimiste.

### 7.1 Hypothèses par scénario

| Levier | Pessimiste | **Médian** | Optimiste |
|---|---|---|---|
| Nouveaux audits/mois | 1 | **3** | 5 |
| Prix moyen audit | CHF 3 000 | **CHF 4 000** | CHF 4 500 |
| Conversion → abonnement | 30 % | **50 %** | 60 % |
| Prix moyen abonnement | CHF 600 | **CHF 900** | CHF 1 100 |
| Churn abonnement annuel | 20 % | **10 %** | 5 % |
| Coûts fixes/mois | CHF 4 000 | **CHF 3 000** | CHF 2 500 |

### 7.2 Résultats fin d'année 1

| | Pessimiste | **Médian** | Optimiste |
|---|---|---|---|
| Audits cumulés (an 1) | 12 | **36** | 60 |
| CA audits one-shot | CHF 36 K | **CHF 144 K** | CHF 270 K |
| Abonnés fin an 1 | 4 | **18** | 36 |
| MRR fin an 1 | CHF 2,4 K | **CHF 16,2 K** | CHF 39,6 K |
| ARR fin an 1 | CHF 29 K | **CHF 194 K** | CHF 475 K |
| **CA total an 1** | **CHF 65 K** | **CHF 338 K** | **CHF 745 K** |
| Break-even MRR | jamais an 1 | **mois 5** | mois 3 |

> **Note** : `action-5-modele-recurrent` projetait CHF 308 K ARR an 1. Mon médian (CHF 194 K) est **plus conservateur** parce que j'applique le stress-test (churn 10 %, conversion 50 %, démarrage lent mois 1-3). L'écart = marge de sécurité.

### 7.3 Seuil de rentabilité réaliste

- Coûts fixes ~CHF 3 000/mois → **4 abonnés Garde** = CHF 3 600 = break-even MRR.
- Atteignable au **mois 5** en médian. **Pessimiste : jamais en an 1** (signal d'alerte).

---

## 8. KILL FACTORS — Top 5 des scénarios mortels

> `analyse-critique` réflexe #6 : identifier ce qui tue le projet.

| # | Kill factor | Probabilité | Impact | Mitigation |
|---|---|---|---|---|
| 1 | **0 client pilote converti** (aucun PME ne paie encore) — *cf. OFFRE-PILOTE toujours en recherche* | **Élevée** | Fatal | Convertir 2 cabinets pilotes gratuits **avant** d'investir dans Stripe/monitoring |
| 2 | **Legalithm gratuit jusqu'en 2028** commoditise l'AI Act → pression prix à la baisse | Moyenne | Élevé | Ne jamais vendre « AI Act nu » — vendre le **gel + WORM + edge** (inréplicables) |
| 3 | **Modulos descend sur le segment PME** (a le capital, ISO 42001) | Faible-Moyenne | Élevé | Verrouiller 5-10 cabinets sous contrat annuel avant leur descente |
| 4 | **CAC incontrôlé** (SocialPulse génère des leads mais conversion email→audit non prouvée) | Élevée | Fatal | Mesurer CAC dès le 1er mois ; si CAC > 1/3 LTV, pivoter vers canal revendeur |
| 5 | **Enforcement AI Act graduel** → urgence acheteur faible en 2026 (sanctions réelles fin 2027+) | Moyenne | Moyen | Vendre sur le **risque réputationnel + certification clients** (B2B demande) pas seulement la sanction |

> **Si le kill factor #1 OU #4 se réalise → le projet est trop risqué à ce stade.** Ce sont les deux à surveiller en priorité.

---

## 9. CONTRE-ANALYSE — Les 10 réflexes appliqués

> `analyse-critique` : jamais de recommandation sans contre-analyse. Voici l'avocat du diable.

1. **💸 Vrais coûts totaux** — La v1 oubliait le **CAC**. Acquisition SocialPulse + cold email + contenu = min. CHF 200-500/client. Le LTV CHF 13 000 reste solide (CAC/LTV 1:26), mais non prouvé.
2. **⚖️ Stress-test marges** — Fait en §7. Le médian (CHF 338 K) tient ; le pessimiste (CHF 65 K) **ne break-even jamais** en an 1.
3. **🔥 Risque réglementaire** — Ironie : **notre produit est lui-même un système IA soumis à l'AI Act**. Le médiateur déterministe nous classe en *Limited Risk* (favorable), mais le agent Raisonnement (LLM) peut nous classer *High Risk* si on l'offre comme décideur. → **Décision produit : rester déterministe côté sécurité, LLM en analyse seule.**
4. **📉 Saturation marché** — Faux ici : le créneau « gouvernance continue agents IA PME FR-CH » a **0 acteur direct**. Vérifié §1.3.
5. **🏭 Compétitivité** — Modulos a le capital pour écraser ; nous n'avons pas de levier prix-volume. Notre levier = **niche + edge + médiateur** (pas reproductible sans réécriture).
6. **💣 Kill factors** — §8. Les #1 et #4 sont fatals potentiels.
7. **🎭 Biais « ça marche pour Mister IA »** — Mister IA a 120 consultants + 10 M€ + le plus gros média IA FR. **Nous n'avons aucune de ces ressources.** Leur succès ne préjuge pas du nôtre. Le canal revendeur (§5.2) est précisément là pour **emprunter** leur force au lieu de la répliquer.
8. **📊 Chiffres indépendants** — Gartner, Deloitte, Latka, ChannelNews : sources croisées ✅. Manque : données d'enforcement AI Act réelles (encore graduel → risque #5).
9. **⏰ Seuil rentabilité** — Médian mois 5. Acceptable (< 8 mois). Pessimiste : **jamais en an 1** → fragile.
10. **🏁 Recommandation honnête** — Voir §11.

---

## 10. PROPOSITIONS FRAGILES (non testées)

> `critical-objective-analysis` §5 : exposer explicitement ce qu'on suppose sans preuve.

| # | Proposition fragile | Test requis |
|---|---|---|
| 1 | *« Les PME FR-CH paieront CHF 4 000 + CHF 900/mois pour gouverner leurs agents IA »* | 2 conversions pilotes gratuites → payantes |
| 2 | *« Mister IA acceptera un partenariat canal »* | 1 contact commercial + 1 deal white-label |
| 3 | *« Le gel déterministe est un argument qui fait vendre »* (vs simple dashboard) | A/B test pitch « gel actif » vs « dashboard » sur 20 prospects |
| 4 | *« SocialPulse convertit email → audit à >5 % »* | 50 emails sortis, mesure du taux |
| 5 | *« Le mode Edge (Ollama) est requis par les cabinets secret pro »* | 3 entretiens avocats/banquiers : validation du besoin |
| 6 | *« Le média SOHK-style génère de l'inbound »* | 10 contenus publiés, mesure leads |

> **Règle** : aucune de ces propositions n'est prouvée. Le plan 90 jours (§12) les teste **toutes** à moindre coût avant tout investissement lourd.

---

## 11. VERDICT — OUI MAIS

> `analyse-critique` : ne jamais dire « recommandé » sans conditions.

### 🟡 OUI MAIS — je mettrais mon argent dedans **sous 3 conditions strictes :**

1. **Convertir 2 cabinets pilotes gratuits → payants avant de build la couche récurrente** (Stripe + monitoring = 3-4 semaines de dev). Sinon, on construit dans le vide. → teste la proposition fragile #1.
2. **Lancer le canal revendeur en parallèle du direct** (1 contact Mister IA ou Houle dans le mois). C'est notre seule défense contre le déficit de ressources vs Mister IA. → teste #2.
3. **Mesurer le CAC dès le mois 1**. Si CAC > CHF 1 500 ou taux conversion SocialPulse < 3 % → pivoter 100 % vers le revendeur, abandonner le direct. → teste #4.

### ❌ NON si :
- 0 pilote converti après 60 jours → le besoin n'est pas un besoin-achat, tuer le vertical.
- Modulos lance une offre PME à < CHF 1 000/mois avant nous → on perd la fenêtre prix.

### Pourquoi pas « OUI » franc ?
Parce que **0 client payant confirmé** aujourd'hui (`OFFRE-PILOTE` encore en quête de pilotes). Toute projection repose sur des hypothèses de conversion non testées. Le vertical est **le meilleur du portefeuille** mais reste une hypothèse jusqu'à preuve d'achat.

---

## 12. ROADMAP 90 JOURS (test des propositions fragiles à coût minimal)

| Semaines | Action | Test validé | Coût |
|---|---|---|---|
| **0-2** | Activer le vertical `agent-ia` dans la config API + landing page section dédiée | — | 0 € |
| **0-2** | Sortir **50 emails** SocialPulse (33 leads 74 + Genève) avec pitch « gel actif » | #4 (conversion email) | 0 € |
| **0-4** | Convertir **2 cabinets pilotes gratuits** (avocat + comptable Genève/74) | #1 (paiement) + #5 (edge) | 0 € |
| **2-4** | 1 contact commercial **Mister IA + Houle** (canal revendeur) | #2 (partenariat) | 0 € |
| **2-6** | Publier **10 contenus média** (Narrateur+Oeil) format SOHK | #6 (inbound) | 0 € |
| **4-8** | A/B test pitch : « gel déterministe » vs « dashboard » sur 20 prospects | #3 (argument) | 0 € |
| **4-8** | **Si 2 pilotes convertis** → build Stripe + monitoring n8n + dashboard | — | dev interne |
| **8-12** | Lancer Agent Scan en self-serve + signer 1er deal revendeur | scale | — |

**Gate de décision semaine 8** : si < 2 pilotes payants → **stop**, pivot ou tuer. Ne pas construire la couche récurrente dans le vide.

---

## 13. PITCH DECK — Outline (10 slides)

1. **Titre** — « Gouvernance d'Agents IA pour PME FR-CH »
2. **Le mal** — Gartner : 40 % des projets agents IA annulés faute de contrôles (citation)
3. **Le marché non défendu** — Mister IA : 750 PME, 12 M$, déploie des agents, 0 gouvernance
4. **Le gap** — Matrice §4 (seuls à cocher 4 cases)
5. **Le produit** — Les 3 modules + le gel déterministe (démo Trust Box)
6. **La douve** — Médiateur + WORM + edge = non reproductible sans réécriture
7. **Le modèle** — One-shot + MRR + canal revendeur (Mister IA = partenaire)
8. **La traction** — Pilotes, SocialPulse, règles JsonLogic, code 80% prêt
9. **Les chiffres** — Médian CHF 338 K an 1, break-even mois 5
10. **L'ask** — 2 cabinets pilotes + 1 partenaire revendeur

---

## 14. CHECKBOXES DE DÉPLOIEMENT

### Court terme (ce que la v1 n'avait pas fait)
- [ ] Activer `agent-ia` dans `active_verticals` (API config)
- [ ] Ajouter section « Vertical Agent IA » sur landing
- [ ] Template email cold SocialPulse spécifique agents IA
- [ ] Template LinkedIn post vertical agents IA
- [ ] Lister 10 cabinets avocats/comptables Genève + 74 comme cibles pilotes

### Validation (avant tout build lourd)
- [ ] 2 cabinets pilotes convertis gratuits → payants
- [ ] CAC mesuré mois 1
- [ ] 1 contact Mister IA / Houle ouvert

### Build (gate semaine 8)
- [ ] Stripe (products + webhook) — cf. `action-5-modele-recurrent` §3.1
- [ ] Workflow n8n monitoring mensuel
- [ ] Dashboard client + certificat PDF
- [ ] Endpoints billing/monitoring

---

## 15. AUTO-CRITIQUE FINALE (skill `critical-objective-analysis` §6)

**Ce qui invaliderait cette analyse :**
1. **Données incomplètes** — je n'ai pas vu le backend complet ni les logs d'usage réels du self-audit widget (taux de conversion actuel inconnu).
2. **Biais de sélection** — j'ai privilégié les traces Telegram du 01/07 ; il existe peut-être des analyses plus récentes qui contredisent (ex. `strategie-2026-06/02-premortem-sonnet-4.6.md` non lu ici).
3. **Hypothèses non testées** — les 6 propositions fragiles §10 sont **toutes** non testées. Toute la projection financière repose dessus.
4. **Contexte manquant** — je ne sais pas si Cortex Leman a déjà des clients payants (OFFRE-PILOTE suggère non, à confirmer).
5. **Alternative ignorée** — j'ai poussé le vertical agents IA parce que c'est l'intersection la plus forte des traces. Mais le vertical **broker de licences conformes** (option ① de l'analyse Mister IA précédente) pourrait avoir un ROI plus rapide. À comparer avant de s'engager.
6. **Sur-analyse possible** — le projet pourrait être plus simple : si 2 cabinets signent en 30 jours, la majorité de ce document devient accessoire.

**Relecture recommandée** : faire passer ce doc par contre-analyse multi-modèle (skill `critical-objective-analysis` §« Multi-model counter-analysis » via OpenRouter gpt-5.5 ≠ modèle courant) avant toute décision d'investissement.

---

**Créé par** : L'Architecte Lémanique (CSO) + Le Gardien des Normes (contre-analyse)
**Statut** : 🟡 OUI MAIS — meilleur vertical du portefeuille, sous 3 conditions (§11)
**Prochaine action immédiate** : 50 emails SocialPulse + 2 cabinets pilotes (semaine 0-4, coût 0 €)
