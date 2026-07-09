# 🎯 STRATÉGIE V3 — Cortex Leman v5
## Cross-validations : 5 modèles × 5 perspectives
## Date : 2026-05-27 (v3 après audit o3)

════════════════════════════════════════════════════════════
  HISTORIQUE DES VERSIONS
════════════════════════════════════════════════════════════

  v1 (2026-05-21) : Plan d'action Nemotron — Score 6.5/10
  v2 (2026-05-27) : Stratégie affinée post-DeepSeek — Score 5.5/10
  v3 (2026-05-27) : Correction post-audit o3 — Score projeté 8.0/10

════════════════════════════════════════════════════════════
  LES 5 VERDICTS CROISÉS
════════════════════════════════════════════════════════════

  ┌──────────────────────┬──────────────┬───────────────────────┐
  │ Analyste             │ Modèle       │ Verdict               │
  ├──────────────────────┼──────────────┼───────────────────────┤
  │ Moi (ingénieur)      │ —            │ OUI — Opportunité MCP │
  │ DeepSeek R1          │ R1-0528      │ OUI MAIS — trop tôt   │
  │ Dir. juridique GE    │ Qwen3-235B   │ OUI MAIS — 4 conditions│
  │ VC suisse            │ Sonnet 4     │ PAS ENCORE — solo     │
  │ Auditeur ISO 42001   │ OpenAI o3    │ NON — Score 5/10      │
  └──────────────────────┴──────────────┴───────────────────────┘

  CONVERGENCE DES 5 :
  - Le Médiateur déterministe est un bon produit technique
  - MCP est un canal, pas une stratégie
  - Le timing est trop précoce pour les agents (18-24 mois)
  - Sans accréditation tierce, le certificat n'a aucune valeur
  - Solo founder = risque majeur pour ce marché

════════════════════════════════════════════════════════════
  LA BOMBE DE L'AUDITEUR o3
════════════════════════════════════════════════════════════

  L'audit o3 a révélé 3 failles fatales dans la v2 :

  1. CERTIFICAT SANS VALEUR JURIDIQUE
     Seuls les organismes accrédités ISO/IEC 17065 peuvent
     délivrer un certificat AI Act (art. 43-45). Le PDF Cortex
     Leman = zéro valeur opposable. Potentiel "faux intellectuel"
     (CP CH art. 251, CP FR art. 441-1).

  2. WORM = VIOLATION RGPD
     Le journal loggue TOUT sans minimisation ni purge.
     Art. 5-1a/b RGPD : finalité et minimisation non respectées.
     Les logs contiennent des données couvertes par le secret
     professionnel sans chiffrement à la source.

  3. GOUVERNANCE ISO 42001 ABSENTE
     Pas de QMS, pas de comité d'éthique, pas de gestion
     d'incidents, pas de post-market monitoring, pas de
     notification aux autorités (AI Act art. 61-62).

  CONSÉQUENCE : Un auditeur ne peut signer qu'un rapport
  "avec réserve majeure". Score de conformité : 5/10.

════════════════════════════════════════════════════════════
  LE PIVOT FONDAMENTAL (v3)
════════════════════════════════════════════════════════════

  v1 : "Compliance layer MCP" (outil pour devs)
  v2 : "SOC 2 des agents IA" (certificat pour directions juridiques)
  v3 : "L'infrastructure de conformité que les certificateurs utilisent"

  ┌──────────────────────────────────────────────────────────┐
  │                                                          │
  │  Cortex Leman n'EST PAS le certificateur.               │
  │  Cortex Leman est l'OUTIL que les certificateurs         │
  │  utilisent pour auditer et certifier.                    │
  │                                                          │
  │  Analogie :                                              │
  │  Vanta/Drata ne délivrent PAS le SOC 2.                 │
  │  Ils fournissent l'infrastructure que l'auditeur         │
  │  utilise pour produire le rapport SOC 2.                 │
  │                                                          │
  │  Cortex Leman ne délivre PAS le certificat AI Act.       │
  │  Il fournit l'infrastructure que le Big 4 ou l'ordre     │
  │  professionnel utilise pour certifier.                   │
  │                                                          │
  └──────────────────────────────────────────────────────────┘

  POURQUOI CE PIVOT EST CRUCIAL :

  1. Élimine le risque "faux intellectuel" — on ne signe pas
  2. Élimine le besoin d'accréditation 17065 — c'est le partenaire qui l'a
  3. Positionne Cortex Leman comme ENABLEUR, pas concurrent des Big 4
  4. Le VC peut investir : pas de risque juridique sur le certificat
  5. Le directeur juridique peut acheter : le certificat vient d'un tiers

