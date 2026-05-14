# ACTION 5 — Vertical "AI Agent Compliance" (Fournisseurs d'Agents IA)

## Pourquoi ce vertical

1mind (Series A $30M, 60+ clients, Amanda Caholo ex-6sense) déploie des "Superhumans" — des agents IA qui remplacent les équipes de vente.

**Problème :** Personne n'audit la conformité de ces agents.

C'est un **marché vierge** au croisement de l'IA et du RGPD. Exactement là où Cortex Leman se positionne.

---

## Le marché

### Qui déploie des agents IA en 2026 ?

| Catégorie | Exemples | Taille marché |
|-----------|----------|---------------|
| **Sales AI** | 1mind, Drift, Conversica, Regie.ai | ~$2B |
| **Support AI** | Decagon, Sierra, Intercom AI | ~$5B |
| **Clone IA** | Synthesia, HeyGen, D-ID | ~$1B |
| **Chatbot e-commerce** | Gorgias, Zigpoll, Tidio AI | ~$3B |
| **Internal agents** | Mouvement massif toutes entreprises | ~$10B+ |

**Tous** sont soumis à RGPD, AI Act, LPerD. **Aucun** n'a d'audit de conformité dédié.

### Les risques spécifiques

1. **Transparence** (AI Act Art. 52) — L'utilisateur doit savoir qu'il parle à une IA
2. **Biométrie** (RGPD Art. 9) — Les clones visage/voix = données sensibles
3. **Manipulation** (AI Act Art. 5) — Pas de techniques manipulatoires
4. **Décision automatisée** (RGPD Art. 22) — Droit à intervention humaine
5. **Data residency** (RGPD Chap. V, LPerD) — Où vont les conversations ?
6. **DPIA** (RGPD Art. 35) — AIPD obligatoire pour les traitements à risque
7. **Profiling** (RGPD Art. 21) — Le scoring IA sans consentement
8. **Conservation** (RGPD Art. 5(1)(e)) — Durée de conservation des conversations

---

## Offre dédiée

### Audit "AI Agent Compliance" — 3 formules

| Formule | Prix | Ce qui est audité | Délai |
|---------|------|-------------------|-------|
| **Agent Scan** | CHF 2,000 | 1 agent IA, 8 checkpoints | 1 semaine |
| **Agent Audit** ⭐ | CHF 4,500 | Jusqu'à 3 agents, OWASP GenAI + AI Act complet | 2 semaines |
| **Agent Fortress** | CHF 8,000 | Illimité, + re-audit trimestriel + hotline | 3 semaines |

### Les 8 checkpoints de l'Agent Scan

1. **Transparence IA** — L'agent s'identifie-t-il comme IA ?
2. **Consentement données** — Les données collectées sont-elles consenties ?
3. **Biométrie** — Y a-t-il du clonage visage/voix ? Consentement ?
4. **Data residency** — Les conversations sont-elles en EU/CH ?
5. **Décision automatisée** — Y a-t-il un recours humain ?
6. **DPIA** — Une AIPD a-t-elle été réalisée ?
7. **Conservation** — Les conversations sont-elles effaçables (Art. 17) ?
8. **Manipulation** — L'agent utilise-t-il des techniques interdites ?

### Audit complet OWASP GenAI (Agent Audit +)

En plus des 8 checkpoints :
- OWASP GenAI Agentic AI (9 phases : Scope → Govern)
- OWASP GenAI Data Security (12 menaces)
- OWASP Top 10 + ASVS v4.0
- Mapping AI Act Articles 9-16
- Mapping LPerD (si Suisse)
- AIPD draft auto-généré
- Plan d'action priorisé

---

## Persona cible

### Primaire : DPO/CISO d'entreprises avec agents IA déployés
- **Douleur :** "J'ai un chatbot IA sur le site mais personne ne l'a audité"
- **Budget :** Déjà alloué (poste conformité)
- **Décision :** Rapide (obligation légale)

### Secondaire : Fournisseurs d'agents IA (type 1mind, agences IA)
- **Douleur :** "Mes clients me demandent si mon agent est conforme"
- **Budget :** Intégré au contrat client
- **Décision :** Driven by customer demand

### Tertiaire : Avocats/conseillers juridiques
- **Douleur :** "Mes clients utilisent l'IA, je dois les conseiller"
- **Budget :** Refacturé au client
- **Décision :** Recommandation professionnelle

---

## Acquisition

### 1. Inbound : Self-audit widget
Le widget de diagnostic sur cortexleman.ch génère des leads qualifiés automatiquement.
- 10 questions → score de risque → email avec recommandation
- Conversion attendue : 15-25% des visiteurs complètent le test

### 2. LinkedIn : Contenu "AI Agent Compliance"
Posts réguliers sur les risques spécifiques des agents IA :
- "Votre chatbot est-il conforme RGPD?" (viral potentiel)
- "1mind, Drift, Intercom : qui audit leur conformité?"
- "AI Act : 5 obligations pour les chatbots IA"

### 3. Partenariats avec agences IA
Les agences qui déploient des agents IA (ZénithIA, etc.) ont besoin de certifier leurs déploiements. Co-branding possible : "Audit de conformité par Cortex Leman" inclus dans le contrat.

### 4. Conférences tech FR-CH
Présenter "OWASP GenAI for AI Agents" aux meetups tech romands.

---

## Règles de médiation (déjà créées)

Le fichier `core/mediator/rules/agent-ia.json` contient 8 règles spécifiques au vertical "fournisseur d'agents IA", couvrant :
- Transparence IA (agent-ia-001)
- Consentement biométrique (agent-ia-002)
- Décision automatisée (agent-ia-003)
- DPIA (agent-ia-004)
- Data residency (agent-ia-005)
- Manipulation comportementale (agent-ia-006)
- Conservation logs (agent-ia-007)
- Registre systèmes IA (agent-ia-008)

---

## Métriques cible (12 mois)

| Métrique | Objectif |
|----------|-----------|
| Agent Scan vendus | 20 |
| Agent Audit vendus | 10 |
| Agent Fortress vendus | 3 |
| Revenue vertical | CHF 95,000 |
| Part du CA total | ~30% |

---

## Checklist déploiement

- [x] Règles médiation agent-ia.json créées
- [x] Self-audit widget JS créé
- [x] Widget intégré dans landing page
- [x] Trust Center créé
- [x] Pitch v2 documenté
- [ ] Ajouter "Agent-IA" dans la landing page (section vertical)
- [ ] Template email spécifique vertical agent IA
- [ ] Template LinkedIn post vertical agent IA
- [ ] Ajouter le vertical dans la config API (`active_verticals`)
- [ ] Mettre à jour le fiche produit
