# Prospect : swiss-premium-insurance.ch

> Analyse stratégique et propositions de solutions Cortex Leman v5  
> Date : 30 avril 2026  
> Classification : Confidentiel — usage interne

---

## 1. Profil du prospect

### 1.1 Identification

**Domaine :** `swiss-premium-insurance.ch`  
**Secteur :** Assurance suisse (vie + non-vie)  
**Régulation principale :** FINMA, ISA/LCA, LBA, nLPD, LPM  
**Juridiction :** Suisse (périmètre principal), éventuels risques transfrontaliers FR-CH

### 1.2 Contraintes réglementaires clés

| Réglementation | Impact IA | Sévérité |
|----------------|-----------|----------|
| **FINMA** | Solvabilité SST, gouvernance, auditabilité des processus IA | Critical |
| **ISA/LCA** | Devoir de conseil, transparence, préavis résiliation | High |
| **LPM** | Données médicales collectées en assurance → secret médical Art. 321 CP | Critical |
| **LBA** | KYC/AML pour assurance vie, primes ≥ 15K CHF | Critical |
| **nLPD** | Minimisation données, droit d'accès, notification 72h | High |
| **AI Act (UE)** | Si opérations EU → classification high-risk | Medium |
| **Secret professionnel assurance** | Art. 321bis CP — personnel d'assurance soumis au secret | Critical |

### 1.3 Spécificité assurance suisse

L'assurance suisse a une particularité unique par rapport aux autres verticales existantes : **elle combine les contraintes de 3 domaines régulés simultanément** :

1. **Secret bancaire** (pour l'assurance vie / produits d'investissement)
2. **Secret médical** (pour les questionnaires de santé et expertises)
3. **Secret professionnel assurance** (Art. 321bis CP — spécifique au secteur)

C'est le cas d'usage le plus exigeant de Cortex Leman.

---

## 2. Diagnostic des besoins

### 2.1 Processus métier candidats à l'IA de confiance

| Processus | Volume typique | Risque réglementaire | Automatisable ? |
|-----------|---------------|---------------------|-----------------|
| **Souscription** (analyse risque, tarification) | 500-5000/jour | High (LBA KYC, données santé) | Partiel (gel dégradé) |
| **Gestion sinistres** (analyse, classification, provision) | 200-2000/jour | Critical (données santé, montants) | Partiel (arbitrage humain) |
| **Expertise médicale** (questionnaires, rapports) | 50-500/jour | Critical (LPM, Art. 321 CP) | Minimal (air-gap obligatoire) |
| **Conformité LBA/AML** (KYC, signalement MROS) | 100-1000/jour | Critical (LBA, pénal) | Partiel (règles + validation) |
| **Résiliation** (vérification préavis, motifs) | 100-500/jour | Medium (ISA Art. 39-41) | Fortement automatisable |
| **Communication client** (polices, avenants) | 1000-5000/jour | Medium (transparence) | Partiel |
| **Reporting FINMA** (SST, ORSA, solvabilité) | Mensuel/Trimestriel | High (exactitude) | Partiel (données + validation) |

### 2.2 Points de douleur identifiés

1. **Volume de souscriptions** → les assureurs traitent des milliers de dossiers/jour, le gel complet tue la productivité
2. **Données médicales partout** → questionnaires santé, expertises, sinistres corporels → LPM + Art. 321 CP
3. **LBA pour l'assurance vie** → KYC obligatoire, délais serrés
4. **Audit FINMA** → traçabilité complète exigée, tout doit être prouvable
5. **Secret professionnel spécifique** → Art. 321bis CP, pas juste RGPD

---

## 3. Solutions proposées

### Solution 1 : Graphe de Confiance Assurance — Mode Haute Protection

**Le produit phare pour ce prospect.**

