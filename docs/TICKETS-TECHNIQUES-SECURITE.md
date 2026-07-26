# Tickets Techniques — Sécurité & Compliance

> **Créé:** 2026-07-14
> **Source:** Veille Threat Intel (ArXiv Daily 2026-07-14) + Alerte Sanction CNIL
> **Destinataire:** Tars (escalade technique)
> **Priorisation:** P0 (bloquant) → P1 (urgent) → P2 (planifié)

---

## TICKET-001 — [P1] Durcir les pipelines vision contre les attaques adversariales

**Menace source:** THREAT-001 (arXiv 2607.11560 — CVPR 2026@AdvML Challenge)
**Risque compliance:** AI Act Art. 15 (Robustesse), Art. 14 (Supervision humaine)

**Contexte:**
Les vision-language agents (VLAs) sont vulnérables à des attaques adversariales multimodales documentées dans le challenge CVPR 2026. Les pipelines de L'Oeil de Cortex utilisant de la vision documentaire (détection de falsification, deepfake, OCR intelligent) sont potentiellement exposés.

**Action attendue de Tars:**
1. Identifier quels composants de L'Oeil de Cortex utilisent des VLAs ou modèles vision-language
2. Évaluer la robustesse adversariale de ces composants (test avec exemples adversariaux)
3. Si vulnérabilité confirmée: ajouter une couche de défense (input sanitization, adversarial training, ou fallback vers validation humaine)
4. Documenter les résultats dans un AIPD si le composant traite des données Art. 9

**Effort estimé:** 2-3 jours (investigation + tests)
**Référence arXiv:** https://arxiv.org/abs/2607.11560

---

## TICKET-002 — [P1] Intégrer le red-teaming d'agents en production

**Menace source:** THREAT-002 (arXiv 2607.11698 — Agent Hacks Agent)
**Risque compliance:** RGPD Art. 32, AI Act Art. 15, OWASP LLM01 (Prompt Injection)

**Contexte:**
Les agents Cortex Leman (tâches autonomes, accès documentaire) peuvent être ciblés via des contenus non fiables qu'ils traitent. Le framework "Agent Hacks Agent" permet de détecter automatiquement ces failles.

**Action attendue de Tars:**
1. Évaluer le framework "Agent Hacks Agent" (arXiv 2607.11698) pour applicabilité
2. Identifier les agents Cortex Leman exposés à des contenus non fiables
3. Créer un pipeline de red-teaming automatisé pour ces agents
4. Intégrer les vecteurs d'attaque documentés dans les tests de pénétration internes
5. Documenter la couverture de test dans le registre de traitement (Art. 30 RGPD)

**Effort estimé:** 3-5 jours (évaluation + implémentation)
**Référence arXiv:** https://arxiv.org/abs/2607.11698

---

## TICKET-003 — [P2] Vérifier l'intégrité multi-agents (backdoors distribués)

**Menace source:** THREAT-003 (arXiv 2607.11751 — Distributed Backdoors in Multi-Agent Systems)
**Risque compliance:** RGPD Art. 25 (Privacy by Design), Art. 32

**Contexte:**
L'architecture multi-agents Cortex Leman (Agent Data → Raisonnement → Action) peut être vulnérable à des backdoors distribués qui exploitent la composition des agents. Un composant compromis peut introduire un comportement malveillant uniquement quand chainé avec d'autres.

**Action attendue de Tars:**
1. Cartographier tous les points de chaining entre agents Cortex Leman
2. Identifier les points d'injection possibles (inputs partagés, contexte passé entre agents)
3. Vérifier l'intégrité de chaque composant agent avant chaining
4. Ajouter des assertions d'intégrité aux interfaces inter-agents

**Effort estimé:** 2-4 jours
**Ré références:** https://arxiv.org/abs/2607.11751

---

## TICKET-004 — [P2] Déploiement dashboard compliance React

**Source:** Weekly Report (job a7cbd0ff1c22) + BUSINESS-CASE-GOUVERNANCE-AGENTS-IA-v2.md
**Risque compliance:** AI Act Art. 13 (Transparence), Art. 60 (Reporting)

**Contexte:**
Le dashboard client interactif (KPIs: score global, violations critiques, ROI client, délai audit) est spécifié dans le skill le-narrateur-augmente mais n'est pas encore déployé. Ce dashboard est nécessaire pour la transparence AI Act (Art. 13) et pour présenter les résultats d'audit de façon professionnelle.

**Action attendue de Tars:**
1. Déployer le dashboard React à partir des specs du skill le-narrateur-augmente
2. Intégrer les KPIs: Score Global, Violations Critiques, ROI Client, Délai Audit
3. Ajouter les filtres: par domaine, par criticité, par statut
4. Connecter aux données d'audit (backend API)
5. Déployer via Docker (docker-compose.yml existe déjà)

**Effort estimé:** 3-5 jours
**Référence:** `docs/BUSINESS-CASE-GOUVERNANCE-AGENTS-IA-v2.md`

---

## TICKET-005 — [P2] Améliorer l'explainability des décisions d'anomalie

**Menace source:** THREAT-004 + ArXiv 2607.11862 (Evidence-Backed Video QA)
**Risque compliance:** AI Act Art. 13 (Transparence), RGPD Art. 22 (Décision automatisée)

**Contexte:**
Les décisions d'anomalie produites par L'Oeil de Cortex doivent être explainables pour se conformer à AI Act Art. 13. Actuellement, les sorties du modèle ne documentent pas systématiquement la chaîne de raisonnement.

**Action attendue de Tars:**
1. Ajouter une sortie "evidence-backed" aux décisions d'anomalie (source, confidence, raisonnement)
2. Implémenter un logging structuré des décisions IA (Art. 30 RGPD)
3. Documenter la chaîne de raisonnement dans le rapport d'audit client

**Effort estimé:** 2-3 jours
**Référence arXiv:** https://arxiv.org/abs/2607.11862

---

## TICKET-006 — [P1] Corriger le hash journal WORM cassé

**Source:** Weekly Report S-28 (job a7cbd0ff1c22, 10/07) — action Top 3 #2
**Risque compliance:** RGPD Art. 5(1)(f) (Intégrité), Art. 30 (Traçabilité), AI Act Art. 12 (Logging)

**Contexte:**
Le rapport interne du 2 juillet détecte un hash invalide à la ligne 9 du journal WORM (Write-Once-Read-Many) append-only. Un journal append-only dont la chaîne de hash est cassée n'est plus vérifiable — il devient un simple fichier texte. Ce journal est l'artefact de traçabilité principal pour justifier une décision IA devant la CNIL (Art. 30 RGPD). En l'état, **inexploitable en audit**.

C'est le blocker technique qui empêche tout usage client sérieux du journal d'audit. Bloque aussi la démo de la stack compliance.

