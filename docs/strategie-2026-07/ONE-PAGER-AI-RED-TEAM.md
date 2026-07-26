# ONE-PAGER — Offre "AI Red Team"

> **Date:** 2026-07-19
> **Auteur:** Le Gardien des Normes (Cortex Leman)
> **Destinataire:** Thierry (validation commerciale) + Le Narrateur (mise en forme)
> **Statut:** Draft — en attente de validation Thierry
> **Source veille:** ArXiv Daily 19/07 (delta) — signaux #1, #2 convergents

---

## 💡 Le constat

**Le pentest IA devient une discipline académique autonome.** 3 papiers distincts en 7 jours (ArXiv 14→19/07/2026) l'institutionnalisent :

| arXiv | Apport | Score |
|-------|--------|-------|
| [2607.14006](https://arxiv.org/abs/2607.14006) | Refonte méthodologique — passage des failles CVE aux **"behavioral objectives"** (comportements IA indésirables). 42 pages. | 17/20 |
| [2607.11698](https://arxiv.org/abs/2607.11698) | Agent Hacks Agent — framework d'automatisation du red-teaming | déjà suivi (TICKET-002) |
| [2607.14256](https://arxiv.org/abs/2607.14256) | Red-team d'agents en production | 17/20 |

**Traduction marché :** les DPO et cabinets de conseil RGPD classiques **ne savent pas faire**. Ils savent auditer la conformité documentaire, pas exécuter des attaques contre une IA. C'est un gap de compétences durable.

---

## 🎯 L'offre Cortex Leman — "AI Red Team Report"

**Positionnement :** extension technique de l'audit compliance RGPD/AI Act. On ne valide pas seulement que le client est conforme sur le papier — on **exécute les attaques documentées** contre son IA en production pour mesurer sa robustesse réelle.

### Périmètre d'attaques testables

| Domaine | Attaque | Référence | Article AI Act |
|---------|---------|-----------|----------------|
| **Prompt injection** | Cross-context, via documents/emails/web scrapé | arXiv 2607.14493 | Art. 15 |
| **Jailbreak quantization** | Si modèle déployé edge/on-prem en INT8/INT4 | arXiv 2607.12792 (JADR) | Art. 15 |
| **Skill poisoning** | Skills/plugins tiers compromise | arXiv 2607.13987 | Art. 9, 14 |
| **Memory poisoning** | Mémoire agent cross-session (Bad Memory, MemPoison) | arXiv 2607.14611, 2607.14651 (1227 cas) | Art. 14, 15 |
| **MCP runtime leak** | Serveurs MCP (Apify, n8n, internes) qui fuient | arXiv 2607.14754 (FlowGuard) | Art. 15, 32 RGPD |
| **Biais implicites** | Value Leakage non visible utilisateur | arXiv 2607.14345 | Art. 10 |
| **Vision adversariale** | Si pipeline vision (OCR, deepfake detection) | arXiv 2607.11560 | Art. 15 |

---

## 📦 Format du livrable "AI Red Team Report"

1. **Executive Summary** (1 page) — score de robustesse global, top 3 vulnérabilités critiques, verbatim risk owner
2. **Méthodologie** (1 page) — références aux papers ArXiv, framework behavioral objectives
3. **Attaques exécutées** (8-12 pages) — pour chaque attaque :
   - Vecteur (paper source, arXiv ID)
   - Préconditions
   - Scénario d'exécution (avec captures/artefacts)
   - Résultat (succès/échec/partial)
   - Sévérité (Critique / Élevée / Moyenne / Faible)
   - Article AI Act / RGPD en jeu
4. **Score de robustesse** (1 page) — radar 7 axes, distribution par sévérité
5. **Plan de remédiation** (3-5 pages) — priorisé, chiffré, avec recommandations techniques concrètes
6. **Annexes** — logs d'exécution, artefacts d'attaque (anonymisés)

---

## 💰 Pricing indicatif (à valider Thierry)

| Option | Périmètre | Délai | Prix indicatif |
|--------|-----------|-------|----------------|
| **Essential** | 3 attaques (prompt injection + memory + MCP) | 5 jours | 8-12k CHF |
| **Standard** | 5 attaques + audit biais implicites | 10 jours | 15-22k CHF |
| **Premium** | 7 attaques + re-test post-remédiation | 15 jours | 25-35k CHF |

**Comparaison :** un audit RGPD classique facturé 5-10k CHF ne couvre pas ces attaques. L'offre Cortex Leman se positionne en sur-ensemble technique premium.

**Récurrent possible :** re-test annuel (Art. 15 AI Act exige évaluation périodique de robustesse).

---

## 🎯 Cibles prioritaires (FR-CH)

1. **Cabinets d'avocats** — utilisent déjà LLMs pour analyse de cas, exposition prompt injection maximale
2. **Fiducies / experts-comptables** — données financières + LLM pour reporting
3. **PME santé (vaudoises, genevoises)** — domaine haut risque AI Act, DPIA obligatoire incluant robustesse
4. **Banques privées genevoises** — domaine financier, exigences FINMA + AI Act
5. **Assurances** — usage LLM en souscription/sinistres, données Art. 9 possibles

---

## 🔥 Argumentaire commercial (3 phrases)

> *"Un audit RGPD vous dit que vos documents sont en règle. Notre AI Red Team Report vous montre ce qu'un attaquant peut réellement faire à votre IA en production — avant qu'il ne le fasse."*
>
> *"L'AI Act (Art. 15) exige une robustesse cybersécurité démontrée. Notre rapport est la preuve technique que vous pouvez présenter à un régulateur."*
>
> *"Les attaques documentées dans nos rapports proviennent de la recherche de pointe (arXiv, 7 derniers jours) — pas d'un template générique."*

---

## ⚡ Next steps (décision Thierry)

- [ ] Valider le positionnement et le pricing
- [ ] Valider les 5 cibles prioritaires
- [ ] Demander à Tars de préparer le prototype de livrable (TICKET-014)
- [ ] Démo sur un cas interne (auto-red-team de la stack Cortex Leman) comme matériau commercial
- [ ] Identifier 1 prospect pilote pour launch offer (-30%)

---

## 📚 Sources

- arXiv 2607.14006 — Rethinking Pentest for AI Systems (42 pages) — https://arxiv.org/abs/2607.14006
- arXiv 2607.11698 — Agent Hacks Agent — https://arxiv.org/abs/2607.11698
- arXiv 2607.14256 — Red-team d'agents en production — https://arxiv.org/abs/2607.14256
- ArXiv Daily Report 19/07 (delta) — `/home/tars/.hermes/cron/output/0f8a90201d56_20260719_110418.txt`
- Connexe : TICKET-001, TICKET-002, TICKET-010, TICKET-011, TICKET-013, TICKET-014
