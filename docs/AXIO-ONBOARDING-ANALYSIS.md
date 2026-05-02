# Analyse Axio Work → Cortex Leman v5
# Inspiration Onboarding & UX

## Source
Transcript vidéo onboarding Axio Work (16 min)
Plateforme: agents IA multi-tâches pour PME/e-commerce
Pricing: free 2 semaines → $10-20/mois

---

## 1. CE QU'AXIO FAIT BIEN (à reprendre)

### A. Onboarding en 60 secondes
- Email/Google → Dashboard → Premier agent en 3 clics
- Pas de config technique, pas de terminal
- L'utilisateur voit IMMÉDIATEMENT la valeur

### B. Agents comme "membres d'équipe"
- Chaque agent a un nom, avatar, personnalité, modèle LLM
- L'utilisateur pense "j'engage quelqu'un" pas "je configure un outil"
- Conversation naturelle, pas de formulaires techniques

### C. Bibliothèque de Skills
- Skills catégorisés (e-commerce, sourcing, marketing, finance)
- "Ajouter" un skill = 1 clic sur un toggle
- Templates pré-faits pour démarrage rapide

### D. Tâches programmées (Scheduled Tasks)
- Morning briefing, suivi emails, rapports quotidiens
- Fréquence configurable (quotidien, hebdo, horaire)
- Vue centralisée de toutes les tâches actives

### E. Connecteurs intégrés
- Gmail, Instagram, Shopify, etc.
- L'agent PEUT AGIR (envoyer emails, publier posts)
- Pas seulement analyser

### F. Canaux de communication
- Chat dans l'app + Telegram + Discord
- L'utilisateur choisit SON canal préféré
- Task = message structuré, Chat = conversation libre

---

## 2. CE QU'AXIO N'A PAS (notre avantage)

### Axio = Outil générique, Cortex Leman = Infrastructure réglementée

| Aspect | Axio Work | Cortex Leman v5 |
|--------|-----------|-----------------|
| Cible | Tout le monde | Professions régulées FR-CH |
| Conformité | Aucune | RGPD, AI Act, CP 321, LB 47, LPM |
| Médiateur | Non | Oui (JsonLogic déterministe) |
| Journal | Non | WORM hash-chainé SHA-256 |
| Arbitrage humain | Non | Oui (dashboard contradictions) |
| Gel préventif | Non | Oui (montant > seuil, vertical sensible) |
| Data residency | Non | EU/CH obligatoire |
| Chiffrement | Non | Fernet at-rest |
| Audit trail | Non | Double journal (fichier + DB) |
| Mode local | Non | Oui (Ollama/K3s) |
| RAG réglementaire | Non | Oui (ChromaDB + 20 textes) |
| Guardrails | Non | PII + Topic + Output safety |
| RBAC | Non | 4 rôles (admin/expert/operator/viewer) |

---

## 3. NOTRE ONBOARDING — Vision adaptée

### Philosophie: "Votre cabinet numérique de confiance en 5 minutes"

### Phase 1: Inscription (30 secondes)
```
1. Email ou SSO (Google/Microsoft)
2. Choisir votre vertical: 
   ☐ Expert-comptable    ☐ Avvocat    ☐ Médecin
   ☐ Banquier           ☐ Startup    ☐ RH
3. Nom du cabinet/organisation
4. → Dashboard personnalisé créé
   → 7 utilisateurs démo seedés
   → Règles JsonLogic de la vertical chargées
   → Textes réglementaires vectorisés (RAG)
   → Premier "Space" créé avec widgets adaptés
```

### Phase 2: Premier contact avec l'agent (2 minutes)
```
┌─────────────────────────────────────────────────────┐
│  🤖 Bonjour ! Je suis l'assistant Cortex Leman      │
│     pour votre cabinet [nom].                        │
│                                                      │
│  En tant qu'[expert-comptable], je peux:             │
│  • Analyser des dossiers fiscaux                     │
│  • Vérifier la conformité RGPD de vos traitements    │
│  • Générer des rapports de TVA                       │
│  • Surveiller les seuils de gel préventif            │
│                                                      │
│  Que souhaitez-vous faire ?                          │
│  [Analyser un dossier]  [Vérifier conformité]        │
│  [Explorer le dashboard] [Configurer mes agents]     │
└─────────────────────────────────────────────────────┘
```

