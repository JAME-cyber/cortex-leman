# ONE-PAGER — Offre "Certification IA Indépendante"

> **Date:** 2026-07-20
> **Auteur:** Le Gardien des Normes (Cortex Leman)
> **Destinataire:** Thierry (validation commerciale) + Le Narrateur (mise en forme)
> **Statut:** Draft — en attente de validation Thierry
> **Source veille:** ArXiv Daily 20/07 — signaux #1, #2 (gouvernance/certification) + Brief RGPD-IA 15/07 (AI Act 2 août)
> **Timing:** J-13 avant entrée en vigueur AI Act (2 août 2026)

---

## 💡 Le constat

**L'AI Act exige une certification tierce-partie pour les systèmes IA à haut risque (Art. 43-49).** Trois papiers convergent en juillet 2026 pour institutionnaliser ce besoin :

| arXiv | Apport | Score |
|-------|--------|-------|
| [2607.15992](https://arxiv.org/abs/2607.15992) | Plaide pour une **certification indépendante tierce-partie** des systèmes IA — schéma d'assurance comparable ISO/SOC | **18/20** |
| [2607.16130](https://arxiv.org/abs/2607.16130) | Propose des **niveaux d'auditabilité formels** tout au long du cycle de vie IA | **18/20** |
| [2503.01816](https://arxiv.org/abs/2503.01816) | **Mapping CRA × RGPD** — correspondances réglementaires pour PME FR-CH | 15/20 |

**Traduction marché :** à partir du **2 août 2026**, toute PME FR-CH qui déploie un système IA doit :
1. Identifier son rôle AI Act (fournisseur / déployeur / importateur)
2. Classifier son niveau de risque (limité / haut / inédit)
3. Pour le haut risque : faire certifier par un tiers

Les DPO et cabinets de conseil RGPD classiques **ne savent pas évaluer un système IA**. Ils savent auditer la conformité documentaire d'un fichier Excel, pas jauger la robustesse d'un LLM. C'est un gap de compétences durable, amplifié par l'entrée en vigueur dans 13 jours.

---

## 🎯 L'offre Cortex Leman — "Attestation IA Déployeur"

**Positionnement :** tierce-partie indépendante qui certifie qu'un système IA utilisé par une PME FR-CH respecte les obligations AI Act (et RGPD croisées). On ne vend pas du conseil — on délivre une **attestation formelle** vérifiable, valide 12 mois.

**Différentiateur vs. auditeur RGPD classique :**
- Auditeur RGPD = lit votre politique de confidentialité → OK / KO documentaire
- Cortex Leman = lit votre politique **ET** évalue votre stack IA (RAG vs fine-tuning, niveau d'autonomie, garde-fous Art. 14, traces Art. 30, robustesse Art. 15)

### Périmètre de la certification

| Bloc | Article AI Act | Article RGPD | Livrable |
|------|----------------|--------------|----------|
| **Identification du rôle** | Art. 2-3 | — | Déployeur / Fournisseur / Importateur |
| **Classification du risque** | Art. 6 (haut risque), Ann. III | — | Limité / Haut / Inédit |
| **Transparence** | Art. 52 | Art. 13 | Mention IA explicite, CG adaptées |
| **Supervision humaine** | Art. 14 | Art. 22 | Workflow de validation, kill switch |
| **Logging & traçabilité** | Art. 12 | Art. 30 | Traces LLM, registre des traitements |
| **Robustesse cybersécurité** | Art. 15 | Art. 32 | Guardrails, sanitization, éval. adversariale |
| **DPIA (si haut risque)** | — | Art. 35 | AIPD complète ou Existing review |
| **Cross-border (si clients CH)** | — | Art. 44-49, LPD Art. 16 | Clauses contractuelles, adéquation |

---

## 📦 Format du livrable

1. **Attestation formelle A4** (1 page) — score de conformité /1.00, durée de validité 12 mois, QR code de vérification en ligne
2. **Rapport d'audit** (15-20 pages) — méthodologie, scores par bloc, findings, plan de remédiation 90 jours
3. **Registre client** (accessible en ligne) — référencement de l'attestation, statut, historique

**Seuil d'attestation :** score global ≥ 0.80. En dessous, plan de remédiation obligatoire avant attestation.

---

## 💰 Pricing indicatif (à valider Thierry)

| Option | Périmètre | Délai | Prix indicatif |
|--------|-----------|-------|----------------|
| **Essential** | Audit déployeur basique (rôle + risque + transparence + logging) | 5 jours | 5-7k CHF |
| **Standard** | Essential + robustesse cybersécurité + DPIA légère | 10 jours | 9-13k CHF |
| **Premium** | Standard + audit Art. 15 complet (cf. offre AI Red Team) + re-test annuel | 15 jours | 15-20k CHF |

**Comparaison :** un audit RGPD classique facturé 5-10k CHF ne couvre pas l'AI Act. Notre attestation couvre les deux cadres en une passe.

**Récurrent naturel :** renouvellement annuel (AI Act + RGPD exigent réévaluation périodique). Estimation : 60% du prix initial / an.

---

## 🎯 Cibles prioritaires (FR-CH)

1. **Cabinets d'avocats** — utilisent déjà ChatGPT/Claude pour analyse de cas. Rôle AI Act: déployeur. Risque: haut (juridique, Ann. III).
2. **Fiducies / experts-comptables** — données financières + LLM pour reporting. Risque: haut (finance).
3. **PME santé (vaudoises, genevoises)** — données Art. 9 RGPD + IA en diagnostic/support. Risque: haut (santé).
4. **Banques privées genevoises** — exigences FINMA + AI Act + secret bancaire (Art. 47 LB). Risque: haut.
5. **E-commerce / retail** — chatbots, recommandations, scoring client. Risque: limité mais transparence Art. 52 obligatoire.

**Pitch d'accroche (secteur avocat) :**
> *"Le 2 août, vos clients peuvent vous demander quelle est votre attestation AI Act pour l'usage de ChatGPT sur leurs dossiers. Si vous n'avez pas de réponse, ils iront chez un cabinet qui en a une."*

---

## 🔥 Argumentaire commercial (3 phrases)

> *"L'AI Act devient applicable le 2 août. Si vous utilisez ChatGPT, Claude ou tout autre IA sur des dossiers clients, vous êtes 'déployeur' au sens du règlement — avec des obligations de transparence, de supervision humaine et de traçabilité."*
>
> *"Notre attestation est délivrée par un tiers indépendant et couvre AI Act + RGPD en une passe. Valide 12 mois, vérifiable en ligne."*
>
> *"Les cabinets de conseil RGPD classiques ne savent pas évaluer une stack IA. C'est littéralement notre métier."*

---

## ⚡ Next steps (décision Thierry)

- [ ] Valider le positionnement et le pricing
- [ ] Valider les 5 cibles prioritaires
- [ ] Demander à Tars de préparer la maquette d'attestation A4 (cf. skill le-narrateur-augmente `generate-attestation`)
- [ ] Construire la landing page "Certification IA Déployeur" (J-13 oblige)
- [ ] Identifier 3 prospects pilotes pour launch offer (-30%) — idéalement 1 cabinet d'avocats + 1 fiducie + 1 PME santé

---

## 📚 Sources

- arXiv 2607.15992 — Closing the AI Trust Gap: Independent Certification for Trustworthy AI — https://arxiv.org/abs/2607.15992
- arXiv 2607.16130 — Methodology for Auditable Trustworthiness Levels in AI Lifecycle Governance — https://arxiv.org/abs/2607.16130
- arXiv 2503.01816 — A Mapping Analysis of Requirements Between the CRA and the GDPR — https://arxiv.org/abs/2503.01816
- ArXiv Daily Report 20/07 — `/home/tars/.hermes/cron/output/0f8a90201d56_2026-07-20_arxiv-daily.txt`
- Brief RGPD-IA 15/07 — AI Act applicable 2 août 2026 (J-13 aujourd'hui)
- Skill le-gardien-des-normes — Checklist PME + 4 dimensions IA
- Connexe : `ONE-PAGER-AI-ACT-2-AOUT-2026.md`, `ONE-PAGER-AI-RED-TEAM.md`
