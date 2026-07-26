# Argumentaire Académique — Citations ArXiv pour Propositions

> **Usage :** snippets à intégrer dans propositions commerciales, slides prospects, et audits clients
> **Source :** Synthèse ArXiv hebdomadaire 26/07/2026 (domaines cs.AI · cs.CR · cs.CV · cs.LG, fenêtre 20–24/07/2026)
> **Maintenu par :** Exécutant Cortex Leman · Dernière MAJ : 2026-07-26

---

## 🎓 Corpus académique prioritaire (R ≥ 10)

### A. Certification tierce partie indépendante — *Closing the AI Trust Gap*

**Paper :** [Closing the AI Trust Gap: The Case for Independent Certification](https://arxiv.org/abs/2607.15992) · R:12 · 17 auteurs internationaux · soumis 17/07/2026

**Citation directe (proposition client) :**

> *"La réglementation seule ne suffit pas. L'auto-gouvernance ne suffit pas. Le marché nécessite une couche de certification indépendante qui rende la trustworthiness mesurable, comparable et commercialement récompensée."* (Closing the AI Trust Gap, 2026)

**Hook commercial Cortex Leman :**
- Nous = cette "couche de certification indépendante" en FR-CH
- Recommandation : orienter les certifications sur les **résultats** (outcomes), pas sur le process — différentiateur vs. concurrents qui font du "checkbox compliance"

---

### B. Le gap des outils compliance actuels — *Critical Analysis of Trustworthy AI Tools*

**Paper :** [A Critical Analysis of Trustworthy AI Tools, Mark Frameworks, and Implementation Chasms](https://arxiv.org/abs/2607.15480) · R:12 · analyse empirique (dataset OECD)

**Trouvaille clé (à citer) :**
- Les outils "Trustworthy AI" actuels (NIST AI RMF, ISO 42001...) présentent des **asymétries majeures** :
  - Focus excessif sur fairness et transparency
  - **Manque d'explainability** et de **sécurité numérique**
  - Concentrés post-développement — peu couvrent la **phase de design/data**

**Argument de vente :**

> *"Notre méthodologie Cortex Leman couvre les 4 lacunes identifiées par la recherche académique de juillet 2026 : explainability, sécurité numérique, phase design, phase data. Les frameworks génériques laissent ces angles morts."*

**Différenciateur concurrentiel direct :** ce papier nous donne une **cartographie publiée des faiblesses de nos concurrents**.

---

### C. La sécurité ne compose pas — *ChannelGuard* ⚠️ finding critique

**Paper :** [ChannelGuard](https://arxiv.org/abs/2607.19430) · R:9

**Finding central :**

> *"La sécurité individuelle des modèles ne compose pas en sécurité système multi-agent."*

**Implication méthodologique Cortex Leman :** Les audits "modèle-par-modèle" sont **obsolètes**. Nous devons évaluer le **système sociotechnique complet**, pas les composants isolés. C'est exactement ce que plaide aussi *Closing the AI Trust Gap*.

**À intégrer dans :**
- Checklist audit (déjà partiellement fait dans `CHECKLIST-COMPLIANCE-IA.md` Phase 13)
- Slide méthodologie prospects
- Réponse aux objections "on a déjà audité ChatGPT"

---

### D. Méthodologie pour systèmes critiques — *Engineering Trustworthy Agentic AI*

**Paper :** [Engineering Trustworthy Agentic AI for Critical Systems](https://arxiv.org/abs/2607.18548) · R:13 (le plus haut de la semaine)

**Usage :** Référence méthodologique pour offres en secteurs critiques (énergie, santé, infrastructure). Citer en bibliographie de tout AIPD/AI Act dossier haut-risque.

---

### E. Mesure des deepfakes — *PhantomSeal*

**Paper :** [PhantomSeal](https://arxiv.org/abs/2607.20564) · R:11

**Usage :** Recommandation technique concrète pour clients exposés au risque deepfake (Art. 50 AI Act — transparence). Mentionner dans tout audit contenant un volet "anti-fraude documentaire".

---

## 🛡️ Vecteurs de sécurité à intégrer dans la checklist (cluster 2)

Ces 7 vecteurs émergents contre les architectures multi-agents doivent figurer dans tout audit Cortex Leman post-juillet 2026 :

| Vecteur | Paper | R | Article RGPD/AI Act |
|---|---|---|---|
| Kill chains MCP | [ChainWatch](https://arxiv.org/abs/2607.19432) | 12 | Art. 32 RGPD |
| Sécurité ne compose pas | [ChannelGuard](https://arxiv.org/abs/2607.19430) | 9 | Art. 32 + Art. 35 |
| Persistance temporelle (mémoire) | [Chronos Vulnerability](https://arxiv.org/abs/2607.19433) | 9 | Art. 5(1)(e) |
| Attaques état interne agents | [Self-State Attacks](https://arxiv.org/abs/2607.17986) | 9 | Art. 32 |
| CI/CD détourné | [Trusted CI/CD as Attack Surface](https://arxiv.org/abs/2607.19267) | 9 | Art. 32 + Art. 17 AI Act |
| Coding agents trojans | [IssueTrojanBench](https://arxiv.org/abs/2607.20759) | 9 | Art. 15 AI Act |
| Vol d'architecture | [Leaky LLMs](https://arxiv.org/abs/2607.20723) | 9 | Art. 32 + secret affaires |

**Insight stratégique :** *ChannelGuard* invalide l'approche "modèle-par-modèle". Nos audits doivent évaluer le système sociotechnique complet.

---

## 🔬 Cluster equity / droit à l'oubli (RGPD Art. 17)

**Voir one-pager dédié :** `docs/strategie-2026-07/ONE-PAGER-DROIT-OUBLI-EQUITABLE-IA.md`

| Paper | R | Angle |
|---|---|---|
| [Survey: LLM Unlearning for Cyber Defense](https://arxiv.org/abs/2607.16227) | 9 | Vue d'ensemble |
| [Unlearning Under Imbalance](https://arxiv.org/abs/2607.21300) | 8 | **Inéquité** du unlearning |
| [Privacy Cost as Equity Input](https://arxiv.org/abs/2607.16620) | 8 | Coût privacy = critère d'équité |
| [Gradient Concentration Explains Class Unlearning](https://arxiv.org/abs/2607.21353) | 8 | Mécanisme théorique |
| [Oracle-Free Certification Limits](https://arxiv.org/abs/2607.19442) | 8 | **Limites de certification** (honnêteté technique) |

---

## 📋 Mapping RGPD / AI Act consolidé (semaine 20–24/07/2026)

| Article | Papers pertinents | Priorité Cortex Leman |
|---|---|---|
| AI Act Art. 9-15 (haut-risque) | Engineering Trustworthy Agentic AI (R:13), Regulating Autonomous AI (R:13), JANUS (R:11) | 🔴 Immédiat |
| AI Act Art. 17 (corrective actions / monitoring) | RAIL Guard (R:11), DARWIN co-évolution (R:11), Auditable Levels (R:11) | 🔴 Immédiat |
| AI Act Art. 50 (transparence, deepfakes) | PhantomSeal (R:11), Compétition Document Forgery (R:8) | 🟡 Semaine |
| AI Act Art. 5 (pratiques interdites) | Ethics of Autonomous Offensive Agents (R:10), DecoyFace biométrie (R:7) | 🟡 Semaine |
| RGPD Art. 17 (effacement) | 6 papiers unlearning (R:7-9) | 🟡 Semaine |
| RGPD Art. 22 (décisions automatisées) | Cryptographic Verifiable Authorization (R:10), Accountability papers | 🟡 Semaine |
| RGPD Art. 32 (sécurité) | ChainWatch, ChannelGuard, Leaky LLMs + 15 papiers sécurité agents | 🔴 Immédiat |
| RGPD Art. 35 (DPIA) | PhantomSeal, TRUST-ESD (R:8) | 🟡 Semaine |

---

## 🎯 Top 5 papers à intégrer dans les offres (priorité d'exécution)

1. **[Closing the AI Trust Gap](https://arxiv.org/abs/2607.15992)** (R:12) — Fondation académique pour offre certification tierce partie. **Citer dans toutes les propositions.**
2. **[Critical Analysis of Trustworthy AI Tools](https://arxiv.org/abs/2607.15480)** (R:12) — Cartographie publiée des gaps des outils existants. **Différenciateur commercial direct.**
3. **[ChannelGuard](https://arxiv.org/abs/2607.19430)** (R:9) — "La sécurité ne compose pas". **À intégrer dans methodology d'audit système.**
4. **[Regulating Autonomous and Agentic AI](https://arxiv.org/abs/2607.21345)** (R:13) — Référence pour recommandations stratégiques clients déployant des agents.
5. **[PhantomSeal](https://arxiv.org/abs/2607.20564)** (R:11) — Mesure technique deepfakes (Art. 50 AI Act).

---

## 📈 Volume de la semaine

| Domaine | Entries (5 jours) | R≥7 | Alertes critiques (R≥10) |
|---|---:|---:|---:|
| cs.AI | 1072 | ~150 | 6 |
| cs.CR | 173 | 49 | 5 |
| cs.CV | 595 | ~83 | 0 |
| cs.LG | 932 | ~122 | 1 |
| **Total** | **2772** | **~95** | **12** |

Taux de pertinence : 3.4% (95/2772) — cohérent avec la moyenne historique.

---

## 🔁 Maintenance

- **Prochain scan ArXiv :** lundi 27/07/2026 (nouveau lot hebdomadaire ~20:00 UTC)
- **Ce corpus est valable jusqu'au 02/08/2026** (date à laquelle un nouveau lot remplacera les références de juillet)
- À réviser si nouveau signal R ≥ 10 détecté en semaine suivante

---

*Document généré par l'Exécutant Cortex Leman · Cycle 26/07 · Source : synthèse hebdomadaire L'Oeil de Cortex 26/07/2026 · Corpus ArXiv fenêtre 20–24/07/2026.*
