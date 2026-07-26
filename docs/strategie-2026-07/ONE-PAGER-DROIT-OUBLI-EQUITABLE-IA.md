# One-Pager Commercial — Droit à l'Oubli IA Équitable

> **Offre N°8** · Cortex Leman · Créé 2026-07-26 (veille ArXiv cluster *Machine Unlearning Equity*, 4 papers R:8)
> **Cible :** Toute PME FR-CH entraînant ou déployant un modèle IA sur données clients/patients
> **Articles :** RGPD Art. 17 (effacement) + Art. 22 (décisions automatisées) + AI Act Art. 9-15 (haut-risque)

---

## 💡 Le problème que personne ne voit

Le **droit à l'effacement** (RGPD Art. 17) est trivial pour une base de données : on supprime la ligne. Il devient **techniquement irrésoluble** quand les données sont **intégrées ("bakees") dans un modèle** — qu'il soit fine-tuné ou simplement pré-entraîné sur vos corpus.

**Ce que la recherche a découvert cette semaine (ArXiv 20–24/07/2026) :** les méthodes de *machine unlearning* actuelles **désavantagent systématiquement certaines classes démographiques**. Autrement dit :

> *"Exercer son droit à l'oubli peut dégrader les performances du modèle pour d'autres groupes."*

Ceci ouvre un **risque juridique inédit** : un client patient/client qui demande l'effacement peut, par effet de bord, déclencher une discrimination envers une catégorie protégée — créant un manquement **Art. 9 RGPD** (données sensibles) là où il n'y en avait pas.

---

## 🎯 Pourquoi Cortex Leman est le seul à couvrir ça

| Approche classique | Approche Cortex Leman |
|---|---|
| "On vous supprime la ligne" | Audit complet : la donnée est-elle dans le modèle ? |
| Pas de méthode | Méthode **équité-auditée** de machine unlearning |
| Pas de preuve devant la CNIL | **Certification de l'oubli** (vérification post-remédiation) |
| Risque Art. 9 latent ignoré | Évaluation d'impact equity obligatoire avant exécution |

**Références académiques à citer en proposition** (corpus ArXiv 07/2026) :
- [Unlearning Under Imbalance](https://arxiv.org/abs/2607.21300) — inéquité du unlearning
- [Privacy Cost as Equity Input](https://arxiv.org/abs/2607.16620) — coût privacy comme critère d'équité
- [Gradient Concentration Explains Class Unlearning](https://arxiv.org/abs/2607.21353) — mécanisme théorique
- [Oracle-Free Certification Limits](https://arxiv.org/abs/2607.19442) — **limites de certification** (crucial : prouve qu'un audit honnête doit reconnaître les cas impossibles)
- [Survey: LLM Unlearning for Cyber Defense](https://arxiv.org/abs/2607.16227) (R:9)

---

## 📦 Offre — 3 phases

| Phase | Délivré | Durée | Livrable |
|---|---|---|---|
| **Phase 1 — Diagnostic** | Cartographie des données "piégées" dans les modèles (fine-tuning, RAG embeddings, prompts historisés) | 3–5 jours | Rapport d'exposition + score de risque equity |
| **Phase 2 — Équité-impact** | Simulation de l'impact d'un effacement sur chaque catégorie démographique avant exécution | 5–8 jours | AIPD Art. 35 enrichi equity + scénarios de biais |
| **Phase 3 — Certification** | Exécution vérifiée + certificat d'oubli équitable (ou preuve d'impossibilité) | 3–7 jours | Attestation Cortex Leman + QR vérification |

---

## 💶 Pricing FR-CH

| Segment | Phase 1 seule | Pack 3 phases |
|---|---|---|
| PME < 50 employés | 4 500 CHF HT | 12 000 CHF HT |
| ETI 50–250 | 7 000 CHF HT | 18 000 CHF HT |
| Secteur santé / finance / RH | +30% | +30% |

**Récurrent possible :** audit annuel equity du droit à l'oubli (obligatoire si le modèle est ré-entraîné) — 2 500–6 000 CHF/an.

---

## 🎯 5 cibles prioritaires FR-CH

1. **Assurances** — scoring IA sur données médicales (haut-risque AI Act)
2. **Hôpitaux privés / cliniques** — modèles diagnostiques sur données patients
3. **Banques** — scoring crédit fine-tuné (RGPD + égalité de traitement)
4. **RH tech / plateformes recrutement IA** — biais démontrés (cf. Amazon 2018)
5. **Avocats / legaltech** — IA générative entraînée sur dossiers clients

---

## 🎣 Hook commercial (cold outreach)

> *"Le droit à l'oubli est trivial sur une base SQL. Sur un modèle fine-tuné, il peut déclencher une discrimination involontaire. Cortex Leman vous certifie un effacement équitable — ou prouve documentalement qu'il est techniquement impossible (ce qui, devant la CNIL, vaut mieux que rien)."*

---

## 📅 Prochaines étapes

- [ ] Pitch oral Thierry → 5 prospects (TOP priorité commerciale)
- [ ] Démo technique : exécuter un mini-cas d'école sur modèle ouvert + dataset synthétique
- [ ] Slide pour présentation prospects (cf. `le-narrateur-augmente`)

---

*Livrable généré par l'Exécutant Cortex Leman (cycle 26/07) · Source : synthèse ArXiv hebdomadaire 26/07/2026, cluster Machine Unlearning Equity · Aucun paper nouveau depuis le 25/07 (cycle précédent).*