### Phase 3: Configuration agents (3 minutes)
```
Inspiré d'Axio: chaque agent est un "collègue"

┌─────────────────────────────────────────┐
│  VOTRE ÉQUIPE CORTEX LEMAN              │
│                                          │
│  📊 Agent Data — "Data"                 │
│     Collecte et recherche documentaire   │
│     [Connecté: Knowledge Vault]          │
│     [Skills: recherche avancée, OCR]     │
│                                          │
│  ⚖️ Agent Raisonnement — "Juriste"      │
│     Analyse juridico-financière          │
│     [Connecté: LLM + RAG réglementaire]  │
│     [Skills: fiscal, conformité, audit]  │
│                                          │
│  🔒 Médiateur — "Gardien"               │
│     Surveillance et gel préventif        │
│     [22 règles actives]                  │
│     [Jamais de LLM — 100% déterministe]  │
│                                          │
│  ⚡ Agent Action — "Exécutant"           │
│     Exécution des tâches validées        │
│     [Connecté: n8n workflows]            │
│     [Jamais de LLM — transactionnel]     │
│                                          │
│  📈 Superviseur — "Observateur"          │
│     Tableau de bord continu              │
│     [Jamais de LLM — numérique pur]      │
│                                          │
│  [+ Ajouter un workflow personnalisé]    │
└─────────────────────────────────────────┘
```

### Phase 4: Connecteurs (inspiré Axio)
```
Pour Cortex Leman, les connecteurs sont RÉGLEMENTÉS:

┌─────────────────────────────────────────┐
│  CONNECTEURS DISPONIBLES                 │
│                                          │
│  📧 Email professionnel     [Connecter]  │
│     → Lecture seule pour audit           │
│                                          │
│  📊 ERP (Sage/SAP/Free)    [Connecter]   │
│     → Import données comptables          │
│                                          │
│  ⚖️ InfoGreffe/Zefix       [Connecter]   │
│     → Vérification registres             │
│                                          │
│  🔗 n8n Workflows          [Connecter]   │
│     → Automatisation réglementée         │
│                                          │
│  ⚠️ Mode Haute Protection               │
│     → Tous les connecteurs externes      │
│       sont désactivés (Art. 321 CP,      │
│       Art. 47 LB, LPM)                   │
└─────────────────────────────────────────┘
```

### Phase 5: Tâches programmées (inspiré Axio)
```
┌─────────────────────────────────────────┐
│  TÂCHES AUTOMATISÉES                     │
│                                          │
│  📋 Rapport conformité quotidien         │
│     Tous les jours à 8h00                │
│     [Actif ✅]  [Modifier]  [Pause]      │
│                                          │
│  🔔 Alerte seuil TVA                     │
│     Temps réel (NATS event)              │
│     [Actif ✅]  [Modifier]               │
│                                          │
│  📊 Synthèse mensuelle                   │
│     1er de chaque mois                   │
│     [Actif ✅]  [Modifier]               │
│                                          │
│  [+ Créer une tâche personnalisée]       │
└─────────────────────────────────────────┘
```

---

## 4. DIFFÉRENCES CLÉS POUR NOTRE ONBOARDING

### A. Onboarding GUIDÉ, pas libre
Axio = l'utilisateur crée ce qu'il veut
Cortex = l'utilisateur est GUIDÉ par sa vertical

```
Comptable → TVA, seuils, AFC, plan comptable
Avocat    → Secret professionnel, dossiers, CP 321
Santé     → HDS, consentement, LPM
Banque    → KYC/AML, LB 47, FINMA
Startup   → DPIA, RGPD, AI Act
RH        → Anti-discrimination, Art. 22 RGPD
```

### B. Gardrails dès le premier message
Axio = l'agent peut faire n'importe quoi
Cortex = le médiateur vérifie CHAQUE action

```
 utilisateur → "Déduire 15K de TVA"
 médiateur   → ⚠️ montant ≥ 10K + vertical comptable = GEL PRÉVENTIF
 utilisateur → "Pourquoi c'est gelé ?"
 système     → "Règle comptable-006: montant ≥ 50K nécessite validation expert"
 expert      → [Approuve] / [Rejette] / [Modifie]
```

