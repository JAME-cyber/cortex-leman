# 🎯 CORTEX LEMAN v5 — PLAN D'ACTION PRIORISÉ
# Synthèse des cross-validations : Nemotron-120B + Mistral Nemotron + Llama-3.3
# Généré le 2026-05-21

════════════════════════════════════════════════════════════
  SCORE CONSOLIDÉ : 6.5/10
  Verdict : Prometteur, pas prêt pour production client
════════════════════════════════════════════════════════════

  ✅ Points forts (consensus des 2 modèles) :
  - Architecture 5 agents + Médiateur + NATS solide
  - Business model récurrent réaliste (CHF 500-1500)
  - Positionnement FR-CH unique
  - Journal WORM + JsonLogic = bons choix techniques
  - 81 modules core + 23 fichiers tests

  🔴 Points faibles (consensus des 2 modèles) :
  - Mode dégradé incomplet (pas de timeout, pas de re-validation)
  - Trous réglementaires dans les questions d'audit
  - Aucun client pilote réel (5 dossiers vault = test data)
  - Frontend incomplet
  - Pas de DPIA documentée
  - Pas de preuve de terrain

════════════════════════════════════════════════════════════
  ACTIONS CLASSÉES PAR PRIORITÉ
════════════════════════════════════════════════════════════

  🔴 PRIORITÉ 1 — BLOQUANT POUR DÉPLOIEMENT CLIENT
  
  Ces actions sont OBLIGATOIRES avant tout déploiement
  chez un vrai cabinet. Sans elles = responsabilité juridique.

  ✅ 1.1 TIMEOUT mode dégradé (30 min max)
      - Fichier : core/mediator/mediator.py
      - _DEGRADED_TIMEOUT_SEC = 1800s, auto-FROZEN si dépassé
      - FAIT le 2026-05-21

  ✅ 1.2 Re-validation LLM en mode dégradé
      - Fichier : core/mediator/mediator.py
      - _validate_enrichment(): confidence ≥ 0.3, pas de résultat vide/erreur
      - FAIT le 2026-05-21

  ✅ 1.3 Matrice de gravité dans le Médiateur
      - Fichier : core/mediator/mediator.py
      - _SEVERITY_TO_GRAVITY: low=1, medium=2, high=3, critical=4, block=5
      - Niveau 1-2 → DEGRADED, niveau 3-5 → FROZEN immédiat
      - FAIT le 2026-05-21

  ✅ 1.4 Tests onboarding (37 tests)
      - Fichier : tests/test_onboarding.py
      - 37/37 passent : compliance, haute protection, LLM modes, tenant ID, edge cases
      - FAIT le 2026-05-21

  ✅ 1.5 Template DPIA / AIPD par vertical
      - docs/compliance/AIPD-TEMPLATE.md — template commun
      - docs/compliance/aipd/aipd-comptable.md
      - docs/compliance/aipd/aipd-avocat.md
      - docs/compliance/aipd/aipd-sante.md
      - docs/compliance/aipd/aipd-banque.md
      - docs/compliance/aipd/aipd-startup.md
      - docs/compliance/aipd/aipd-rh.md
      - FAIT le 2026-05-21
      - Temps estimé : 3h

  □ 1.4 Tests onboarding
      - Fichier : tests/test_onboarding.py (à créer)
      - Couvrir : création tenant, activation journal, chargement règles, consentement
      - Pourquoi : 0 test actuellement = risque de régression silencieuse
      - Temps estimé : 4h

  □ 1.5 Document DPIA par verticale
      - Fichier : docs/compliance/DPIA-TEMPLATE.md (à créer)
      - Couvrir : santé, banque, avocat, RH, comptable, startup
      - Pourquoi : RGPD Art.35 obligatoire pour données sensibles
      - Temps estimé : 6h (rédaction)

  🟡 PRIORITÉ 2 — NÉCESSAIRE POUR CRÉDIBILITÉ
  
  Ces actions sont nécessaires pour convaincre un prospect
  ou passer un audit de certification.

  ✅ 2.1 Compléter les questions d'audit manquantes
      - Fichier : docs/AUDIT-QUESTIONS.md
      - 7 sections ajoutées (15-21) couvrant :
        * Section 15 : DPIA / AIPD par verticale (Art. 35)
        * Section 16 : Registre des Risques IA (Art. 9-15)
        * Section 17 : Sous-traitants & Transfert (Art. 28)
        * Section 18 : Sécurité des LLM (Art. 15)
        * Section 19 : PCA / DRP avec RTO/RPO
        * Section 20 : Explicabilité & Transparence (Art. 13-14)
        * Section 21 : Auditabilité & Preuve légale
      - Sections 6.1 et 6.3 mises à jour (mode dégradé)
      - 68 questions d'audit au total (was ~54)
      - FAIT le 2026-05-21

  □ 2.2 Runbooks d'exploitation
      - Fichier : docs/runbooks/ (à créer)
      - Créer : incident-response.md, failover.md, key-rotation.md
      - Pourquoi : aucun runbook existant = impossible d'exploiter
      - Temps estimé : 4h

  □ 2.3 Trouver 1 VRAI client pilote
      - Cible : 1 cabinet d'avocats OU 1 cabinet comptable genevois/annemassien
      - Offre : audit gratuit + 3 mois Sentinelle (CHF 0)
      - Objectif : 1 cas d'usage réel documenté
      - Pourquoi : 5 vault = test data. 0 client réel = pas de traction
      - Temps estimé : prospecter via réseau existant

  ✅ 2.4 Cross-valider les AIPD avec Nemotron
      - Modèle : Nemotron-3-Super-120B via OpenRouter
      - Score : 4/10 (template non rempli — attendu pour un template client)
      - Lacunes corrigées : règles JsonLogic complétées (avocat-003/004, sante-003, banque-003, rh-003)
      - Note ajoutée sur le statut template vs document complété
      - Résultat : docs/compliance/aipd/CROSS-VALIDATION-RESULT.txt
      - FAIT le 2026-05-21

  □ 2.5 Frontend pages critiques
      - Manquant : Dashboard conformité, Journal viewer, Arbitrage UI
      - Pourquoi : un cabinet ne peut pas utiliser que le chat
      - Temps estimé : 2-3 semaines (frontend React)

  □ 2.5 Workflow Stripe pour plans récurrents
      - Fichier : action-5-modele-recurrent.md décrit l'implémentation
      - Configurer : Sentinelle (CHF 500), Garde (CHF 900), Forteresse (CHF 1500)
      - Pourquoi : aucun revenu sans système de paiement
      - Temps estimé : 1 semaine

  🟢 PRIORITÉ 3 — AMÉLIORATION CONTINUE
  
  Ces actions améliorent la qualité mais ne bloquent pas le lancement.

  □ 3.1 Partenariat ordre professionnel (barreau, ordre experts-comptables)
  □ 3.2 Content marketing (white papers, webinars conformité IA)
  □ 3.3 Certificat de conformité dynamique
  □ 3.4 Version "lite" pour petits cabinets (< 10 personnes)
  □ 3.5 Monitoring drift du modèle LLM