════════════════════════════════════════════════════════════
  ÉCOSYSTÈME CIBLE (v3)
════════════════════════════════════════════════════════════

  ┌──────────────────────────────────────────────────────────┐
  │                                                          │
  │  LÉGISLATEUR/RÉGULATEUR                                  │
  │  CNIL · PFPDT · FINMA · ENISA                           │
  │       │ définit les exigences                            │
  │       ▼                                                  │
  │  ORDRES PROFESSIONNELS                                   │
  │  Barreau · OEC · Ordres médecins                        │
  │       │ recommande le standard                           │
  │       ▼                                                  │
  │  CERTIFICATEURS (Big 4 / cabinets audit)                 │
  │  PwC · EY · Deloitte · KPMG · LALIVE                    │
  │       │ utilise Cortex Leman pour auditer                │
  │       ▼                                                  │
  │  CABINETS RÉGULÉS (clients finaux)                       │
  │  Avocats · Comptables · Banquiers · Médecins            │
  │       │ achète le certificat via le certificateur        │
  │       ▼                                                  │
  │  CORTEX LEMAN (infrastructure)                           │
  │  Médiateur · WORM · Rules · RAG · APIs                  │
  │                                                          │
  └──────────────────────────────────────────────────────────┘

  Flux de revenus :
  - Cabinet → paie le certificateur (Big 4) pour l'audit
  - Certificateur → paie Cortex Leman pour la licence plateforme
  - Cortex Leman → fournit l'infrastructure + support

════════════════════════════════════════════════════════════
  5 AXES STRATÉGIQUES (v3)