### C. "Vibe" = Conformité, pas fun
Axio: friendly, professional, creative
Cortex: rigoureux, prudent, nuancé (comme notre skill reasoning.md)

### D. Audit permanent
Chaque action tracée (journal WORM + DB audit_logs)
L'utilisateur peut consulter son historique à tout moment
Indispensable pour RGPD + AI Act

---

## 5. PLAN D'IMPLÉMENTATION FRONTEND

### Sprint 3: React Frontend + Onboarding

#### Étape 1: Pages d'onboarding (React)
```
/login          → Email/SSO
/onboarding     → Choix vertical + nom cabinet
/dashboard      → Vue principale (par vertical)
/agents         → Gestion des agents (inspiré Axio)
/tasks          → Tâches programmées
/connectors     → Intégrations
/audit          → Journal d'audit
/arbitration    → Décisions d'arbitrage
/settings       → Configuration
```

#### Étape 2: Wizard de création d'agent
```typescript
// Inspiré Axio mais adapté réglementaire
interface AgentConfig {
  name: string;
  type: "data" | "reasoning" | "action";
  vertical: Vertical;
  skills: string[];
  model: "openrouter" | "ollama";
  guardrails: {
    pii_detection: boolean;     // toujours true
    topic_control: boolean;     // toujours true  
    output_safety: boolean;     // toujours true
    freeze_threshold: number;   // par vertical
  };
  schedule?: {
    task: string;
    frequency: "daily" | "weekly" | "monthly" | "realtime";
    time: string;
  };
}
```

#### Étape 3: Chat interface
```
Axio-style chat mais avec:
- Indicateur de confiance (barre colorée)
- Badge "Gel préventif" quand applicable
- Références réglementaires cliquables
- Bouton "Demander arbitrage" pour l'expert
- Historique des révisions d'intention
```

---

## 6. PRIORITÉ D'IMPLÉMENTATION

### P0 — Immédiat (Sprint 3)
1. ✅ API auth JWT (déjà fait)
2. 🔄 React frontend avec onboarding wizard
3. 🔄 Dashboard par vertical
4. 🔄 Chat interface avec guardrails visuels

### P1 — Court terme (Sprint 4)
5. Connecteurs (email, ERP)
6. Tâches programmées UI
7. Multi-tenancy
8. Mobile-responsive

### P2 — Moyen terme
9. Telegram/Discord channel
10. Module marketplace
11. White-label par tenant
12. App native (Electron/Tauri)

---

## 7. CE QU'ON NE REPREND PAS D'AXIO

| Concept Axio | Pourquoi on l'ignore |
|-------------|---------------------|
| Agent "libre" (fait n'importe quoi) | Non-conforme AI Act |
| Pas de journal d'audit | Obligatoire RGPD |
| LLM pour toutes les décisions | Médiateur doit être déterministe |
| Pas de gel/arbitrage | Obligatoire pour professions régulées |
| Aucun contrôle data residency | Obligatoire CH/EU |
| "Vibe" fun/creative | Inapproprié pour juridique/fiscal |
| Prix $10-20/mois | Notre valeur est dans la conformité |

---

## CONCLUSION

Axio Work nous inspire pour:
- **UX/DX**: Simplicité de l'interface, wizard d'onboarding
- **Mental model**: Agents = collègues (pas des outils)
- **Skills library**: Bibliothèque de compétences par catégorie
- **Tâches programmées**: Vue centralisée des automatisations
- **Connecteurs**: Intégrations tierces accessibles

Mais notre produit est fondamentalement DIFFÉRENT:
- Axio = productivité générique (n'importe qui, n'importe quoi)
- Cortex Leman = infrastructure de CONFIANCE (professions régulées, conformité)

Notre onboarding doit transmettre cette confiance dès la première seconde:
"Votre cabinet dispose maintenant d'une infrastructure de confiance IA
conforme RGPD, AI Act et secret professionnel. Chaque action est tracée,
chaque décision critiques est arbitrée par un humain."