════════════════════════════════════════════════════════════
  PLANNING PROPOSÉ (4 SEMAINES)
════════════════════════════════════════════════════════════

  SEMAINE 1 : SÉCURITÉ + CONFORMITÉ (Priorité 1)
  ├── Jour 1-2 : Timeout mode dégradé + matrice de gravité
  ├── Jour 3-4 : Re-validation LLM + tests onboarding
  └── Jour 5 : Template DPIA

  SEMAINE 2 : AUDIT + DOCS (Priorité 2.1 + 2.2)
  ├── Jour 1-2 : Compléter questions d'audit
  ├── Jour 3-4 : Runbooks d'exploitation
  └── Jour 5 : Mise à jour knowledge base

  SEMAINE 3 : PILOTE + PAIEMENT (Priorité 2.3 + 2.5)
  ├── Jour 1-3 : Prospecter 1 client pilote
  ├── Jour 3-5 : Configurer Stripe plans récurrents
  └── Livrable : offre pilote prête

  SEMAINE 4 : FRONTEND + LANCEMENT (Priorité 2.4)
  ├── Jour 1-3 : Dashboard + Journal viewer minimaux
  ├── Jour 4-5 : Landing page mise à jour + test complet
  └── Livrable : produit déployable pour 1er client

════════════════════════════════════════════════════════════
  INVESTISSEMENT NÉCESSAIRE
════════════════════════════════════════════════════════════

  | Poste | Coût | Quand |
  |-------|------|-------|
  | Serveur CH (pilote) | ~50 CHF/mois | Semaine 3 |
  | Stripe setup | 0€ (2.9% + 0.30 CHF/transaction) | Semaine 3 |
  | Domaine .ch | ~15 CHF/an | Semaine 3 |
  | NVIDIA NIM (LLM) | Free tier ou ~50 CHF/mois | Continu |
  | Total mois 1 | ~65 CHF | |

════════════════════════════════════════════════════════════
  MÉTRIQUES DE SUCCÈS
════════════════════════════════════════════════════════════

  Semaine 1 : 5 corrections critiques implémentées
  Semaine 2 : Questions d'audit complètes + runbooks
  Semaine 3 : 1 client pilote signé + Stripe live
  Semaine 4 : Produit déployé chez 1er client
  
  Mois 3 : 3-5 clients récurrents (MRR ~3000-4500 CHF)
  Mois 6 : 10+ clients (MRR ~8000 CHF, break-even)