════════════════════════════════════════════════════════════

  ╔═══════════════════════════════════════════════════════╗
  ║  AXE 1 : INFRASTRUCTURE D'AUDIT (pas certificat)     ║
  ╚═══════════════════════════════════════════════════════╝

  CORRECTION o3 : On ne délivre PAS de certificat.
  On fournit les DONNÉES et les OUTILS pour qu'un certificateur
  accrédité produise un certificat.

  Ce qu'on vend :
  - Rapport de conformité brut (données d'audit)
  - Extrait WORM signé (preuve d'intégrité)
  - Score de conformité par verticale (métriques)
  - Mapping AI Act art. 9-17 (référentiel de contrôle)
  - Export PDF/CSV pour l'auditeur

  Ce qu'on NE vend PAS :
  - Un certificat signé Cortex Leman
  - Une attestation de conformité
  - Un label ou badge "approuvé par Cortex Leman"

  Pricing (licence plateforme) :
  - Par cabinet audité : CHF 300-800/mois
  - Par certificateur (Big 4) : CHF 2 000-5 000/mois
  - Setup initial : CHF 1 000-3 000

  ╔═══════════════════════════════════════════════════════╗
  ║  AXE 2 : SGAI ISO 42001 (gouvernance)                ║
  ╚═══════════════════════════════════════════════════════╝

  CORRECTION o3 : Sans gouvernance, le produit n'est pas auditable.

  Actions obligatoires :
  □ Politique de conformité IA documentée
  □ Registre des parties prenantes
  □ Objectifs mesurables (KPIs conformité)
  □ Comité d'éthique IA (min. 3 membres externes)
  □ Gestion des incidents (procédures, SLA, RACI)
  □ Post-market monitoring (AI Act art. 61-62)
  □ Notification aux autorités (délai 15 jours)

  Livrable : Manuel Qualité IA (SGAI) documenté
  Délai : 8 semaines

  ╔═══════════════════════════════════════════════════════╗
  ║  AXE 3 : WORM CONFORME RGPD                          ║
  ╚═══════════════════════════════════════════════════════╝

  CORRECTION o3 : Le WORM actuel viole le RGPD.

  Actions obligatoires :
  □ Minimisation des données journalisées (RGPD art. 5-1c)
  □ Règle de purge automatique (durée de conservation définie)
  □ Chiffrement au repos des logs WORM (AES-256)
  □ Cloisonnement par client/tenant (isolation des données)
  □ Anonymisation des données sensibles dans les logs
  □ Registre des traitements (RGPD art. 30)
  □ Matrice base légale par traitement (RGPD art. 6)
  □ Convention avocat-prestataire (CNB 2023-14)
  □ Clause de transfert si Azure/OpenAI (RGPD art. 44+)

  Livrable : WORM v2 conforme RGPD + documentation
  Délai : 6 semaines

  ╔═══════════════════════════════════════════════════════╗
  ║  AXE 4 : INTERFACES AGNOSTIQUES                       ║
  ╚═══════════════════════════════════════════════════════╝

  Inchangé par rapport à v2. 4 canaux d'entrée :

  MCP Tool ──┐
  REST API ──┤
  Python SDK─┼──► MÉDIATEUR ──► RAPPORT D'AUDIT
  CLI tool ──┘    (déterministe)    (pour certificateur)

  Ajout v3 : API d'export auditeur
  - /api/v1/audit/export?format=pdf&period=Q2-2026
  - /api/v1/audit/worm-extract?from=...&to=...
  - /api/v1/audit/compliance-score?vertical=comptable
  - Données structurées pour que l'auditeur certifie

  ╔═══════════════════════════════════════════════════════╗
  ║  AXE 5 : PARTENARIATS CERTIFICATEURS                 ║
  ╚═══════════════════════════════════════════════════════╝

  NOUVEAU dans v3. Remplace "cibler les ordres directement".

  Stratégie : s'adosser à ceux qui ONT DÉJÀ l'accréditation.

  Cible 1 : Big 4 (PwC, EY, Deloitte, KPMG)
  - Ils ont les accréditations ISO 17065
  - Ils ont les clients régulés
  - Ils ont besoin d'outils techniques pour l'AI Act
  - Proposition : "On vous fournit l'infrastructure d'audit IA,
    vous produisez le certificat et le signez"

  Cible 2 : Cabinets juridiques tech (LALIVE, Bär & Karrer)
  - Avis juridique sur la conformité IA
  - Peuvent recommander Cortex Leman à leurs clients
  - Proposition : "Notre infrastructure + votre avis juridique
    = service complet de conformité IA"

  Cible 3 : Assureurs RC professionnelle
  - Ils couvrent les cabinets contre les erreurs IA
  - Un cabinet avec Cortex Leman = risque réduit = prime baisse
  - Proposition : "Cabinet utilisant Cortex Leman = réduction
    de prime RC Pro de X%"

════════════════════════════════════════════════════════════
  PLAN D'EXÉCUTION — 24 SEMAINES (revu)
════════════════════════════════════════════════════════════

  PHASE 1 : CONFORMITÉ INTERNE (S1-S8) — Juin-Juillet 2026
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Avant de vendre de la conformité, être conforme soi-même.

  □ S1-S2 : SGAI ISO 42001
      - Politique de conformité IA
      - Registre des parties prenantes
      - Comité d'éthique (3 membres externes : 1 avocat,
        1 DPO, 1 expert IA)
      - Objectifs mesurables
      - Livrable : Manuel Qualité IA v1

  □ S3-S4 : WORM v2 conforme RGPD
      - Minimisation des données journalisées
      - Chiffrement au repos AES-256
      - Règle de purge (conservation max 24 mois)
      - Cloisonnement multi-tenant
      - Registre des traitements
      - Livrable : WORM v2 + documentation RGPD

  □ S5-S6 : Référentiel de contrôle AI Act
      - Mapper chaque article AI Act 9-17 → contrôle Cortex
      - Mapper RGPD 5-35 → contrôle Cortex
      - Mapper secret pro FR-CH → contrôle Cortex
      - Livrable : matrice de conformité (art. → contrôle → statut)

  □ S7-S8 : API d'export auditeur + interfaces agnostiques
      - 3 tools MCP (mediator_check/explain/precedent)
      - REST API /api/v1/mediator/check
      - API export /api/v1/audit/export (PDF/CSV)
      - Python SDK squelette
      - Livrable : infrastructure connectable par tout certificateur

  PHASE 2 : PILOTE AVEC CERTIFICATEUR (S9-S16) — Août-Octobre 2026
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  □ S9-S10 : Approche Big 4 / cabinet audit
      - Contacter 1 cabinet d'audit (PwC ou EY Genève/Lausanne)
      - Contacter 1 cabinet juridique tech (LALIVE)
      - Proposition : POC gratuit de l'infrastructure d'audit IA
      - Livrable : 1 certificateur en POC

  □ S11-S12 : 1er audit réel via certificateur
      - Déployer Cortex Leman chez 1 cabinet pilote
      - Le certificateur utilise Cortex pour produire un rapport
      - Documenter le process complet
      - Livrable : 1 rapport d'audit IA produit via Cortex Leman

  □ S13-S14 : Avis juridique externe
      - Obtenir un avis LALIVE (ou équivalent) sur :
        * La conformité RGPD de la plateforme
        * Le respect du secret professionnel
        * La validité des données d'audit pour l'AI Act
      - Livrable : avis juridique favorable

  □ S15-S16 : RC professionnelle + assurance
      - Souscrire une RC Pro pour Cortex Leman
      - Contacter 1 assureur RC Pro (Helvetia, Swiss Re)
      - Proposer : cabinet avec Cortex Leman = prime réduite
      - Livrable : RC Pro active + 1 assureur partenaire

  PHASE 3 : SCALE (S17-S24) — Novembre 2026-Février 2027
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  □ S17-S18 : White paper + ENISA
      - Publier "Infrastructure d'audit IA pour professions
        régulées FR-CH"
      - Contribuer aux travaux ENISA
      - Livrable : publication + visibilité régulateurs

  □ S19-S20 : Ordres professionnels
      - Avec 1 certificateur partenaire + 1 avis juridique,
        approcher les ordres (Barreau, OEC)
      - Proposition : "Recommandez l'infrastructure Cortex Leman
        comme standard d'audit IA pour vos membres"
      - Livrable : 1 ordre intéressé

  □ S21-S22 : Recrutement co-founder business
      - Profil : juriste tech ou ex-Big 4 conformité
      - Mission : partnerships + sales
      - Finance : equity + consulting revenue
      - Livrable : équipe de 2

  □ S23-S24 : Fundraising pre-seed
      - Si milestones atteints :
        * 1 certificateur partenaire actif
        * 1 avis juridique favorable
        * 1 cabinet pilote réel
        * Co-founder recruté
      - Lever CHF 100-200K pre-seed
      - Livrable : runway 12-18 mois

════════════════════════════════════════════════════════════
  MÉTRIQUES DE SUCCÈS (v3)
════════════════════════════════════════════════════════════

  Phase 1 (conformité interne) :
  □ Score de conformité ISO 42001 : 5/10 → 8/10
  □ WORM v2 conforme RGPD
  □ Référentiel AI Act complet (art. 9-17 mappés)
  □ 4 interfaces d'entrée opérationnelles
  □ Comité d'éthique constitué (3 membres)
  □ RC Pro souscrite

  Phase 2 (pilote certificateur) :
  □ 1 Big 4 ou cabinet audit en POC
  □ 1 rapport d'audit IA produit via Cortex Leman
  □ 1 avis juridique favorable
  □ 1 cabinet pilote réel (avec certificateur)

  Phase 3 (scale) :
  □ 1 ordre professionnel en discussion
  □ Co-founder business recruté
  □ CHF 100-200K levés
  □ 3-5 cabinets audités via Cortex Leman

════════════════════════════════════════════════════════════
  RISQUES ET MITIGATION (v3)
════════════════════════════════════════════════════════════

  RISQUE 1 : Microsoft lance "Compliance Hub for Agents"
  Probabilité : 60% dans 12-18 mois
  Mitigation v3 : Agnostisme total + positionnement enableur.
  Si MS lance son hub, les Big 4 auront besoin d'une alternative
  indépendante. Cortex Leman = l'alternative non-Microsoft.

  RISQUE 2 : Marché trop précoce
  Probabilité : élevée sur agents, modérée sur outils IA basiques
  Mitigation v3 : Le certificateur vend au cabinet, pas nous.
  Son cycle de vente existe déjà. On lui ajoute un service
  (audit IA) sans créer un nouveau marché de zéro.

  RISQUE 3 : Big 4 construisent leur propre outil
  Probabilité : 30%
  Mitigation v3 : First-mover + expertise FR-CH. Les Big 4
  sont lents à construire. S'ils utilisent Cortex Leman pendant
  12 mois, le switching cost sera élevé.

  RISQUE 4 : Solo founder
  Probabilité : 100% aujourd'hui
  Mitigation v3 : Recrutement S21-S22. En attendant,
  le comité d'éthique (3 membres externes) apporte crédibilité.

  RISQUE 5 : WORM non conforme RGPD
  Probabilité : 100% aujourd'hui (identifié par o3)
  Mitigation v3 : WORM v2 en Phase 1 (S3-S4). Bloquant.

════════════════════════════════════════════════════════════
  CE QUI NE CHANGE PAS (cœur de produit)
════════════════════════════════════════════════════════════

  ✅ Médiateur 100% déterministe (jamais de LLM pour les décisions)
  ✅ Journal WORM hash-chainé SHA-256 (mais v2 conforme RGPD)
  ✅ Arbitrage humain (l'IA ne décide jamais seule)
  ✅ 6 verticales FR-CH
  ✅ Mode Haute Protection (K3s + Ollama)
  ✅ Rules JsonLogic par verticale
  ✅ Precedent Store (jurisprudence IA)

════════════════════════════════════════════════════════════
  CE QUI CHANGE (v2 → v3)
════════════════════════════════════════════════════════════

  ❌ v2 : "On délivre le certificat"
  ✅ v3 : "On fournit les données pour que le certificateur délivre"

  ❌ v2 : Cible cabinets directement
  ✅ v3 : Cible certificateurs (Big 4) qui vendent aux cabinets

  ❌ v2 : Certificat Cortex Leman
  ✅ v3 : Rapport d'audit Cortex Leman (pour certificateur)

  ❌ v2 : Badge "Certifié Cortex Leman"
  ✅ v3 : Données d'audit vérifiables (pour certificateur)

  ❌ v2 : Pricing cabinet (CHF 500-1500/mois)
  ✅ v3 : Pricing certificateur (CHF 2000-5000/mois)
           + pricing cabinet via certificateur

  ❌ v2 : Pas de gouvernance ISO 42001
  ✅ v3 : SGAI complet + comité d'éthique

  ❌ v2 : WORM journalise tout sans purge
  ✅ v3 : WORM v2 avec minimisation + chiffrement + purge

════════════════════════════════════════════════════════════
  LA PHRASE QUI TUE — v3 (ELEVATOR PITCH)
════════════════════════════════════════════════════════════

  v1 : "Infrastructure de confiance IA"
  v2 : "Le SOC 2 des agents IA"
  v3 :

  "L'infrastructure d'audit IA pour professions régulées.
   On fournit au certificateur les données, les contrôles
   et la traçabilité pour certifier la conformité AI Act
   et RGPD des cabinets franco-suisses."

  → Réaction du Big 4 : "Vous nous faites gagner du temps
     sur les audits IA ? On est preneur."
  → Réaction du VC : "Pas de risque juridique sur le certificat.
     Vous vendez des shovels pendant la ruée vers l'or. Combien ?"
  → Réaction du directeur juridique : "Mon cabinet d'audit
     utilise votre outil ? Alors je suis couvert."

════════════════════════════════════════════════════════════
  PROCHAINE ACTION IMMÉDIATE
════════════════════════════════════════════════════════════

  Semaine 1 (Phase 1) :

  1. WORM v2 — Ajouter chiffrement AES-256 au repos
     + minimisation des données journalisées
     + règle de purge (conservation max 24 mois)
     Fichier : core/journal/append_only_journal.py

  2. SGAI — Créer le document Manuel Qualité IA
     (politique, gouvernance, objectifs)
     Fichier : docs/sgai/MANUAL-QUALITE-IA.md

  3. Comité d'éthique — Identifier 3 membres externes
     (1 avocat, 1 DPO, 1 expert IA)

  4. API export auditeur — Endpoint /api/v1/audit/export
     Fichier : api/routes/audit.py

  Durée estimée : 2 semaines
  Prérequis : codebase actuelle + corrections o3

════════════════════════════════════════════════════════════
  ANNEXE : RÉFÉRENTIEL DE CONTRÔLE AI ACT (extrait)
════════════════════════════════════════════════════════════

  | Art. AI Act | Exigence                    | Contrôle Cortex         | Statut |
  |-------------|-----------------------------|------------------------|--------|
  | 9           | Risk management system      | Médiateur + rules      | Partiel|
  | 10          | Data governance              | —                      | MANQUANT|
  | 11          | Technical documentation      | WORM + export audit    | Partiel|
  | 13          | Transparency                 | Journal + score        | Partiel|
  | 14          | Human oversight              | Arbitrage humain       | OK     |
  | 15          | Accuracy/robustness/security | Circuit breaker + saga | Partiel|
  | 17          | Quality management system    | —                      | MANQUANT|
  | 61-62       | Post-market monitoring       | —                      | MANQUANT|

  | Art. RGPD   | Exigence                    | Contrôle Cortex         | Statut |
  |-------------|-----------------------------|------------------------|--------|
  | 5-1a/b      | Finalité/minimisation       | WORM purge             | MANQUANT|
  | 6/9         | Base légale/sensibles       | —                      | MANQUANT|
  | 30          | Registre traitements        | —                      | MANQUANT|
  | 35          | DPIA                        | Auto-générée           | Partiel|
  | 44+         | Transferts                  | Mode Haute Protection  | OK     |

  | Secret pro  | Exigence                    | Contrôle Cortex         | Statut |
  |-------------|-----------------------------|------------------------|--------|
  | CP 321      | Secret avocat CH            | Chiffrement WORM       | MANQUANT|
  | LB 47       | Secret bancaire CH          | K3s local              | OK     |
  | LPM         | Données santé CH            | HDS + local            | Partiel|
  | CNB 2023-14 | Convention avocat-prestataire| —                      | MANQUANT|

════════════════════════════════════════════════════════════
  SCORE DE CONFORMITÉ PROJETÉ
════════════════════════════════════════════════════════════

  Actuel (mai 2026) :     5.0 / 10  (audit o3)
  Après Phase 1 (S8) :    7.5 / 10  (projeté)
  Après Phase 2 (S16) :   8.5 / 10  (projeté)
  Après Phase 3 (S24) :   9.0 / 10  (projeté)

════════════════════════════════════════════════════════════
  SIGNÉ : Cortex Leman v3
  CROSS-VALIDÉ PAR : DeepSeek R1 · Qwen3-235B · Claude Sonnet 4 · OpenAI o3
  DATE : 2026-05-27
════════════════════════════════════════════════════════════