**Action attendue de Tars:**
1. Investiguer la ligne 9 du journal WORM : pourquoi le hash ne valide pas (encodage, algo, ordre des champs ?)
2. Corriger la logique de hashage dans le module d'écriture du journal
3. Ajouter un test de non-régression : à chaque append, vérifier la chaîne de bout en bout
4. Re-valider le journal existant (ou le réinitialiser proprement si irrecevable, avec trace de l'opération)

**Effort estimé:** 2-4 heures (investigation + fix + tests)
**Référence:** Weekly Report 10/07 §2 Produit, point 2

---

## TICKET-007 — [P2] Tester la robustesse jailbreak des modèles quantifiés (protocole JADR)

**Menace source:** arXiv 2607.12792 — "Silent Alarm" (score 14/20, ArXiv Daily 15/07)
**Risque compliance:** AI Act Art. 15 (Robustesse, cybersécurité), RGPD Art. 32

**Contexte:**
L'étude "Silent Alarm" démontre que la **quantization** (BF16 → INT8 → INT4) dégrade les mécanismes de sécurité internes des LLM. Les modèles quantifiés, déployés pour économiser du compute chez les clients (edge, on-prem), deviennent plus vulnérables au jailbreak. Le protocole JADR mesure la reconnaissance interne du danger via l'espace Jacobian avant la première réponse.

Si Cortex Leman déploie ou recommande des modèles quantifiés chez ses clients (scénario PME on-prem, latence faible), la posture de sécurité réelle est inférieure à celle mesurée en labo.

**Action attendue de Tars:**
1. Répertorier les modèles quantifiés effectivement déployés/recommandés chez les clients Cortex Leman
2. Reproduire le protocole JADR sur ces modèles (3 niveaux : BF16, INT8, INT4) — code open-source disponible
3. Intégrer un check "niveau de quantization vs robustesse" dans la checklist de déploiement client (CHECKLIST-COMPLIANCE-IA.md)
4. Si vulnérabilité confirmée : documenter la mesure complémentaire requise (Art. 32 RGPD)

**Effort estimé:** 1-2 jours (reproduction + intégration checklist)
**Référence arXiv:** https://arxiv.org/abs/2607.12792

---

## TICKET-008 — [P2] Auditer le registre de skills Hermes/Cortex Leman (skills hallucinées)

**Menace source:** arXiv 2607.12340 — "Hallucinated Skill Recommendation" (score 12/20, ArXiv Daily 15/07)
**Risque compliance:** AI Act Art. 9-10 (Gestion des risques), RGPD Art. 25 (Privacy by Design), OWASP LLM08 (Supply Chain Vulnerabilities)

**Contexte:**
L'étude à grande échelle sur les skills hallucinées recommandées par les agents LLM depuis des registres ouverts révèle un risque de **supply chain attack** : un agent peut recommander et tenter d'invoquer une skill inexistante ou malveillante. Appliqué au système de skills Hermes/Cortex Leman, une skill inexistante ou compromise recommandée par l'agent pourrait introduire des vulnérabilités ou exécuter des actions non prévues.

Particulièrement pertinent vu le grand nombre de skills chargées dans ce projet (le-gardien-des-normes, le-narrateur-augmente, anti-ia-humanizer, etc.).

**Action attendue de Tars:**
1. Extraire la liste exhaustive des skills effectivement installées dans Hermes (default profile)
2. Pour chaque skill, vérifier qu'elle correspond à un fichier réel et non une hallucination de l'agent
3. Ajouter un garde-fou : si l'agent recommande/invoque une skill non listée dans le registre → bloquer + alerter
4. Documenter le registre de skills vérifié dans le registre de traitement (Art. 30 RGPD)

**Effort estimé:** 1 jour (audit + garde-fou)
**Référence arXiv:** https://arxiv.org/abs/2607.12340

---

## TICKET-009 — [P1] Évaluer Traccia comme socle d'observabilité agent IA (OpenTelemetry)

**Menace source:** arXiv 2607.14309 — "Traccia: An OpenTelemetry-Based Governance Platform for AI Systems" (score 20/20, ArXiv Daily 18/07)
**Risque compliance:** AI Act Art. 12 (Logging obligatoire), Art. 17 (Transparence), RGPD Art. 22 (Décision automatisée expliquée), Art. 30 (Registre)

**Contexte:**
Traccia est une plateforme open-source de gouvernance IA exploitant OpenTelemetry pour tracer LLMs et agents autonomes de bout-en-bout. Score parfait 20/20 sur le scan du 18/07. Comble exactement le gap entre les exigences AI Act (transparence, accountability, logging) et les pratiques réelles de monitoring chez les PME FR-CH.

Pour Cortex Leman, c'est double intérêt :
1. **Interne** — socle d'évidence pour justifier nos décisions agent devant la CNIL (Art. 22 + Art. 30)
2. **Commercial** — différenciateur "compliance tooling" face aux auditeurs RGPD classiques (cf. ArXiv Daily 18/07 signal #2)

OpenTelemetry est déjà un standard mature → intégration rapide, ROI compliance direct.

**Action attendue de Tars:**
1. Cloner/évaluer le repo Traccia (licence, maturité, dépendances)
2. POC d'intégration sur un agent Cortex Leman (L'Oeil de Cortex ou L'Ingénieur de Flux)
3. Vérifier que les traces produites couvrent : chaque prompt, chaque réponse LLM, chaque appel d'outil, timing par composant (cf. Checklist Phase 6)
4. Si concluant : déployer sur le pipeline agent de production + documenter dans le registre de traitement (Art. 30)
5. Préparer un one-pager commercial "Notre stack d'observabilité IA est AI Act-ready" pour Le Narrateur

**Effort estimé:** 2-3 jours (évaluation + POC + doc)
**Référence arXiv:** https://arxiv.org/abs/2607.14309

---

## TICKET-010 — [P0] Auditer la mémoire persistante Hermes/Cortex Leman (Bad Memory + MemPoison)

**Menace source:** arXiv 2607.14611 — "Bad Memory: Prompt Injection via Agent Memory" (16/20) + arXiv 2607.14651 — "MemPoison: Persistent Memory Threats" (12/20, 1227 cas documentés) — ArXiv Daily 18/07
**Risque compliance:** AI Act Art. 14 (Oversight humain), Art. 15 (Robustesse), RGPD Art. 25 (Privacy by Design), Art. 32 (Sécurité)
**Priorité:** **P0 — IMPACT DIRECT SUR NOTRE STACK**

**Contexte:**
**⚠️ Ceci est la menace la plus directement applicable à Cortex Leman identifiée ce cycle.**

Deux papiers indépendants (Bad Memory 2607.14611, MemPoison 2607.14651 — 1227 cas documentés) démontrent une nouvelle classe d'attaque : des instructions malveillantes injectées dans les fichiers de mémoire persistante d'agents LLM (mémoire cross-session, préférences comportementales, knowledge bases) peuvent déclencher un comportement déviant en sessions futures, sans que l'utilisateur ne le sache.

**Hermes/Cortex Leman utilisent massivement la mémoire cross-session** — c'est un mécanisme central de l'architecture. Risque réel et documenté : un prompt injecté aujourd'hui dans une mémoire agent (par ex. via un contenu web ingéré par le RAG Auto-Ingestion, un email, un document client) pourrait compromettre le comportement d'agents lors de sessions ultérieures, y compris sur d'autres dossiers clients.

Les 1227 cas MemPoison constituent une base de tests rouge directement exploitable.

**Action attendue de Tars:**
1. **Cartographier toutes les sources d'entrée qui alimentent la mémoire cross-session** des agents Cortex Leman (RAG Auto-Ingestion, contenus web, documents clients, outputs d'autres agents)
2. **Audit sandbox mémoire** : appliquer les vecteurs d'attaque documentés (Bad Memory + MemPoison) sur les profils Hermes en production
3. **Ajouter un sanitizeur** sur tout contenu entrant dans la mémoire persistante (détection de patterns d'instruction persistantes, isolation par namespace client)
4. **Tests de non-régression** : un vecteur MemPoison injecté via le RAG ne doit pas modifier le comportement d'un agent en session ultérieure
5. Documenter dans le registre de traitement (Art. 30) et l'AIPD si profil high-autonomy

**Effort estimé:** 3-5 jours (audit + hardening + tests)
**Références arXiv:**
- https://arxiv.org/abs/2607.14611 (Bad Memory)
- https://arxiv.org/abs/2607.14651 (MemPoison, 1227 cas)

---

## TICKET-011 — [P1] Tester FlowGuard sur les serveurs MCP Apify/n8n (sécurité runtime MCP)

**Menace source:** arXiv 2607.14754 — "FlowGuard: From Signals to Evidence for MCP Security Detection" (12/20, priorité stratégique, ArXiv Daily 18/07)
**Risque compliance:** AI Act Art. 15 (Robustesse & cybersécurité), Art. 9 (Gestion des risques), RGPD Art. 32 (Sécurité)
**Note:** Première recherche académique dédiée à la sécurité MCP — fenêtre early-adopter.

**Contexte:**
Cortex Leman repose sur le Model Context Protocol (MCP) pour les outils Apify, n8n, etc. FlowGuard révèle que les scanners MCP actuels raisonnent uniquement sur des signaux sémantiques (chaînes credential-like) mais ignorent le runtime. Résultat : un scanner peut alerter sur un placeholder inoffensif et rater une vraie fuite. FlowGuard valide via preuves d'exécution (placeholders vs vraies fuites).

Comme Cortex Leman utilise Apify (RAG web browser, scrape) et n8n (3 workflows opérationnels) qui interagissent avec des données clients potentiellement sensibles, la validation runtime des serveurs MCP est devenue nécessaire.

**Action attendue de Tars:**
1. Évaluer FlowGuard (maturité, licence, dépendances) — premier papier académique dédié
2. Tester FlowGuard sur les serveurs MCP en usage : Apify (rag-web-browser, autres actors), n8n (audit-report-generator, anti-ia-humanizer, rebooking-send)
3. Vérifier qu'aucun serveur MCP en usage ne fait fuiter des credentials ou données sensibles au runtime
4. **Avant tout ajout de nouveau MCP tierce** : passer FlowGuard comme étape obligatoire du processus d'onboarding
5. Documenter la politique MCP dans le registre de traitement

**Effort estimé:** 2-3 jours (évaluation + tests)
**Référence arXiv:** https://arxiv.org/abs/2607.14754

---

## TICKET-012 — [P2] Politique supply-chain pour skills externes (Setup Compromised)

**Menace source:** arXiv 2607.15143 — "Setup Complete, Now You Are Compromised" (12/20, ArXiv Daily 18/07)
**Risque compliance:** AI Act Art. 9-10 (Gestion des risques), RGPD Art. 25, OWASP LLM08 (Supply Chain Vulnerabilities)

**Contexte:**
Première évaluation systématique d'attaques supply-chain livrées via README/requirements/Makefile. Un attaquant édite un README ou un fichier d'instructions dans un repo distant ; un agent coding (type Hermes/Cursor/Claude Code) qui lit ce fichier installe un package malveillant (typosquatting, registry non-fiable).

**Hermes et les skills Cortex Leman sont directement exposés** : un README malveillant dans un repo distant, ou une skill externe référencée mais compromise, peut déclencher l'installation de packages compromis via l'agent coding. Les skills externes (anti-ia-humanizer, etc.) constituent une surface d'attaque reconnue.

**Action attendue de Tars:**
1. **Inventorier les skills externes** installées dans le profil Hermes default (et les autres profils si pertinents)
2. Pour chaque skill externe : vérifier la source (repo de confiance ?), l'intégrité (commit hash, signature), les dépendances (`requirements.txt`, `pyproject.toml`)
3. **Ajouter un validateur** : tout `requirements.txt` / `Makefile` / `setup.py` lu par un agent coding doit passer par un validateur de registry + integrity check avant exécution
4. Politique : refuser par défaut les install de packages hors registry connus (pypi.org, npmjs.com)
5. Documenter la politique dans `docs/compliance/POLITIQUE-SUPPLY-CHAIN-SKILLS.md`

**Effort estimé:** 1-2 jours
**Référence arXiv:** https://arxiv.org/abs/2607.15143

---

## TICKET-013 — [P1] Formaliser la politique de validation Skills (Agent Skill Security)

**Menace source:** arXiv 2607.13987 — "Agent Skill Security: Threat Models and Sandboxing" (17/20, ArXiv Daily 19/07 delta)
**Risque compliance:** AI Act Art. 9-10 (Gestion des risques), Art. 14 (Oversight humain), RGPD Art. 25, Art. 32, OWASP LLM07/LLM08
**Note:** **Premier papier académique dédié à la sécurité des systèmes de Skills** — fenêtre early-adopter. Complète TICKET-008 (skills hallucinées) et TICKET-012 (supply-chain).

**Contexte:**
Le papier 2607.13987 formalise pour la première fois les threat models spécifiques aux systèmes de skills d'agents LLM (Hermes Agent Skills, ChatGPT GPTs/Actions, Claude MCP, etc.). Les vecteurs documentés incluent :
- **Skill squatting** — une skill malveillante se positionne sur un nom/profil proche d'une skill légitime
- **Skill poisoning** — modification silencieuse d'une skill installée via update compromise
- **Privilege escalation via skill** — une skill exploite les permissions accordées à l'agent hôte
- **Cross-skill leakage** — une skill accède au contexte/outputs d'une autre skill

**Hermes/Cortex Leman sont directement concernés** : le système de skills est central (le-gardien-des-normes, le-narrateur-augmente, l-architecte-lemanique, etc.), chargé depuis des sources potentiellement externes, avec permissions étendues sur la stack (fichiers, code, cron).

**Action attendue de Tars:**
1. **Politique formelle de validation Skills** — tout ajout/modification de skill doit passer par :
   - Vérification d'intégrité (commit hash, signature, registry de confiance)
   - Sandbox de test (exécution en environnement isolé avant promotion)
   - Revue manuelle du code (permissions demandées, accès réseau/fichiers)
   - Validation du namespace (anti-squatting)
2. **Inventaire complet** des skills installées (cf. TICKET-008) avec pour chacune : source, permissions réelles, date dernière mise à jour
3. **Tests de non-régression** appliquant les 4 vecteurs documentés (squatting, poisoning, privilege escalation, cross-skill leakage)
4. **Logging spécifique** : chaque invocation de skill doit être tracée (Art. 30 RGPD)
5. Documenter la politique dans `docs/compliance/POLITIQUE-VALIDATION-SKILLS.md` (peut être co-écrit avec TICKET-012 supply-chain)

**Effort estimé:** 2-3 jours (politique + inventaire + tests)
**Référence arXiv:** https://arxiv.org/abs/2607.13987

---

## TICKET-014 — [P2] Évaluer 2607.14006 comme socle d'offre "AI Red Team"

**Menace/opportunité source:** arXiv 2607.14006 — "Rethinking Pentest for AI Systems" (42 pages, 17/20, ArXiv Daily 19/07 delta)
**Risque compliance:** AI Act Art. 9 (Gestion des risques), Art. 15 (Robustesse & cybersécurité), Art. 55 (Systèmes GPAI)
**Note:** **Opportunité produit différenciante** — 3 papiers distincts en 7 jours institutionnalisent le pentest IA comme discipline. Premiers movers advantage.

**Contexte:**
Le papier 2607.14006 (42 pages) propose une refonte méthodologique du pentest pour systèmes IA : passage des "objectifs de vulnérabilité" classiques (CVE-like) aux **"behavioral objectives"** — on ne cherche plus des failles d'implémentation mais des comportements IA indésirables (hallucination dirigée, prompt injection cross-contextuelle, jailbreak via tool calls, leakage de prompts système).

Cette discipline émerge en parallèle de :
- arXiv 2607.11698 (Agent Hacks Agent — automatisation) — cf. TICKET-002
- arXiv 2607.14256 (red-team d'agents en production, 17/20)

**Cortex Leman est bien positionné** : nous avons déjà (i) les 5 domaines d'audit du Gardien des Normes, (ii) la veille Threat Intel ArXiv, (iii) la matrice R1-R4. L'offre "AI Red Team" est l'extension naturelle — exécuter les attaques documentées chez le client, pas seulement auditer les défenses.

**Action attendue de Tars:**
1. Lire 2607.14006 en entier (42 pages, méthodologie complète)
2. Évaluer la transposabilité des "behavioral objectives" sur nos 5 domaines d'audit
3. Constituer un catalogue d'attaques testables chez clients PME FR-CH (prompt injection, jailbreak quantization, skill poisoning, memory poisoning, MCP runtime)
4. Préparer un **prototype de livrable "AI Red Team Report"** (format: Executive Summary → Méthodologie → Attaques exécutées → Score de robustesse → Plan de remédiation)
5. Présenter une proposition chiffrée à Thierry (offre standalone ou extension audit compliance)

⚠️ **Note commerciale :** l'offre AI Red Team est différentiable des DPO/conseil RGPD classiques (ils ne savent pas le faire). Pricing premium justifiable. Cf. one-pager créé ce cycle `docs/strategie-2026-07/ONE-PAGER-AI-RED-TEAM.md`.

**Effort estimé:** 3-5 jours (lecture + catalogue + prototype livrable)
**Référence arXiv:** https://arxiv.org/abs/2607.14006

---

## TICKET-015 — [P1] Aligner UX client et mécanisme d'escalade Hermes avec Agent Permission UX (AI Act Art. 14)

**Menace source:** arXiv 2607.13718 — "Agent Permission UX: Designing for Human Oversight" (16/20, ArXiv Daily 19/07 delta)
**Risque compliance:** AI Act Art. 14 (Oversight humain), Art. 26 (Obligations deployeurs), RGPD Art. 22 (Décision automatisée)
**Note:** Convergent avec 2 autres papiers ArXiv (2607.13987, 2607.13718) sur le contrôle humain des agents — refonte UX client nécessaire.

**Contexte:**
Le papier 2607.13718 formalise les patterns UX pour le contrôle humain des agents autonomes. Les patterns identifiés : consentement granulaire par action, transparence d'intention (l'agent annonce ce qu'il va faire avant de le faire), réversibilité (toujours pouvoir annuler), audit trail visible, mécanisme d'escalade clair.

**Applications directes pour Cortex Leman:**

1. **UX client (dashboard + rapports)** — actuellement le client voit le résultat d'audit mais pas le cheminement. Recommandations :
   - Afficher chaque décision IA avec son raisonnement court (cf. TICKET-005 explainability)
   - Bouton "Contester cette décision" visible sur chaque finding (Art. 22 RGPD)
   - Mode "agent actif" : montrer en temps réel ce que fait l'agent (transparence d'intention)

2. **Mécanisme d'escalade Hermes** — actuellement 120 min d'attente puis abort. À enrichir :
   - Distinguer escalade "décision" (l'agent demande une validation) vs escalade "alerte" (un risque a été détecté)
   - Notification plus rapide pour les R3/R4 (timeout 30 min, pas 120)
   - Log visible côté client de chaque escalade (audit trail)

3. **Permission UX chez les clients** — si le client utilise nos agents en autonomie Medium/High, il doit pouvoir :
   - Approuver/refuser chaque envoi client final
   - Suspendre l'agent à tout moment (kill switch accessible, pas enterré dans un menu)
   - Recevoir un récap quotidien des actions effectuées

**Action attendue de Tars:**
1. Lire 2607.13718 — extraire les patterns UX applicables
2. Auditer le dashboard compliance actuel (TICKET-004) contre ces patterns
3. Implémenter le minimum viable : bouton "Contester" + mode "agent actif" + kill switch accessible
4. Adapter le mécanisme d'escalade Hermes (cf. `~/.hermes/agent-harness/policies/autonomy.yaml`) pour distinguer décision vs alerte, et réduire timeout pour R3/R4
5. Documenter les patterns UX dans la checklist compliance (Phase 3 Garde-fous)

**Effort estimé:** 3-4 jours (lecture + audit UX + implémentation MVP)
**Référence arXiv:** https://arxiv.org/abs/2607.13718

---

## TICKET-016 — [P1] Évaluer Cognitive Firewall comme architecture zero-trust multi-gate (LLM safety)

**Menace source:** arXiv 2607.01277 — "Cognitive Firewall: Zero-Trust Multi-Gate Framework for LLM Safety" (17/20, ArXiv Daily 20/07, IMMÉDIAT)
**Risque compliance:** AI Act Art. 15 (Robustesse & cybersécurité), RGPD Art. 32 (Sécurité), DPIA Art. 35 si autonomie High
**Note:** Architecture de référence pour durcir L'Oeil de Cortex et les agents en production.

**Contexte:**
Le papier 2607.01277 formalise une architecture zero-trust à portes multiples (multi-gate) pour les LLM en production : chaque requête traverse plusieurs filtres indépendants (sanitization entrée, classification d'intention, validation de sortie, détection d'injection) avant d'atteindre l'utilisateur final ou un outil à effet externe. Chaque porte applique le principe du moindre privilège et logge systématiquement.

**Cortex Leman est directement concerné :**
- L'Oeil de Cortex traite des contenus non fiables (web scrapé, documents clients)
- Les agents (Gardien, Ingénieur de Flux) ont accès à des outils avec effets externes (email, API)
- Le mécanisme actuel (`shared_ai_safety/guardrails.py`) est mono-gate (RiskClassifier → allow/deny)

**Action attendue de Tars:**
1. Lire 2607.01277 — extraire le pattern multi-gate (5+ portes typiques)
2. Comparer avec le guardrail actuel (`shared_ai_safety/guardrails.py` : PromptSanitizer + RateLimiter + SecurityGuardrails)
3. POC : ajouter 2 portes critiques manquantes — (a) classification d'intention avant exécution d'outil, (b) validation de sortie LLM avant passage à exec/eval (OWASP LLM02)
4. Documenter l'architecture multi-gate dans le registre de traitement (Art. 30) + AIPD si profil high-autonomy
5. Préparer une section "Architecture Cognitive Firewall" pour l'offre AI Red Team (différenciateur technique)

**Effort estimé:** 3-4 jours (lecture + POC + doc)
**Référence arXiv:** https://arxiv.org/abs/2607.01277

---

## TICKET-017 — [P2] Auditer et détecter les checkpoints LLM "abliterated" (refus retirés)

**Menace source:** arXiv 2607.01854 — "Has This Checkpoint Been Abliterated? A Two-Signal Audit and Failure Map" (14/20, ArXiv Daily 20/07, SEMAINE) + arXiv 2607.13162 — "What Models Express, Suppress, and Resist: Auditing Open-Weight LLMs" (13/20)
**Risque compliance:** AI Act Art. 9-10 (Gestion des risques, qualité données), Art. 15 (Robustesse)
**Note:** Opportunité produit — combine avec l'offre AI Red Team pour les PME qui déploient des LLM open-source (Mistral, Llama, Qwen).

**Contexte:**
Le papier 2607.01854 cartographie les checkpoints LLM "abliterated" — des modèles open-weight dont les mécanismes de refus ont été retirés (orthogonalisation, fine-tuning directionnel) pour les rendre "uncensored". Le papier 2607.13162 propose des méthodes d'audit via persona vectors pour détecter ce que les modèles open-weight expriment, suppriment et résistent.

**Pour Cortex Leman :** les PME FR-CH qui déploient des LLM open-source (scénario on-prem, souveraineté, latence) peuvent involontairement utiliser un checkpoint abliterated — ce qui signifie :
- Refus de contenu illicite/haut risque désactivé → AI Act Art. 9-10 non respecté
- Comportement non documenté par le fournisseur → transparence Art. 13 compromise
- Robustesse inconnue → Art. 15 non démontrable

**Action attendue de Tars:**
1. Lire 2607.01854 (deux-signal audit) + 2607.13162 (persona vectors)
2. Reproduire la méthode two-signal sur 3-5 checkpoints open-source populaires chez PME FR-CH (Mistral-7B-Instruct, Llama-3-8B-Instruct, Qwen-2.5 variants)
3. Construire un **catalogue d'audit** : modèle → statut (clean / partiellement ablitéréré / totalement uncensored) → recommandation Art. 9-10
4. Intégrer ce catalogue à l'offre AI Red Team comme module "Vérification de checkpoints"
5. Documenter dans la checklist compliance (Phase 4 — Sécurité technique)

**Effort estimé:** 2-3 jours (méthode + catalogue initial)
**Références arXiv:**
- https://arxiv.org/abs/2607.01854 (abliterated audit)
- https://arxiv.org/abs/2607.13162 (open-weight auditing)

---

## TICKET-018 — [P1] Durcir les primitives de contrôle agent ("Stop Means Stop")

**Menace source:** arXiv 2607.14166 — "Stop Means Stop: Enforcement Gap in Agent-Framework Control Primitives" (15/20, ArXiv Daily 20/07, SEMAINE)
**Risque compliance:** AI Act Art. 14 (Oversight humain), RGPD Art. 22 (Décision automatisée)
**Note:** Convergent avec TICKET-015 (Agent Permission UX) sur le contrôle humain des agents. À traiter conjointement.

**Contexte:**
Le papier 2607.14166 mesure systématiquement les lacunes d'application des primitives de contrôle d'agents ("stop", abort, suspend). Le constat : un pourcentage non-négligeable de frameworks d'agents continuent d'exécuter des actions après réception d'un signal "stop" — soit par design (job en cours non interruptible), soit par bug (race condition, timeout non propagé). Conséquence directe : le kill switch client n'est pas réellement instantané.

**Pour Cortex Leman :**
- Le `autonomy.yaml` Hermes définit un timeout d'escalade (120 min) mais ne garantit pas l'arrêt immédiat
- Les agents en autonomie Medium/High (Gardien des Normes sur dossier sensible, Ingénieur de Flux) doivent pouvoir être interrompus proprement
- Le kill switch client (TICKET-015 Permission UX) ne vaut que si l'arrêt est réellement effectif

**Action attendue de Tars:**
1. Lire 2607.14166 — reproduire le benchmark sur Hermes/Cortex Leman
2. Tester le signal "stop" sur chaque type d'agent : (a) agent one-shot, (b) agent avec boucle tool-use, (c) agent avec job longue durée (cron)
3. Mesurer le temps réel entre signal stop et arrêt effectif (objectif: < 5 secondes pour R3/R4)
4. Si gap > 5s : identifier les points non-interruptibles et ajouter des checkpoints d'annulation
5. Synchroniser avec TICKET-015 (Permission UX) : le bouton "kill switch" client doit être wire au signal stop réel, pas à un placeholder
6. Documenter les performances d'arrêt dans le registre de traitement (Art. 30) et l'AIPD (Art. 35)

**Effort estimé:** 2-3 jours (benchmark + fix éventuel)
**Référence arXiv:** https://arxiv.org/abs/2607.14166

---

## TICKET-019 — [P1] Isolation multi-tenant absente (table `tenants` vide)

**Source:** Rapport Compliance Hebdo W29 (`0dc376b91586`, 20/07) — Alerte #4 HIGH
**Risque compliance:** RGPD Art. 5(1)(f) (confidentialité) + Art. 10 AI Act (qualité données)
**Priorité:** 🔴 **P1** — préalable à toute levée du Kill Switch

**Contexte :**
Le scan de `cortex-leman.db` révèle que la table `tenants` contient **0 rows** malgré 2 events `tenant_onboarded` loggés. **Tous les 12 users ont `tenant_id = NULL`**, ce qui signifie qu'aucun mécanisme d'isolation n'est actif : un user d'une organisation peut potentiellement accéder aux données d'une autre organisation. Pour les verticals à secret absolu (Avocat Art. 321 CP, Banque Art. 47 LB), c'est un manquement structurel grave.

**8 tenants à créer :**
1. `hopital-geneve` (Dr. S. Laurent — Santé)
2. `ubank-sa` (T. Müller — Banque)
3. `martin-avocat` (P. Martin — Avocat)
4. `dupont-comptable` (M. Dupont)
5. `groupe-rh` (J. Moreau)
6. `startup-paris` (L. Dubois)
7. `cortex-leman-internal` (admin)
8. `[individuel]` (J. Callaghan — après correction email `gmail:com → gmail.com`)

**Action attendue de Tars :**
1. **Diagnostiquer** pourquoi les events `tenant_onboarded` ne sont pas persistés dans la table `tenants` (bug d'écriture ? migration manquante ?)
2. **Créer les 8 tenants** avec un script idempotent (au cas où certains existent partiellement)
3. **Assigner chaque user** à son `tenant_id` via migration SQL
4. **Configurer `dpo_email`** par tenant (lookup par domaine email)
5. **Tester l'isolation** : un user du tenant A ne peut PAS voir les données du tenant B (test avec 2 users de tenants différents)
6. **Vérifier le Vault** : chaque tenant a son propre vault isolé (pas de partage de Knowledge Vault inter-tenant)
7. **Documenter** dans audit_logs : `action="tenant_isolation_enable"`

**Effort estimé :** 1-2 jours (diagnostic + migration + tests)
**Deadline :** 3 août 2026 (avant levée Kill Switch)

---

## TICKET-020 — [P1] Capturer les IPs réelles dans audit_logs (middleware + hashing)

**Source:** Rapport Compliance Hebdo W29 (`0dc376b91586`, 20/07) — Alerte #5 HIGH
**Risque compliance:** RGPD Art. 30 (registre des traitements) + Art. 5(2) (traçabilité)
**Priorité:** 🔴 **P1** — préalable à toute investigation CNIL/PFPDT

**Contexte :**
Sur 63 logs dans `audit_logs`, **100% des IPs sont des placeholders** (`None`, `127.0.0.1`, `testclient`). Aucune IP réelle client n'est capturée. Conséquence : en cas d'investigation CNIL ou de litige, il est **impossible de prouver** qui a accédé à quoi et depuis quand. L'audit trail est juridiquement inutilisable.

**Action attendue de Tars :**
1. **Ajouter un middleware FastAPI** qui capture `X-Forwarded-For` (après validation du reverse proxy) ou `request.client.host` en fallback
2. **Hasher l'IP avant stockage** : SHA-256 + sel statique (pour permettre corrélation sans réidentification)
3. **Anonymiser après 13 mois** (recommandation CNIL pour les IPs) via cron de purge
4. **Backfiller les 63 logs existants** avec un marker `ip_source="legacy_placeholder"` pour traçabilité
5. **Tester** : un login réel doit générer un log avec IP hashée non-placeholder
6. **Documenter** dans le registre des traitements (Art. 30) : champ "IP hashée (SHA-256), durée 13 mois"

**Attention :** ne PAS stocker d'IP en clair (minimisation Art. 5(1)(c)), ne PAS utiliser d'IP pour fingerprinting utilisateur (sauf base légale séparée).

**Effort estimé :** 1 jour (middleware + cron + tests)
**Deadline :** 3 août 2026

---

## TICKET-021 — [P2] Évaluer "Zero Hallucination by Construction" (layered oversight) comme pattern d'architecture

**Source:** ArXiv Daily 21/07 (`0f8a90201d56`) — paper 2607.17883, score 12/20, IMMÉDIAT
**Risque compliance:** AI Act Art. 9 (gestion des risques) + Art. 15 (accuracy/robustesse), RGPD Art. 22
**Priorité:** 🟠 **P2** — opportunité d'architecture pour offres régulées

**Contexte :**
Le papier 2607.17883 "Zero Hallucination, by Construction: Hallucination-Aware Layered Oversight for Trustworthy Enterprise AI" propose une architecture d'oversight multi-couches qui élimine les hallucinations par construction plutôt que par post-filtrage. C'est directement applicable aux déploiements clients en environnement régulé (santé, banque, avocat — exactement les 3 verticals qui ont déclenché les alertes CRITICAL W29).

**Pour Cortex Leman :**
- Les verticals Santé et Avocat ont un risque "hallucination" classé 4-5/5 dans leurs AIPD
- Actuellement mitigé par confidence threshold (0.3) + arbitrage humain
- Le pattern layered oversight pourrait remplacer l'arbitrage humain réactif par une détection pro-active multi-couches

**Action attendue de Tars :**
1. Lire 2607.17883 et évaluer la compatibilité avec l'architecture multi-agents Cortex Leman existante (Agent Data → Raisonnement → Action)
2. Identifier si une couche d'oversight peut s'insérer entre Agent Raisonnement et Agent Action
3. POC sur un vertical pilote (recommandé : Avocat — risque hallucination juridique critique)
4. Si concluant : intégrer comme différenciateur dans l'offre "Certification IA Indépendante" (`ONE-PAGER-CERTIFICATION-IA-INDEPENDANTE.md`)

**Effort estimé :** 3-5 jours (évaluation + POC)
**Référence arXiv :** https://arxiv.org/abs/2607.17883

---

## TICKET-022 — [✅ IMPLÉMENTÉ] ChainMark Watermarking AI Act Art. 50

**Source:** ArXiv Daily 22/07 (`0f8a90201d56`) — paper 2607.18445, score **12/20**, IMMÉDIAT
**Risque compliance:** AI Act Art. 50 (transparence contenu synthétique), Art. 12 (documentation)
**Priorité:** ✅ **RÉSOLU** — implémenté le 2026-07-26 (J-7 deadline)
**Voir:** `docs/security/TICKET-022-CHAINMARK-WATERMARKING.md`

**Contexte :**
ChainMark propose un watermarking LLM **model-free** (indépendant du modèle générateur) avec calibration en forme fermée. Les auteurs citent **explicitement l'EU AI Act** comme cadre cible. C'est la technique de référence pour la conformité Art. 50 (marquage machine-lisible du contenu synthétique). Un one-pager commercial associé a été créé : `docs/strategie-2026-07/ONE-PAGER-WATERMARKING-IA-ART-50.md`.

**Pour Cortex Leman :**
- L'Art. 50 AI Act entre en vigueur le 2 août 2026 — tous les clients déployeurs de LLM générant du contenu pour tiers sont concernés
- ChainMark résout le verrou technique : un watermark attaché à un modèle précis ne survit pas au changement de fournisseur → ChainMark est agnostique
- Opportunité produit différenciante : la 5e offre Cortex Leman (watermarking Art. 50) est prête commercialement, il faut la capacité technique

**Action attendue de Tars :**
1. Lire 2607.18445 et évaluer la maturité d'implémentation (code disponible ? licence ?)
2. POC : intégrer ChainMark sur un flux de contenu synthétique de test
3. Évaluer la robustesse du watermark (résistance à la réécriture, à la traduction, au copier-coller)
4. Si concluant : industrialiser comme socle de l'offre watermarking Cortex Leman
5. Documenter dans le registre des traitements (Art. 30) : nouvelle mesure technique de transparence

**Effort estimé :** 3-5 jours (évaluation + POC + recommandation)
**Référence arXiv :** https://arxiv.org/abs/2607.18445
**Lien commercial :** `docs/strategie-2026-07/ONE-PAGER-WATERMARKING-IA-ART-50.md`

---

## TICKET-023 — [P1] Intégrer le survey "Engineering Trustworthy Agentic AI" comme cadre d'audit

**Source:** ArXiv Daily 22/07 (`0f8a90201d56`) — paper 2607.18548, score **12/20**, IMMÉDIAT
**Risque compliance:** AI Act Art. 8-15 (systèmes haut-risque), RGPD Art. 35 (DPIA), Art. 5(2) (accountability)
**Priorité:** 🟠 **P1** — cadre méthodologique structurant pour les audits

**Contexte :**
Survey majeur traitant la **trustworthiness comme propriété de première classe** pour les systèmes agents IA critiques. Modèle en **5 dimensions** : (1) safety/constraints, (2) robustesse, (3) transparence, (4) accountability/auditabilité, (5) privacy et sécurité. Mapping complet sur 4 domaines critiques (énergie, véhicules autonomes, HPC, réseaux). Propose un **framework d'assurance cross-domaine** analogue à la certification graduelle des systèmes safety-critical.

**Pour Cortex Leman :**
- Le rapport ArXiv recommande ce paper comme **référence structurelle pour les audits** Cortex Leman
- Les 5 dimensions du survey **mapping** directement sur les exigences AI Act + RGPD
- Actuellement, les audits Cortex Leman utilisent la checklist 8 phases + 4 dimensions IA (Stanford) — ce survey apporte un cadre d'assurance plus formel (gradué, cross-domaine)
- Différenciateur vs. un audit RGPD classique : capacité à scorer la trustworthiness d'un système agent IA

**Action attendue de Tars :**
1. Lire 2607.18548 et extraire le framework d'assurance (5 dimensions + gradation)
2. Mapper les 5 dimensions sur la checklist compliance existante (`docs/compliance/CHECKLIST-COMPLIANCE-IA.md`)
3. Identifier les gaps : la checklist actuelle couvre-t-elle les 5 dimensions du survey ?
4. Si concluant : adopter comme cadre méthodologique officiel des audits Cortex Leman (mise à jour checklist + matrice R1-R4)
5. Documenter dans la matrice de risques R1-R4 : ajouter une colonne "trustworthiness dimension"

**Effort estimé :** 2-3 jours (lecture + mapping + recommandation)
**Référence arXiv :** https://arxiv.org/abs/2607.18548

---

## TICKET-024 — [P1] Prévention proactive des fuites de données dans les agents IA

**Source:** ArXiv Daily 22/07 (`0f8a90201d56`) — paper 2607.18847, score **11/20**, SEMAINE
**Risque compliance:** RGPD Art. 32 (sécurité du traitement), AI Act Art. 15 (robustesse)
**Priorité:** 🔴 **P1** — critique pour les déploiements agents en production

**Contexte :**
Le papier *Data Leakage Prevention in Agentic Applications via Preemptive Hardening* adresse les fuites de données **proactives** dans les systèmes agents IA via prompt injection et failures de boundary instruction/data. Pertinent pour toute organisation déployant des agents LLM avec outils externes — exactement le cas d'usage des PME FR-CH (agents Cortex Leman avec accès documentaire, API, base de connaissances).

**Pour Cortex Leman :**
- Les agents Cortex Leman (Agent Data → Raisonnement → Action) utilisent des tools externes → surface d'attaque prompt injection
- TICKET-018 (Stop Means Stop) et TICKET-015 (Permission UX) adressent la gouvernance runtime ; ce papier adresse la **prévention des fuites** en amont
- Les 3 verticals CRITICAL W29 (Santé/Banque/Avocat) ont le plus haut risque de fuite de données sensibles

**Action attendue de Tars :**
1. Lire 2607.18847 et évaluer la technique de "preemptive hardening"
2. Identifier les points de boundary instruction/data dans l'architecture multi-agents Cortex Leman
3. Évaluer l'application aux 3 verticals high-risk (Santé/Banque/Avocat)
4. Si concluant : ajouter une couche de hardening proactive avant la levée du Kill Switch
5. Documenter dans les AIPD Santé/Banque/Avocat (mesure technique Art. 32)

**Effort estimé :** 3-5 jours (évaluation + POC)
**Référence arXiv :** https://arxiv.org/abs/2607.18847

---

## TICKET-025 — [P2] Adopter un framework quantitatif de risque résiduel (CPSAINT/FRIESA-K)

**Source:** ArXiv Daily 22/07 (`0f8a90201d56`) — paper 2607.18243, score **10/20**, SEMAINE
**Risque compliance:** AI Act Art. 9 (gestion des risques pour systèmes haut-risque)
**Priorité:** 🟠 **P2** — opportunité méthodologique

**Contexte :**
Le papier *From Agent Failure Paths to Quantified Residual Risk* propose **CPSAINT** : décomposition d'intégrité en 7 couches (Physical, Sensors, Data, Compute, Actuators, Environment, Time) + **FRIESA-K**, un fonctionnel de risque résiduel qui mappe chaque failure path à une instance de risque quantifié. Démontre la composabilité structurelle sur 2 cas contrastés (robot warehouse + agent financier governance-instrumenté).

**Pour Cortex Leman :**
- Actuellement, la matrice R1-R4 est **déterministe** (patterns regex) mais **non quantifiée** en risque résiduel
- FRIESA-K pourrait fournir un score quantitatif de risque résiduel par agent — différenciateur d'audit
- Le cas "agent financier governance-instrumenté" est directement applicable aux verticals Banque/Avocat

**Action attendue de Tars :**
1. Lire 2607.18243 et évaluer la transposabilité de FRIESA-K au contexte Cortex Leman
2. Évaluer si les 7 couches CPSAINT s'appliquent aux agents IA software-only (vs. robots physiques)
3. POC : scorer un agent Cortex Leman existant avec FRIESA-K
4. Si concluant : intégrer comme dimension quantiative dans la matrice R1-R4

**Effort estimé :** 3-5 jours (évaluation + POC)
**Référence arXiv :** https://arxiv.org/abs/2607.18243

---

## TICKET-026 — [P2] Évaluer Sarus (homomorphic encryption) comme pattern privacy-by-design

**Source:** ArXiv Daily 22/07 (`0f8a90201d56`) — paper 2607.19146, score **10/20**, SEMAINE
**Risque compliance:** RGPD Art. 25 (privacy by design), AI Act Art. 10 (qualité données)
**Priorité:** 🟠 **P2** — opportunité architecture

**Contexte :**
Le papier *Sarus: Privacy-Preserving Multi-Vendor Perception Fusion via Homomorphic Encryption* protège les modèles propriétaires tout en permettant la collaboration multi-fournisseurs via **homomorphic encryption**. Architecture applicable au-delà des véhicules autonomes (cas original).

**Pour Cortex Leman :**
- Privacy-by-design (Art. 25 RGPD) est une exigence structurelle, pas une option
- L'homomorphic encryption pourrait permettre des audits cross-tenant sans exposition de données — pertinent pour l'isolation multi-tenant (cf. TICKET-019)
- Cas d'usage : fusion de données Santé/Banque pour scoring risque sans exposer les données sensibles Art. 9

**Action attendue de Tars :**
1. Lire 2607.19146 et évaluer la maturité (le HE est-il production-ready pour PME ?)
2. Évaluer le coût computationnel (le HE est historiquement coûteux)
3. Identifier si un cas d'usage Cortex Leman justifie l'investissement (ex. fusion Santé + Finance pour un client)
4. Si concluant : POC sur un vertical pilote

**Effort estimé :** 2-3 jours (évaluation)
**Référence arXiv :** https://arxiv.org/abs/2607.19146

---

## TICKET-027 — [P1] Sécuriser les agents auto-hébergés (cluster Chronos + Self-State + CI/CD)

**Source:** ArXiv Daily 25/07 (`0f8a90201d56`) — cluster émergent "self-hosted agent security", 4 papiers R≥8
- 2607.19433 (Chronos Vulnerability, R:9) — persistance temporelle + memory deception
- 2607.17986 (Self-State Attacks, R:9) — attaques sur l'état interne, limites des défenses OS
- 2607.18063 (Adaptive Adversaries, R:9) — benchmark attaques multi-tours multi-LLM
- 2607.19267 (Trusted CI/CD Pipeline as Attack Surface, R:9) — détournement de CI/CD agentique

**Risque compliance:** RGPD Art. 32 (sécurité), AI Act Art. 15 (robustesse), Art. 14 (supervision humaine)
**Priorité:** 🟠 **P1** — nouveau vecteur critique pour clients on-prem FR-CH

**Contexte :**
Un cluster cohérent de 4 papiers ArXiv (tous R≥8, publiés sur 5 jours) révèle que **les défenses OS traditionnelles sont insuffisantes pour les agents IA auto-hébergés**. Trois vecteurs nouveaux sont documentés :

1. **Persistance temporelle (Chronos)** — un attaquant peut planter un payload déclenchable ultérieurement dans la mémoire long-terme de l'agent, invisible au moment de l'audit.
2. **Attaques sur l'état interne (Self-State)** — compromission du runtime agent (variables, contexte, call stack) qui contourne les sandbox OS classiques.
3. **CI/CD comme surface d'attaque** — les pipelines de déploiement agentique (GitHub Actions, GitLab CI) peuvent être dévoyés pour injecter du comportement malveillant au moment du build, validé par les tests mais actif en prod.

**Pour Cortex Leman :**
- Les verticals Santé/Banque/Avocat sont précisément les candidats au déploiement on-prem (souveraineté des données Art. 9) → **exposition directe**
- L'agent Hermes lui-même tourne on-prem chez Tars → **risque interne direct**
- La fenêtre commerciale : positionner Cortex Leman comme l'offre de référence pour "agent IA auto-hébergé sécurisé" en FR-CH

**Action attendue de Tars :**
1. Lire les 4 papiers (2607.19433, 2607.17986, 2607.18063, 2607.19267) et cartographier les vecteurs applicables à la stack Cortex Leman
2. Auditer le runtime Hermes : où est stocké l'état agent ? Quelle isolation ? Quelle surface CI/CD ?
3. Tester la persistance temporelle (Chronos) sur un agent de test — un payload peut-il survivre à un redémarrage ?
4. Durcir le pipeline de build (signature des artefacts, SBOM IA — cf. TICKET-028)
5. Documenter les résultats dans un AIPD si l'agent traite des données Art. 9

**Effort estimé :** 4-6 jours (audit + tests de pénétration internes)
**Références arXiv :**
- https://arxiv.org/abs/2607.19433
- https://arxiv.org/abs/2607.17986
- https://arxiv.org/abs/2607.18063
- https://arxiv.org/abs/2607.19267

---

## TICKET-028 — [✅ IMPLÉMENTÉ] Adopter un AI SBOM (AI Bill of Materials) pour la chaîne de modèles

**Source:** ArXiv Daily 25/07 (`0f8a90201d56`) — paper 2607.17242, score **8/20**, SEMAINE
**Risque compliance:** AI Act Art. 11 (documentation technique), Art. 13 (transparence), RGPD Art. 30 (registre)
**Priorité:** 🟠 **P1** — émergent réglementaire

**Contexte :**
Le papier *A Large-Scale Measurement of AI Bill of Materials Completeness* (HuggingFace, 2607.17242) mesure la complétude des "AI SBOM" sur le hub HuggingFace et constate que la majorité des modèles publiés **n'exposent pas les métadonnées requises** pour traçabilité (données d'entraînement, dépendances, licences). L'AI Act Art. 11 et Art. 13 exigent cette transparence pour les systèmes haut-risque.

**Pour Cortex Leman :**
- Nos audits clients incluent l'inventaire des modèles utilisés — un AI SBOM standardisé serait un livrable différenciant
- Cortex Leman utilise elle-même plusieurs modèles (GLM-5, Claude, GPT, modèles open-source via Apify/n8n) → notre propre AI SBOM est un prérequis de crédibilité
- Convergent avec TICKET-022 (ChainMark watermarking) et TICKET-027 (CI/CD agent security)

**Action attendue de Tars :**
1. Lire 2607.17242 et identifier le format AI SBOM standardisé (SPDX / CycloneDX extension IA)
2. Générer l'AI SBOM interne Cortex Leman (modèles utilisés, versions, fournisseurs, juridictions, transferts cross-border)
3. Intégrer l'AI SBOM comme livrable standard des audits clients (Template)
4. Vérifier la conformité AI Act Art. 11/13 de chaque modèle utilisé

**Effort estimé :** 2-3 jours (évaluation + template + SBOM interne)
**Référence arXiv :** https://arxiv.org/abs/2607.17242

---

## TICKET-029 — [P2] Évaluer RAIL Guard comme socle de la boucle évaluation→remédiation Cortex Leman

**Source:** ArXiv Daily 25/07 (`0f8a90201d56`) — paper 2607.16215, score **11/20**, IMMÉDIAT
**Risque compliance:** AI Act Art. 17 (corrective actions), Art. 9(2)(g), RGPD Art. 5(2) (accountability)
**Priorité:** 🟡 **P2** — opportunité méthodologique

**Contexte :**
Le papier *RAIL Guard: Closing the Evaluation-to-Remediation Gap in Responsible AI* connecte l'évaluation des risques des agents LLM à des actions de remédiation concrètes, au lieu de simples rapports. Ferme le gap entre "detect problems" et "fix problems".

**Pour Cortex Leman :**
- Notre offer actuelle produit des rapports + plans d'action — mais **le suivi de l'exécution des remédiations n'est pas outillé**
- RAIL Guard pourrait devenir le socle d'un module "Suivi remédiation" récurrent (revenue stream)
- Convergent avec le constat interne : la deadline CRITICAL est dépassée faute de boucle de remédiation outillée

**Action attendue de Tars :**
1. Lire 2607.16215 et évaluer la maturité (framework ouvert ? implémentation de référence ?)
2. POC : appliquer RAIL Guard au suivi interne des 5 actions CRITICAL non exécutées
3. Si concluant : industrialiser comme module de l'offre "Certification IA Indépendante"

**Effort estimé :** 2-3 jours (évaluation + POC)
**Référence arXiv :** https://arxiv.org/abs/2607.16215

---

## ARCHIVE — Tickets résolus

*(Vide)*

---

*Pour exécuter un ticket: Tars doit créer une branche `fix/TICKET-XXX`, implémenter le fix, tester, et merger selon le workflow git du projet.*