```
┌─────────────────────────────────────────────────────────┐
│              APPLIANCE K3s — DATA CENTER ZURICH         │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ Souscrip-│  │ Sinistres│  │ Expertise│  │LBA/AML  │ │
│  │ tion     │  │          │  │ Médicale │  │         │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬────┘ │
│       │              │              │              │      │
│  ┌────▼──────────────▼──────────────▼──────────────▼────┐ │
│  │              ORCHESTRATEUR                            │ │
│  │     Hub conversationnel permanent                    │ │
│  └────────────────────┬────────────────────────────────┘ │
│                       │                                   │
│  ┌────────────────────▼────────────────────────────────┐ │
│  │              NATS JETSTREAM (33 sujets)              │ │
│  └───┬──────────┬──────────┬──────────┬────────────────┘ │
│      │          │          │          │                    │
│  ┌───▼───┐ ┌───▼───┐ ┌───▼───┐ ┌───▼────┐              │
│  │ DATA  │ │RAISONN │ │ACTION │ │MÉDIAT. │              │
│  │       │ │EMENT   │ │(auto) │ │22 règl.│              │
│  └───┬───┘ └───┬───┘ └───┬───┘ └───┬────┘              │
│      │         │         │         │                     │
│  ┌───▼─────────▼─────────▼─────────▼──────────────────┐ │
│  │          JOURNAL WORM (SHA-256 + HMAC)              │ │
│  │          + Horodatage SwissSign ZertES              │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌──────────────────────────────────────────────────────┐│
│  │          OLLAMA (Mistral 7B — 100% LOCAL)           ││
│  │          AUCUNE donnée ne sort de l'appliance       ││
│  └──────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

**Pourquoi c'est la bonne solution :**
- Mode Haute Protection = air-gap complet → secret professionnel garanti
- Ollama local → AUCUNE donnée client ne transite par un cloud
- Journal WORM → audit FINMA facilité
- Médiateur déterministe → l'auditeur peut vérifier chaque règle ligne à ligne
- Arbitrage humain → le souscripteur/expert reste décisionnaire

### Solution 2 : Mode Dégradé Conforme pour Souscription

**Le gain de productivité pour le prospect.**

Le processus de souscription est le plus sensible en volume. Avec le gel dégradé :

| Phase | Agents | Statut | Impact |
|-------|--------|--------|--------|
| Analyse risque | Data + Raisonnement | **Actifs** | Enrichissent le dossier en continu |
| Vérification KYC | Data | **Actif** | Continue la vérification même si montant ≥ 100K |
| Tarification | Raisonnement | **Actif** | Peut affiner la proposition |
| Validation / Exécution | Action | **Bloqué** | Aucune police émise sans validation |
| Arbitrage expert | Humain | **Décision** | Dossier enrichi → meilleure décision |

**Gain estimé :** 30-50% de temps gagné sur les souscriptions complexes (montant élevé ou données médicales) car l'expert humain reçoit un dossier pré-analysé au lieu de devoir tout reprendre à zéro.

### Solution 3 : Conformité LBA/AML Automatisée

Le Médiateur avec 8 règles spécifiques assurance :

| Règle | Seuil | Action | Référence |
|-------|-------|--------|-----------|
| Données santé hors CH | Tout montant | **Block** | LPM + Art. 321 CP |
| LLM externe pour données sinistres | Tout | **Block** | Secret professionnel |
| Infrastructure hors CH | Tout | **Block** | FINMA |
| Sinistre ≥ 50K CHF | 50 000 | Arbitrage | Contrôle interne |
| Capital assuré ≥ 100K CHF | 100 000 | Arbitrage | LBA/KYC renforcé |
| Transaction ≥ 15K sans KYC | 15 000 | **Block** | LBA Art. 9 |
| Transfert données hors CH | Tout | **Block** | nLPD + FINMA |
| Résiliation police | Tout | Arbitrage | ISA Art. 39-41 |

### Solution 4 : Reporting FINMA Automatisé

- Journal WORM → extraction automatique des métriques SST/ORSA
- Compliance Gateway → rapports quotidiens et mensuels
- Dashboard 6 sections → vue temps réel pour le compliance officer
- Endpoint `GET /api/v1/compliance/report/monthly` → rapport mensuel pré-formaté

### Solution 5 : Knowledge Vault Assurance

- 5 documents réglementaires seedés (ISA, FINMA, LPM, LBA, nLPD)
- RAG ChromaDB vectoriel pour recherche sémantique dans les circulaires
- Mise à jour continue via n8n workflows (ingestion circ. FINMA, ATF, etc.)
- Isolation par produit d'assurance (vie, non-vie, santé, RC)

---

## 4. Architecture de déploiement recommandée

### Option A : Appliance On-Premise (recommandé)

```
┌─────────────────────────────────────────┐
│   3 serveurs K3s — Data Center Zürich   │
│                                          │
│  Master: API + Orchestrateur + Médiateur │
│  Worker 1: Ollama (GPU) + RAG           │
│  Worker 2: NATS + Redis + PostgreSQL    │
│                                          │
│  Sécurité:                               │
│  ✓ iptables: zero trafic sortant        │
│  ✓ mTLS entre tous les nœuds            │
│  ✓ SwissSign TSA local (appliance)      │
│  ✓ Fernet at-rest                       │
│  ✓ Journal WORM persistant              │
└─────────────────────────────────────────┘
```

**Budget estimé :** 3 appliances ~15K CHF + appliance SwissSign ~5K CHF = ~20K CHF infrastructure

### Option B : Private Cloud Suisse (alternative)

```
┌─────────────────────────────────────────┐
│   Exoscale / Infomaniak / Swisscom      │
│   Data residency: CH exclusivement      │
│                                          │
│  K3s cluster managed                    │
│  Ollama sur instances GPU               │
│  PostgreSQL managed                     │
│  Backup: Swiss jurisdiction only        │
└─────────────────────────────────────────┘
```

**Budget estimé :** ~2-3K CHF/mois

### Option C : Hybride (futur)

- Production: appliance on-premise
- DR/BCP: private cloud suisse pour reprise

---

## 5. Scénarios d'utilisation concrets

### Scénario 1 : Souscription police vie avec questionnaire santé

```
1. Client remplit questionnaire santé en ligne
2. Agent Data: extrait données médicales → GEL IMMÉDIAT (règle assu-001)
   - Mode: DEGRADED (Data peut continuer à chercher des antécédents)
   - Action: BLOQUÉE (aucune police émise)
