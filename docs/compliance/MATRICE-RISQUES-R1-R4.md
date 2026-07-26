# Matrice de Risques R1-R4 — Cortex Leman

> **Source:** Adapté de HELEN Risk Matrix (récupérée depuis bytecode 2026-07-10) pour contexte FR-CH PME.
> **Référence skill:** `le-gardien-des-normes` → references/helen-risk-matrix-recovered.md
> **Version:** 1.0 — 2026-07-14
> **Statut:** 🟢 Actif — Source officielle de classification des risques pour Cortex Leman

---

## 1. Niveaux de Risque (R1-R4)

| Niveau | Code | Description | Action | Kill Switch |
|--------|------|-------------|--------|-------------|
| **R1** | `R1_LOW` | Risque Faible — Traitement Automatique Autorisé | ✅ Automatisation OK, pas de validation humaine requise | Non |
| **R2** | `R2_MODERATE` | Risque Modéré — Validation Humaine Requise | ⚠️ Un humain doit valider avant livraison | Non |
| **R3** | `R3_HIGH` | Risque Élevé — Double Validation Requise | 🔸 Deux validations indépendantes requises | Non |
| **R4** | `R4_CRITICAL` | Risque Critique — Blocage Système | 🚫 Kill Switch — bloquer + alerter + escalader | **OUI** |

### Propriétés par niveau

| Propriété | R1 | R2 | R3 | R4 |
|-----------|----|----|----|----|
| `requires_human_validation` | ✗ | ✓ | ✓ | ✓ |
| `is_blocking` | ✗ | ✗ | ✗ | ✓ |
| `is_safe_for_automation` | ✓ | ✗ | ✗ | ✗ |

---

## 2. Patterns de Classification (Déterministe — Regex, pas ML)

**Principe Fail Safe:** En cas d'erreur ou d'incertitude, le classificateur défaut vers R3_HIGH (pas R1). Mieux vaut sur-valider que manquer un risque critique.

### R4_CRITICAL — Patterns de blocage immédiat

| Pattern | Contexte Cortex Leman | Article RGPD/AI Act |
|---------|----------------------|---------------------|
| `conflit d'intérêts` | Avocat/fiduciaire représentant deux parties | Art. 5(1)(a) RGPD |
| `partie adverse` | Traitement de données d'un opposant légal | Art. 9 RGPD |
| Données de santé (Art. 9) | Catégorie sensible — DPIA obligatoire | Art. 9, 35 RGPD |
| Données financières sensibles | Numéros de carte, secrets bancaires | Art. 32 RGPD, Art. 47 LB (CH) |
| Protection des mineurs | Toute donnée relative à un mineur | Art. 8 RGPD |
| Décision judiciaire automatisée | Output IA présenté comme décision légale | Art. 22 RGPD |

### R3_HIGH — Patterns de double validation

