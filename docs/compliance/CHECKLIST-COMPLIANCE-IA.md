# Checklist Compliance IA — Cortex Leman

> **Version:** 1.0 — 2026-07-14
> **Usage:** À compléter avant tout déploiement d'un système IA chez un client PME FR-CH
> **Source:** Le Gardien des Normes + Veille Threat Intel ArXiv 2026-07-14
> **Références:** `MATRICE-RISQUES-R1-R4.md`, `AIPD-TEMPLATE.md`, `security_audit_owasp.md`

---

## Phase 1 — Identification du système IA

- [ ] **Rôle AI Act identifié** (Fournisseur / Déployeur / Importateur / Distributeur)
- [ ] **Niveau d'autonomie IA défini** (Low / Medium / High)
  - Low = Humain approuve chaque action (+0 risque)
  - Medium = Agent agit, humain révise (+2 risque)
  - High = Agent autonome, alertes exceptions (+5 risque, DPIA obligatoire)
- [ ] **Type d'architecture IA** (RAG / Fine-tuning / Hybride)
  - Si fine-tuning: justification documentée (cf. exceptions acceptables)
- [ ] **Domaine de risque** identifié (juridique / RH / santé / finance / retail / public)

---

## Phase 2 — Classification du risque (R1-R4)

> Voir `docs/compliance/MATRICE-RISQUES-R1-R4.md` pour les patterns complets