3. Agent Raisonnement: analyse le risque avec les données médicales
4. Médiateur: vérifie LBA KYC si capital ≥ 100K (règle assu-005)
5. Arbitrage: le souscripteur valide avec le dossier enrichi
6. Journal WORM: toute la chaîne est tracée (audit FINMA)
7. Dégel + émission de la police
```

**Sans Cortex Leman :** Le souscripteur doit manuellement vérifier KYC, questionnaires santé, montants. Temps: 2-4h par dossier complexe.

**Avec Cortex Leman :** Le souscripteur reçoit un dossier pré-analysé, enrichi, avec alertes réglementaires. Temps: 15-30 min.

### Scénario 2 : Sinistre corporel 80K CHF

```
1. Déclaration sinistre: accident corporel, 80K CHF
2. Agent Data: rechercher precedents, jurisprudence ATF
3. Agent Raisonnement: analyser couverture, exclusion, subrogation
4. Médiateur: sinistre ≥ 50K → arbitrage (règle assu-004)
5. Mode DEGRADED: Data continue à chercher des precedents
6. Arbitrage: le gestionnaire sinistres valide avec dossier complet
7. Provision constituée, paiement autorisé
8. Journal WORM: traçabilité complète pour audit FINMA
```

### Scénario 3 : Détection anti-blanchiment

```
1. Prime unique 50K CHF sur police vie
2. KYC non vérifié dans le système
3. Médiateur: règle assu-006 → BLOCK immédiat
4. Alerte compliance officer + signalement MROS
5. Aucune donnée envoyée à un LLM externe (règle assu-002)
6. Journal WORM: preuve de la détection pour audit LBA
```

---

## 6. Nouvelle verticale : Assurance (proposition)

### 6.1 Seuils de gel recommandés

| Verticale | Seuil montant | Gel par type | Mode requis |
|-----------|-------------|-------------|-------------|
| Assurance | 50 000 CHF (sinistres) | Oui (données santé, LBA) | Haute Protection |
| Assurance vie | 15 000 CHF (KYC) | Oui (données financières) | Haute Protection |
| Assurance santé | 0 (tout montant) | Données médicales uniquement | Haute Protection |

### 6.2 Règles JsonLogic proposées

8 règles dans `docs/prospects/rules-assurance.json` :

| ID | Nom | Sévérité | Action |
|----|-----|----------|--------|
| assu-001 | Données santé hors CH | Critical | Block |
| assu-002 | LLM externe données sinistres | Critical | Block |
| assu-003 | Infrastructure CH | Critical | Block |
| assu-004 | Sinistre ≥ 50K | High | Arbitrate |
| assu-005 | Capital assuré ≥ 100K | High | Arbitrate |
| assu-006 | Anti-blanchiment ≥ 15K sans KYC | Critical | Block |
| assu-007 | Transfert données hors CH | Critical | Block |
| assu-008 | Résiliation police | Medium | Arbitrate |

### 6.3 Documents réglementaires

5 documents seedés dans `docs/prospects/vault-assurance.json` :
1. ISA/LCA — contrat d'assurance
2. FINMA — surveillance des assurances
3. LPM — données médicales en assurance
4. LBA — anti-blanchiment assurance
5. nLPD — protection des données

---

## 7. Arguments commerciaux

### 7.1 Différenciateurs Cortex Leman vs concurrence

| Critère | Cortex Leman v5 | IA générique (ChatGPT, etc.) | GRC traditionnel |
|---------|-----------------|------------------------------|------------------|
| Data residency CH | ✅ Natif (mode Haute Protection) | ❌ Cloud US/EU | ✅ On-premise |
| Secret professionnel | ✅ Art. 321/321bis CP intégré | ❌ Aucune garantie | ⚠️ Processus manuel |
| Auditabilité FINMA | ✅ Journal WORM + horodatage ZertES | ❌ Boîte noire | ✅ Logs basiques |
| Gel préventif | ✅ Mode dégradé (productivité) | ❌ Pas applicable | ❌ Tout ou rien |
| Arbitrage humain | ✅ Structuré avec précédents | ❌ L'IA décide | ✅ Manuel |
| Traçabilité | ✅ SHA-256 chainé + HMAC | ❌ Aucune | ⚠️ Partielle |
| LBA/AML intégré | ✅ Règles JsonLogic automatiques | ❌ Pas applicable | ⚠️ Alertes basiques |

### 7.2 ROI estimé

| Métrique | Avant | Après Cortex Leman | Gain |
|----------|-------|--------------------|------|
| Temps souscription complexe | 2-4h | 15-30 min | **-85%** |
| Faux positifs conformité | 30-40% | <5% (seuils par type) | **-85%** |
| Délai audit FINMA | 2-3 semaines | 2-3 jours | **-80%** |
| Signalement MROS manqué | Risque pénal | Détection automatique | **100%** |
| Coût conformité annuel | ~500K CHF (effectif) | ~200K CHF (automatisé) | **-60%** |

### 7.3 Argument de confiance pour le prospect

> "Cortex Leman v5 est le seul système d'IA de confiance qui garantit que **zéro donnée patient/client ne quitte votre infrastructure**. Notre Médiateur est 100% déterministe — l'auditeur FINMA peut vérifier chaque décision ligne à ligne. Notre journal WORM est horodaté SwissSign ZertES — il constitue une preuve juridique opposable."

---

## 8. Plan de déploiement proposé

### Phase 1 : Proof of Value (4 semaines)

| Semaine | Action | Livrable |
|---------|--------|----------|
| S1 | Installation appliance K3s + Ollama | Infrastructure opérationnelle |
| S2 | Configuration verticale assurance + 8 règles | Médiateur fonctionnel |
| S3 | Seed Knowledge Vault + 5 docs réglementaires | RAG opérationnel |
| S4 | Test avec 50 dossiers réels (anonymisés) | Rapport Proof of Value |

### Phase 2 : Déploiement production (8 semaines)

| Phase | Action |
|-------|--------|
| Sprint 1 | Intégration SI assureur (API, base sinistres, KYC) |
| Sprint 2 | Formation équipes souscription + sinistres |
| Sprint 3 | Mise en production progressive (10% → 50% → 100%) |
| Sprint 4 | Audit FINMA préparation + documentation |

### Phase 3 : Extension (12 semaines)

| Phase | Action |
|-------|--------|
| Sprint 5 | Assurance vie + LBA/AML complet |
| Sprint 6 | Reporting FINMA automatisé (SST/ORSA) |
| Sprint 7 | n8n workflows d'ingestion réglementaire |
| Sprint 8 | Dashboard exécutif |

---

## 9. Checklist de conformité prospect

### Points à vérifier avec le prospect

- [ ] Type de licence FINMA (vie, non-vie, les deux)
- [ ] Volume de souscriptions / jour
- [ ] Volume de sinistres / jour
- [ ] Infrastructure actuelle (on-premise, cloud, hybride)
- [ ] Fournisseur KYC/AML actuel
- [ ] Dernier audit FINMA — observations
- [ ] Procédure MROS actuelle
- [ ] Questionnaire santé — flux actuel
- [ ] Budget conformité annuel
- [ ] Équipe compliance — taille et formation
- [ ] SI existant — API disponibles
- [ ] Politique data residency actuelle

### Questions sensibles à poser

1. "Comment traitez-vous les questionnaires santé aujourd'hui ? Où sont stockées les données ?"
2. "Quel est votre taux de faux positifs sur les alertes LBA ?"
3. "Combien de temps préparez-vous un dossier pour un audit FINMA ?"
4. "Avez-vous déjà eu un signalement MROS manqué ?"
5. "Comment garantissez-vous que les données clients ne partent pas dans un cloud IA ?"

---

*Document confidentiel — Cortex Leman v5*  
*Prospect: swiss-premium-insurance.ch — 30 avril 2026*