| Pattern | Contexte | Article |
|---------|----------|---------|
| PII détectée par middleware | Nom, email, téléphone dans un prompt | Art. 4(1), 25 RGPD |
| `Sensibilité élevée` | Traitement marqué sensible par le client | Art. 9 RGPD |
| Transfert international non documenté | Données vers API US (OpenAI/Anthropic) sans garanties | Art. 44-49 RGPD |
| Fine-tuning proposé | Contournement du RAG recommandé | Art. 17 RGPD (droit à l'oubli) |

### R2_MODERATE — Patterns de validation humaine

| Pattern | Contexte | Article |
|---------|----------|---------|
| `Interaction client` | Contenu destiné à un client final | Art. 7 RGPD |
| Document contractuel | Génération de CG, contrats, attestations | Art. 52 AI Act |
| Recommandation financière | Conseil produit/service basé sur IA | Art. 6-9 AI Act |
| Communication externe | Email, courrier, message public | Art. 52 AI Act |

### R1_LOW — Aucun marqueur détecté

Traitement interne, anonymisé, sans PII ni catégorie sensible. Automatisation autorisée.

---

## 3. Intégration ArXiv Threat Intel (Mise à jour 2026-07-14)

> **Source:** ArXiv Daily Report 2026-07-14 (job 0f8a90201d56)
> Les menaces IA émergentes identifiées par la veille sont intégrées dans la matrice ci-dessous.

| Menace | arXiv ID | Impact Cortex Leman | Niveau assigné | Action |
|--------|----------|---------------------|----------------|--------|
| Attaques adversariales multimodales sur VLAs (vision-language agents) | 2607.11560 | Pipelines de détection de falsification documentaire vulnérables | **R3** pour tout pipeline vision utilisant des VLAs | Audit robustesse adversariale obligatoire avant déploiement |
| Red-teaming automatisé d'agents en production | 2607.11698 | Agents Cortex Leman (tâches autonomes, accès documentaire) exposés | **R2** par défaut, **R3** si agent a accès outil critique | Intégrer vecteurs d'attaque dans tests de pénétration |
| Backdoors distribués dans systèmes multi-agents | 2607.11751 | Architecture multi-agents Cortex Leman (Agent Data → Raisonnement → Action) | **R3** pour tout déploiement multi-agents | Vérifier intégrité des composants agents avant chaining |
| Claims de risque non vérifiés en RL distributionnel | 2607.11607 | Si client utilise RL pour décision automatisée | **R3** si RL dans le pipeline | Audit des claims de risque avant validation compliance |

---

## 3.bis Intégration ArXiv Threat Intel — Cycle 2026-07-22

> **Source :** ArXiv Daily Report 2026-07-22 (job `0f8a90201d56`, run 11:36, non injecté au prompt principal)
> **5 nouveaux papers R ≥ 10** (dont 2 × R:12) intégrés ci-dessous. Tickets associés : TICKET-022 à 026.

| Menace / Opportunité | arXiv ID | Impact Cortex Leman | Niveau assigné | Action |
|----------------------|----------|---------------------|----------------|--------|
| Watermarking LLM model-free (AI Act Art. 50) | 2607.18445 | **Opportunité produit** : conformité transparence contenu synthétique, J-11 avant 2 août | **R2** par défaut, **R3** si high-risk | Évaluer comme socle technique (TICKET-022) |
| Engineering Trustworthy Agentic AI (survey, 5 dimensions) | 2607.18548 | **Cadre méthodologique** pour audits, mapping direct AI Act/RGPD | **R2** (référence structurelle) | Adopter comme cadre d'audit (TICKET-023) |
| Prévention proactive fuites de données agents | 2607.18847 | Surface d'attaque prompt injection sur agents Cortex Leman | **R3** pour tout agent avec tools externes | Hardening préventif (TICKET-024) |
| Framework quantitatif risque résiduel (CPSAINT/FRIESA-K) | 2607.18243 | Score quantitatif de risque résiduel par agent | **R2** (différenciateur audit) | Évaluer (TICKET-025) |
| Privacy-preserving multi-vendor via homomorphic encryption | 2607.19146 | Privacy-by-design renforcé, fusion cross-tenant sans exposition | **R2** (opportunité architecture) | Évaluer (TICKET-026) |

### Signal dominant du cycle 22/07

La communauté académique **structure la sécurité des systèmes agents IA**. Trois papiers majeurs convergent : prévention des fuites de données (2607.18847), attaques CI/CD via agents (2607.19267), attribution cross-agent (2607.18826). À surveiller pour les audits AI Act Art. 9 (gestion des risques) des systèmes high-risk.

Le concept émergent de **Safety Drift** (2607.18366) — érosion progressive des garanties de sécurité au fil des interactions multi-turn — devrait informer les exigences de **monitoring continu** (AI Act Art. 17) pour les systèmes haut-risque.

---

## 4. Garde-fous multi-niveaux (AI Act)

| Niveau | Garde-fou | Articles | Quand appliquer |
|--------|-----------|----------|-----------------|
| 1 — Transparence | Indiquer interaction avec IA | Art. 52 AI Act | Tout système IA avec interaction utilisateur |
| 2 — CG + Supervision humaine | CG mentionnant hallucinations + vérification humaine avant envoi | Art. 7 RGPD, Art. 14 AI Act | Tout système IA générant du contenu pour tiers |
| 3 — Doc technique + Conformité | DPIA, doc technique, logo CE, traces complètes | Art. 35 RGPD, Art. 6-9 AI Act | Domaines haut risque (juridique, RH, santé, finance) |

---

## 5. Rôles AI Act pour clients Cortex Leman

| Rôle | Définition | Obligations | Exemple Cortex Leman |
|------|------------|-------------|----------------------|
| **Fournisseur** | Crée l'IA de A à Z | Doc technique, conformité CE, gestion risques | Si on développe un modèle propriétaire |
| **Déployeur** | Utilise une IA sur le marché EU | Transparence, supervision humaine, DPIA si haut risque | Nos clients PME utilisant ChatGPT/Claude |
| **Importateur** | Amène une IA étrangère sur marché EU | Vérifier conformité fournisseur, documentation | Utiliser une API US sans adequacy |
| **Distributeur** | Met à disposition une IA sans la créer | Information, coopération avec autorités | Marketplace d'agents IA |

---

## 6. Kill Switch — Procédure d'activation

Le Kill Switch est déclenché automatiquement quand un traitement est classifié **R4_CRITICAL**.

**Actions immédiates:**
1. Blocage du traitement en cours
2. Alerte envoyée au Gardien des Normes + Responsable de Traitement
3. Escalade vers Tars (intervention humaine obligatoire)
4. Log de sécurité créé (SecurityEvent, severity=critical)
5. Aucun output n'est délivré au client

**Désactivation du Kill Switch:** Uniquement par intervention humaine (Tars ou Thierry), après analyse du SecurityEvent et validation que la cause racine est résolue.

---

## 7. Checklist d'audit (Synthèse)

### Avant tout déploiement IA client:

- [ ] Niveau d'autonomie IA identifié (Low/Medium/High)
- [ ] Rôle AI Act identifié (Fournisseur/Déployeur/Importateur/Distributeur)
- [ ] Niveau de risque classé (R1-R4) selon les patterns ci-dessus
- [ ] Si R3+: DPIA (AIPD) en place (`docs/compliance/AIPD-TEMPLATE.md`)
- [ ] Traces LLM complètes (prompt, réponse, appel d'outil) — Art. 30 RGPD
- [ ] Kill Switch testé et fonctionnel
- [ ] Transparence IA (Art. 52 AI Act) — utilisateur sait qu'il interagit avec une IA
- [ ] CG mentionnent hallucinations/erreurs possibles
- [ ] Supervision humaine avant envoi client final
- [ ] Architecture RAG privilégiée sur fine-tuning (justification si exception)
- [ ] Robustesse adversariale testée (si pipeline vision/VLA — cf. ArXiv 2607.11560)
- [ ] Intégrité multi-agents vérifiée (si architecture multi-agents — cf. ArXiv 2607.11751)

---

*Référence technique: `~/.hermes/skills/compliance/le-gardien-des-normes/references/helen-risk-matrix-recovered.md`*
*Référence OWASP: `~/.hermes/skills/compliance/le-gardien-des-normes/references/security_audit_owasp.md`*