- [ ] Scan R4_CRITICAL effectué (conflit d'intérêts, partie adverse, santé, mineurs, données financières)
- [ ] Scan R3_HIGH effectué (PII détectée, sensibilité élevée, transfert international non documenté)
- [ ] Scan R2_MODERATE effectué (interaction client, document contractuel, communication externe)
- [ ] **Niveau de risque final assigné:** [ R1 / R2 / R3 / R4 ]
- [ ] Si R3 ou R4: DPIA/AIPD en place (`docs/compliance/AIPD-TEMPLATE.md`)

---

## Phase 3 — Garde-fous obligatoires

### Niveau 1 — Transparence (Art. 52 AI Act)
- [ ] L'utilisateur sait qu'il interagit avec une IA
- [ ] Mention explicite dans l'interface (chatbot, assistant, API)

### Niveau 2 — CG + Supervision humaine (Art. 7 RGPD, Art. 14 AI Act)
- [ ] Conditions générales mentionnent les risques d'hallucination
- [ ] CG mentionnent la nécessité de vérifier les outputs IA
- [ ] Supervision humaine obligatoire avant envoi au client final
- [ ] Workflow de validation humaine documenté

### Niveau 3 — Documentation technique (Art. 35 RGPD, Art. 6-9 AI Act)
- [ ] DPIA/AIPD complétée si autonomie High ou domaine haut risque
- [ ] Documentation technique complète du système IA
- [ ] Logo conformité européenne (si fournisseur AI Act)
- [ ] Traces LLM complètes (prompt, réponse, appel d'outil) — Art. 30 RGPD

---

## Phase 4 — Sécurité technique

### OWASP Top 10 (A01-A10)
- [ ] Pas de routes sans authentification (A01)
- [ ] Pas de secrets codés en dur (A02)
- [ ] Pas d'injection SQL/commande/eval (A03)
- [ ] Rate limiting en place (A04)
- [ ] Debug=False en production (A05)
- [ ] Dépendances à jour (A06)
- [ ] JWT vérifiés, sessions sécurisées (A07)
- [ ] Pas de désérialisation non sécurisée (A08)
- [ ] Pas de données sensibles dans les logs (A09)
- [ ] Pas de SSRF vers URLs user-controlled (A10)

### OWASP LLM Top 10 (LLM01-LLM10)
- [ ] Guardrails anti-prompt-injection en place (LLM01)
- [ ] Output LLM validé avant passage à exec/eval (LLM02)
- [ ] Pas de données sensibles dans les prompts (LLM06)
- [ ] Plugins sandboxés, permissions minimales (LLM07)
- [ ] Pas d'agency excessive (HITL sur outils critiques) (LLM08)
- [ ] Pas de confiance aveugle dans les outputs (LLM09)

### Veille Threat Intel (ArXiv 2026-07-14 → 2026-07-18)
- [ ] **Si pipeline vision/VLA:** robustesse adversariale testée (THREAT-001, arXiv 2607.11560)
- [ ] **Si agents autonomes:** red-teaming effectué (THREAT-002, arXiv 2607.11698)
- [ ] **Si architecture multi-agents:** intégrité des composants vérifiée (THREAT-003, arXiv 2607.11751)
- [ ] **Si RL dans le pipeline:** claims de risque audités (THREAT-004, arXiv 2607.11607)
- [ ] **Si modèle quantifié déployé (edge/on-prem):** protocole JADR exécuté (arXiv 2607.12792, TICKET-007)
- [ ] **Si registre de skills ouvert:** skills hallucinées filtrées (arXiv 2607.12340, TICKET-008)

### Veille Threat Intel — ArXiv 18/07/2026 (mise à jour cycle)
- [ ] **Mémoire agent cross-session audité** contre Bad Memory / MemPoison (arXiv 2607.14611, 2607.14651 — 1227 cas documentés, **TICKET-010 P0**). Obligatoire dès qu'un agent persiste un état entre sessions.
- [ ] **Serveurs MCP validés runtime** via FlowGuard (arXiv 2607.14754, **TICKET-011 P1**). Obligatoire pour tout serveur MCP en usage (Apify, n8n) et tout nouveau MCP tierce.
- [ ] **Skills externes validées** (source + intégrité + dépendances) avant installation (arXiv 2607.15143, **TICKET-012 P2**). Politique supply-chain documentée.
- [ ] **Trade-off fairness↔privacy audité** si modèle client en healthcare/finance/legal (arXiv 2607.14607 — 20/20). Les algorithmes fairness peuvent *augmenter* les risques membership inference au niveau subpopulation.
- [ ] **Socle d'observabilité OpenTelemetry** en place si autonomie Medium/High (Traccia, arXiv 2607.14309 — 20/20, **TICKET-009 P1**). Couvre AI Act Art. 12 (Logging).

### Veille Threat Intel — ArXiv 19/07/2026 (delta weekend, mise à jour cycle)
- [ ] **Politique formelle de validation Skills** en place (anti-squatting + anti-poisoning + sandbox + revue manuelle). Premier papier académique dédié (arXiv 2607.13987 — 17/20, **TICKET-013 P1**). Obligatoire pour toute installation/modification de skill Hermes.
- [ ] **UX client alignée avec Agent Permission UX** (AI Act Art. 14) : consentement granulaire par action, bouton "Contester" visible (RGPD Art. 22), kill switch accessible, mode "agent actif" (arXiv 2607.13718 — 16/20, **TICKET-015 P1**).
- [ ] **Audit Value Leakage / biais implicites LLM** effectué (arXiv 2607.14345 — 16/20). Les LLM leakent des valeurs implicites non-visibles pour l'utilisateur. À intégrer à l'audit éthique Gardien des Normes pour modèles clients.
- [ ] **Métriques cost-aware de sécurité** intégrées au ROI compliance MSSP/SOC (arXiv 2607.15263 — 17/20). Le benchmark économique des agents de sécurité guide les recommandations client.

### Veille Threat Intel — ArXiv 20/07/2026 (mise à jour cycle)
- [ ] **Architecture Cognitive Firewall (zero-trust multi-gate)** évaluée pour les agents en production (arXiv 2607.01277 — 17/20, **TICKET-016 P1**). Pattern : plusieurs portes indépendantes (sanitization entrée, classification intention, validation sortie). Au-delà du guardrail mono-gate actuel.
- [ ] **Checkpoints LLM open-weight audités** contre "abliteration" (retrait de refus) si déploiement on-prem/client (arXiv 2607.01854 + 2607.13162, **TICKET-017 P2**). Obligatoire pour Mistral/Llama/Qwen avant recommandation client (AI Act Art. 9-10).
- [ ] **Primitives "Stop Means Stop" testées** : temps réel entre signal stop et arrêt effectif de l'agent < 5 secondes pour R3/R4 (arXiv 2607.14166 — 15/20, **TICKET-018 P1**). Converge avec TICKET-015 Permission UX.
- [ ] **Protection RAG sous requêtes dynamiques** réévaluée (arXiv 2607.14811 — 16/20). La protection DB n'est pas statique — adversaire peut reconstruire des données privées via multi-query. Impact direct sur architecture RAG clients.
- [ ] **Attaque KidnapRAG** testée si RAG agent en production (arXiv 2607.00422 — 15/20). Détournement du raisonnement en boîte noire. À intégrer à l'offre AI Red Team.
- [ ] **Disclosure Divergence auditée** chez clients : décalage entre politique de confidentialité affichée et pratiques effectives de Data Safety (arXiv 2607.14442 — 15/20). Transparence Art. 13 RGPD + Art. 50 AI Act.
- [ ] **Watermarking IA** non considéré comme preuve forensique suffisante (arXiv 2607.16010 — 15/20). À ne PAS recommander seul comme solution anti-AI générique chez les clients. Mesures complémentaires obligatoires.

---

## Phase 5 — Données personnelles (RGPD)

- [ ] Base légale de collecte identifiée (Art. 5, 6, 13)
- [ ] Consentement libre, éclairé, spécifique (Art. 7) — si basé sur consentement
- [ ] Droit à l'oubli implémenté (Art. 17) — RAG: suppression dans l'index
- [ ] Chiffrement des données au repos et en transit (Art. 25, 32)
- [ ] Registre des traitements à jour (Art. 30) — inclut traces LLM
- [ ] Transferts internationaux documentés (Art. 44-49) — API US: garanties requises
- [ ] Procédure de violation de données (Art. 33-34) — notification 72h

---

## Phase 6 — Évaluation et traçabilité

### Évaluations obligatoires (Stanford CS230 / RGPD Art. 22, 35)
- [ ] **Evals composants (objectifs):** assertions Python sur chaque composant du pipeline
- [ ] **Evals composants (subjectifs):** LLM judge sur ton, complétude (rubrique 1-5)
- [ ] **Evals end-to-end (objectifs):** workflow complet testé, DB update correcte
- [ ] **Evals end-to-end (subjectifs):** humains notent la conversation complète
- [ ] **Timing par composant:** durée de chaque étape du pipeline mesurée

### Outils recommandés
- [ ] Solution de tracing choisie et configurée (LangSmith / Braintrust / Helicone / Arize)

---

## Phase 7 — Kill Switch

- [ ] Kill Switch implémenté et testé
- [ ] Procédure de blocage R4_CRITICAL fonctionnelle
- [ ] Alerte automatique au Gardien des Normes + Responsable de Traitement
- [ ] Escalade vers intervention humaine configurée
- [ ] Log de sécurité (SecurityEvent) créé et stocké

---

## Phase 8 — Sign-off

| Champ | Valeur |
|-------|--------|
| **Client** | `[NOM CLIENT]` |
| **Système IA audité** | `[DESCRIPTION]` |
| **Score de conformité** | `[0.00 - 1.00]` |
| **Niveau de risque final** | `[R1/R2/R3/R4]` |
| **Date d'audit** | `[DATE]` |
| **Auditeur** | Le Gardien des Normes (Cortex Leman) |
| **Validation humaine** | `[Nom + signature]` |

### Score de conformité

```
Score = (checklist items conformes / total items applicables) × 1.00
```

| Score | Statut | Action |
|-------|--------|--------|
| ≥ 0.96 | EXCELLENT | Déploiement autorisé |
| 0.81-0.95 | BON | Déploiement autorisé avec corrections mineures |
| 0.61-0.80 | ACCEPTABLE | Corrections nécessaires avant déploiement |
| 0.31-0.60 | INSUFFISANT | Corrections urgentes, déploiement bloqué |
| ≤ 0.30 | CRITIQUE | Déploiement bloqué, Kill Switch considéré |

---

## Phase 9 — Mesures Threat Intel 2026-07-21 (ArXiv Daily 21/07 + Compliance W29)

### 9.1 Détection de biais covert (Value Leakage — 2607.14345)

- [ ] **Audit Value Leakage effectué** sur le/les modèles utilisés (Claude, GPT, Gemini) — compare CoT affiché vs influence réelle
- [ ] **Documentation des biais covert** identifiés dans le dossier de conformité AI Act Art. 50
- [ ] **Information des utilisateurs** que les conseils générés peuvent refléter des valeurs non-divulguées (Art. 13 RGPD)
- [ ] **Supervision humaine** renforcée sur les cas d'usage sensibles (RH, juridique, financier)

### 9.2 Architecture "Zero Hallucination by Construction" (2607.17883)

- [ ] **Évaluation du pattern layered oversight** pour les verticals à risque hallucination critique (Santé, Avocat)
- [ ] **POC sur 1 vertical pilote** (recommandé Avocat) avant intégration au standard Cortex Leman

### 9.3 Gouvernance comparée (Global Index Responsible AI 2026 — 2607.14782)

- [ ] **Positionnement FR-CH documenté** face au benchmark international (retard Suisse/France vs Canada/UK)
- [ ] **Référence GIRAI 2026** intégrée à l'argumentaire commercial Cortex Leman

### 9.4 Sécurité post-quantum anticipatoire (2607.17573 — DW-HKEM)

- [ ] **Veille post-quantum** activée pour verticals Banque/Finance (migration ML-KEM)
- [ ] **Échéance migration** identifiée (NIS2 + RGPD Art. 32 implicite)

### 9.5 Provenance et watermarking (2607.16648)

- [ ] **Fingerprinting algébrique** évalué pour traçabilité outputs IA (Art. 50 AI Act watermarking deepfakes)
- [ ] **Complément au watermarking forensique** (défaillant selon 2607.16010) — ne pas s'y fier seul

### 9.6 Explicabilité Prolog (2607.15459)

- [ ] **Explicabilité exécutable** évaluée pour les décisions automatisées RGPD Art. 22 (sortie "logique Prolog" plutôt que texte vague)
- [ ] **Intégration possible** dans le module Agent Raisonnement Cortex Leman

---

## Phase 10 — Mesures issues du Compliance Hebdo W29 (Alertes CRITICAL/HIGH)

> ⚠️ Ces mesures sont des **pré-requis à la levée du Kill Switch** et à toute reprise d'activité. Voir `PROCEDURE-REMÉDIATION-CRITICAL-2026-07-21.md`.

### 10.1 Authentification multi-facteurs (MFA) — Alerte #1, #2, #3

- [ ] **MFA TOTP activée** sur 100% des comptes (12/12 users)
- [ ] **Priorité SANTE → BANQUE → AVOCAT → ADMIN** respectée
- [ ] **SMS interdit** pour les comptes Art. 9 RGPD (TOTP obligatoire)
- [ ] **MFA documentée** dans le registre des traitements (Art. 30)

### 10.2 Isolation multi-tenant — Alerte #4

- [ ] **Table `tenants` peuplée** (8 organisations identifiées)
- [ ] **`tenant_id` non-NULL** sur 100% des users
- [ ] **`dpo_email` configuré** par tenant
- [ ] **Isolation testée** : user A ne peut pas voir données tenant B
- [ ] **Vault isolé** par tenant (pas de partage Knowledge Vault)

### 10.3 Cross-border CH→EU — Alerte #3

- [ ] **Mécanisme de transfert documenté** pour chaque client `.ch` (CSC ou décision d'adéquation)
- [ ] **CSC 2021/914** signées entre Cortex Leman et les 3 clients suisses concernés
- [ ] **Tombeau suisse (FADP)** vérifié pour le sens CH→UE

### 10.4 Capture IP réelle — Alerte #5

- [ ] **Middleware FastAPI** capture `X-Forwarded-For` validé
- [ ] **IP hashée (SHA-256 + sel)** avant stockage
- [ ] **Anonymisation après 13 mois** (cron de purge)
- [ ] **Backfill** des 63 logs existants avec marker `ip_source="legacy_placeholder"`

### 10.5 DPIA/AIPD verticals high-risk — Alerte #6

- [ ] **AIPD Santé** validée (Dr. Laurent — voir `AIPD-DRAFT-SANTE-LAURENT-2026-07-21.md`)
- [ ] **AIPD Banque** validée (T. Müller — voir `AIPD-DRAFT-BANQUE-UBANK-2026-07-21.md`)
- [ ] **AIPD Avocat** validée (P. Martin — voir `AIPD-DRAFT-AVOCAT-MARTIN-2026-07-21.md`)

### 10.6 Qualité des données — Alerte #7

- [ ] **Validation format email** à l'inscription (regex + SMTP check)
- [ ] **Correction enregistrement invalide** `jame.callaghan@gmail:com` → `gmail.com`

### 10.7 Garde-fous IA (3 niveaux) — Alerte phases 3 du rapport

- [ ] **Niveau 1 — Transparence** (Art. 52 AI Act) : bannière "vous interagissez avec une IA"
- [ ] **Niveau 2 — CG** : conditions générales mentionnant hallucinations + supervision humaine obligatoire
- [ ] **Niveau 3 — Documentation technique** : DPIA + doc AI Act Art. 11 pour les high-risk

### 10.8 Politique de rétention par vertical

- [ ] **Profil de rétention** défini par vertical (pas 365j uniforme)
- [ ] **Santé : 20 ans** (CSP), **Banque : 10 ans** (LBA), **Avocat : 10 ans** (déontologique), **Standard : 365j**

---

## Phase 11 — Procédure de violation (notification < 72h)

- [ ] **Procédure documentée** notification CNIL < 72h (Art. 33 RGPD)
- [ ] **Procédure documentée** notification PFPDT < 72h (LPD Suisse)
- [ ] **Procédure documentée** notification FINMA (Banque CH) si applicable
- [ ] **Procédure documentée** notification ARS (Santé FR) si applicable
- [ ] **Procédure documentée** notification Bâtonnier (Avocat CH) si applicable
- [ ] ** Registre des violations** tenu à jour (Art. 33(5) RGPD)
- [ ] **Test de la procédure** effectué (simulation 1x/an)

---

*Checklist enrichie le 2026-07-21 — Exécutant Cortex Leman. Les Phases 9-11 consolident les mesures Threat Intel ArXiv 18-21/07 et les gaps détectés par le Compliance Hebdo W29.*

---

## Phase 12 — Mesures Threat Intel cycle 2026-07-22

> **Source :** ArXiv Daily Report 2026-07-22 (`0f8a90201d56`, run 11:36, 5 papers R ≥ 10)
> **Tickets associés :** TICKET-022 à 026

### 12.1 Transparence du contenu synthétique (AI Act Art. 50) — J-11

- [ ] **Watermarking machine-lisible** du contenu synthétique évalué (ChainMark, 2607.18445 — cf. TICKET-022)
- [ ] **Bannière de transparence** "vous interagissez avec une IA" déployée sur tous les chatbots/assistants clients
- [ ] **Inventaire des flux de contenu synthétique** réalisé (quels LLM, quelles sorties, quels canaux)
- [ ] **Procédure de vérification continue** du marquage actif documentée

### 12.2 Framework trustworthiness (5 dimensions) — Cadre d'audit

- [ ] **5 dimensions trustworthiness** intégrées dans la checklist : (1) safety/constraints, (2) robustesse, (3) transparence, (4) accountability/auditabilité, (5) privacy/sécurité (2607.18548 — cf. TICKET-023)
- [ ] **Mapping** des 5 dimensions sur les exigences AI Act Art. 8-15 effectué
- [ ] **Score trustworthiness** par système agent IA audité

### 12.3 Prévention des fuites de données agents (Art. 32 RGPD)

- [ ] **Boundary instruction/data** cartographiée pour chaque agent Cortex Leman avec tools externes (2607.18847 — cf. TICKET-024)
- [ ] **Hardening préventif** contre prompt injection évalué sur les 3 verticals high-risk (Santé/Banque/Avocat)
- [ ] **Test de fuite de données** effectué sur les agents en production

### 12.4 Risque résiduel quantifié (AI Act Art. 9)

- [ ] **Score de risque résiduel** FRIESA-K évalué pour au moins un agent par vertical (2607.18243 — cf. TICKET-025)
- [ ] **7 couches CPSAINT** évaluées pour les agents software-only (Data, Compute, Time pertinentes)

### 12.5 Monitoring continu (AI Act Art. 17) — Signal émergent

- [ ] **Safety Drift** (2607.18366) évalué : détection de l'érosion des garanties de sécurité au fil des interactions multi-turn
- [ ] **Alerting sur dérive** de comportement agent configuré pour les systèmes high-risk

---

## Phase 13 — Mesures Threat Intel cycle 2026-07-25

> **Source :** ArXiv Daily Report 2026-07-25 (`0f8a90201d56`, run 09:11, cluster self-hosted agent security + AI SBOM + RAIL Guard)
> **Tickets associés :** TICKET-027, 028, 029
> **Caractéristique du cycle :** rapport "delta week-end" complet (`show=1000`) révèle **3 nouveaux clusters** non couverts par les cycles précédents — la pagination limitée à 50 manquait ~64% des signaux.

### 13.1 Sécurité runtime agents auto-hébergés (AI Act Art. 15, RGPD Art. 32)

- [ ] **Persistance temporelle (Chronos)** testée sur les agents on-prem : un payload dormant peut-il survivre à un redémarrage ? (2607.19433 — cf. TICKET-027)
- [ ] **État interne agent** audité : surface d'attaque sur les variables, contexte, call stack (2607.17986 — Self-State Attacks)
- [ ] **Robustesse multi-tours** testée : les guardrails résistent-ils aux attaques adaptatives multi-LLM ? (2607.18063 — Adaptive Adversaries)
- [ ] **Surface CI/CD** auditée : signature des artefacts de build, détection d'injection au moment du déploiement (2607.19267)
- [ ] **Sandbox runtime** évalué : les défenses OS classiques sont insuffisantes pour agents IA — isolation renforcée documentée

### 13.2 AI SBOM (AI Act Art. 11, 13 — documentation technique)

- [ ] **Format AI SBOM** standardisé (SPDX / CycloneDX extension IA) choisi (2607.17242 — cf. TICKET-028)
- [ ] **AI SBOM interne Cortex Leman** généré : modèles utilisés, versions, fournisseurs, juridictions, transferts cross-border
- [ ] **AI SBOM client** intégré comme livrable standard des audits (Template)
- [ ] **Conformité Art. 11/13** vérifiée pour chaque modèle utilisé (traçabilité données d'entraînement, dépendances, licences)

### 13.3 Boucle évaluation→remédiation (AI Act Art. 17, RGPD Art. 5(2))

- [ ] **RAIL Guard** (2607.16215 — cf. TICKET-029) évalué comme socle du suivi de remédiation
- [ ] **Suivi des actions de remédiation** outillé (le gap actuel : les rapports sont produits, l'exécution des remédiations n'est pas tracée systématiquement)
- [ ] **Re-test post-remédiation** systématisé pour les alertes CRITICAL (cf. deadline interne dépassée — STATUT-DEADLINE-CRITICAL-2026-07-25)

### 13.4 Vision & Biométrie — nouveaux vecteurs physiques (RGPD Art. 9)

- [ ] **Attaques EMI sur reconnaissance faciale** évaluées pour tout système biométrique client (2607.15512, R:9)
- [ ] **Faux souvenirs visuels** (2607.15657, R:9) : si agent IA à mémoire long-terme multimodale, test d'injection de faux souvenirs
- [ ] **CrackedPDFs** (2607.19396, R:8) : si pipeline de traitement PDF, détection d'injection de prompt caché dans les PDF
- [ ] **Forensique documents** (compétition ID-cards/passports, 2607.15734) : état de l'art intégré pour clients avec KYC

### 13.5 Guardrails & Hallucinations — nouvelles limites (AI Act Art. 14)

- [ ] **Refus de safety non fiables** audités (Guardrails as Scapegoats, 2607.19449, R:8) : les guardrails peuvent refuser à tort ou cacher des vulnérabilités
- [ ] **Accumulation de risque conversationnel** (Stateful Guardrails, 2607.19361, R:8) : surveiller la dérive sur sessions longues

---

*Checklist enrichie le 2026-07-25 — Phase 13 ajoute les mesures Threat Intel cycle 25/07 (clusters self-hosted security + AI SBOM + RAIL Guard + vision/biométrie).*


