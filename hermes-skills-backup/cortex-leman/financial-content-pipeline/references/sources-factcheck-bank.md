# Banque de sources vérifiées — L'Effet Composé

> Cumul des sources vérifiées via le workflow `factcheck-workflow.md`.
> **Consulter ce fichier AVANT toute recherche web** — les sources longues à recroiser y sont déjà stockées.
> Date d'accès = date de vérification. Les chiffres datent ; ajouter une note si un refresh est attendu.

---

## Énergie / Data centers

### IEA — "Key Questions on Energy and AI"
- **Date** : 16 avril 2026 (communiqué de presse, rapport complet)
- **URL** : https://www.iea.org/news/data-centre-electricity-use-surged-in-2025-even-with-tightening-bottlenecks-driving-a-scramble-for-solutions
- **Chiffres clés** :
  - Demande data centers **+17% en 2025** (vs +3% global)
  - Capex 5 big tech **>$400B en 2025**, **+75% prévu en 2026**
  - Conso DC **devrait doubler d'ici 2030** ; DC IA **tripler**
  - Tech = **~40% des PPA renewables corporate 2025**
  - Pipeline SMR (small modular reactors) : **25 GW → 45 GW** en 18 mois (fin 2024 → 2026)
  - Efficacité par tâche IA en baisse rapide (effet Jevons inverse)
- **Vérifié le** : 2026-07-18
- **Utilisable pour** : OVHcloud, ASML (capex), angle "transition énergétique IA"

### Commission EU — "In focus: Data centres – an energy-hungry challenge"
- **Date** : 17 novembre 2025
- **URL** : https://energy.ec.europa.eu/news/focus-data-centres-energy-hungry-challenge-2025-11-17_en
- **Chiffres clés** :
  - DC = **~1,5% conso électrique mondiale** (415 TWh)
  - Projection **945 TWh d'ici 2030** (x2,3)
  - UE : 70 TWh (2024) → 115 TWh (2030)
  - **Label DC EU début 2026** (énergie, eau, renouvelables) — nouveauté réglementaire = angle actu
  - Croissance DC **+12%/an sur 5 ans**
- **Vérifié le** : 2026-07-18
- **Utilisable pour** : OVHcloud, angle réglementaire EU

## Emploi / Macro IA

### WEF — "Future of Jobs Report 2025"
- **Date** : 7 janvier 2025
- **URL** : https://www.weforum.org/publications/the-future-of-jobs-report-2025/
- **Chiffres clés** :
  - 1000+ employeurs surveyés, 14M workers, 55 économies
  - 1/3 des jobs impactés par IA d'ici 2030
  - Framing **"transformation"** (pas "destruction") — nuancer vs Goldman Sachs "300M emplois"
- **Vérifié le** : 2026-07-18
- **Utilisable pour** : clips macro IA, Téléperformance, angle emploi

## Semi-conducteurs / Souveraineté EU

### ⚠️ NapForum — "Can ASML Secure Europe's Tech Sovereignty?"
- **Auteur** : Thomas Hollands
- **Date** : 14 juillet 2025
- **URL** : https://www.napforum.org/policy-briefs/can-asml-secure-europe-s-tech-sovereignty
- **Chiffres clés** (selon résumé de l'article, **non vérifiés in-texte**) :
  - ASML = **monopole EUV** (100% des puces avancées passent par ses machines)
  - Angle "battleground stratégique", dépendance Taïwan
- **Vérifié le** : 2026-07-18, **re-vérifié 2026-07-18 (correction)**
- **⚠️ NE PAS citer pour des chiffres précis sans ouvrir l'URL** : un script LLM a attribué à NapForum les chiffres "100% EUV" ET "80% EUV vers TSMC" — en rouvrant l'URL, **NapForum ne soutient ni l'un ni l'autre** avec ces chiffres exacts. Le "100% EUV" est vrai mais sourcé plus rigoureusement chez **TrendForce**. Le "80%" est un **mythe pur** (voir correction ci-dessous).
- **Utilisable pour** : ASML, Soitec (chaîne photonique), angle souveraineté — **comme angle narratif, jamais comme source de chiffre précis**

### TSMC Technology Symposium 2024 — part de base installée EUV
- **Date** : symposium 2024, relayé 13 novembre 2024
- **URL** : https://www.digitimes.com/news/a20241112PD204/euv-tsmc-adoption-2023-technology.html (DigiTimes, Amanda Liang)
- **Corroboration** : AnandTech, The Register
- **Chiffres clés** :
  - TSMC = **56 % de la base installée EUV mondiale (2023)** — déclaré par TSMC elle-même au symposium
  - Trajectoire : 50 % (2020) → 56 % (2023)
  - TSMC aurait eu ~10 EUV en 2019 (lancement N7+), ~84 acquises en 2022, >100 en 2023
- **Vérifié le** : 2026-07-18
- **Utilisable pour** : ASML, TSMC, angle "otage taïwanais", dépendance géopolitique

### ASML — 2025 Annual Report (US GAAP)
- **Date** : exercice 2025 (rapport publié début 2026)
- **URL** : https://www.asml.com/investors/annual-report/2025/financials
- **PDF** : https://ourbrand.asml.com/m/71076aaad607de4d/original/asml-2025-annual-report-based-on-us-gaap.pdf
- **Chiffres clés** :
  - **Ventes nettes totales 2025 : €32,7 Mds** (+15,6 % YoY)
  - **EUV : €11,6 Mds** (48 machines livrées)
  - **TSMC ≈ 24 % des ventes nettes totales** ASML 2025
  - **TSMC + Samsung ≈ 38 %** du CA total
  - ASML ne ventile **jamais** sa production EUV par client dans ses rapports
  - Chine = 33 % du CA 2025, guidé à 20 % en 2026
- **Vérifié le** : 2026-07-18
- **Utilisable pour** : ASML (tous clips : valuation, marge, concentration client)

### TrendForce — parts de marché lithographie
- **URL** : https://www.trendforce.com/insights/asml-euv
- **Chiffres clés** :
  - ASML = **100 % de l'EUV** (monopole absolu)
  - ASML = **94 % de la lithographie globale** (DUV + EUV)
- **Vérifié le** : 2026-07-18
- **Utilisable pour** : toute affirmation "ASML = monopole EUV" — **préférer TrendForce à NapForum** comme source de ce chiffre

## Eau / Empreinte IA

### arXiv — "Making AI Less Thirsty" (Shaface et al)
- **arXiv ID** : 2304.03271
- **Auteurs** : Shaface (UC Riverside, LAUNCHERGY)
- **Chiffres clés** :
  - **Entraînement GPT-3 = 700 000 L d'eau douce** (équivalent piscine olympique)
  - Requête ChatGPT = **10-50 mL** (PAS 1L)
- **Vérifié le** : 2026-07-18
- **CORRECTION** : le chiffre "1L/req" cité par Francis Lelong (podcast Le Déclic) est **FAUX** (factor 20-100x). Ne jamais reprendre tel quel.

### ModuleEdge — "AI Water Usage" (synthèse vulgarisée)
- **Date** : mars 2026
- **URL** : https://www.moduledge.com/blog/ai-water-usage
- **Usage** : synthèse accessible des chiffres arXiv, utile pour citer source grand public

## Chiffres corrigés — À NE JAMAIS reprendre tels quels

| Source originale | Chiffre cité | Chiffre réel | Reformulation défendable |
|---|---|---|---|
| Mythe sectoriel (ASML/TSMC) | "80 % des machines EUV livrées à TSMC / Taïwan" | **FAUX** — ASML ne ventile pas sa production EUV par client. La métrique défendable = **56 % de la base installée EUV** (TSMC Tech Symposium 2024, DigiTimes 13/11/2024). Ne pas confondre avec ~24 % des ventes nettes totales ASML (rapport annuel 2025). | "Plus de la moitié des machines EUV en service dans le monde tournent chez TSMC" (voix-off prudente) + "56 % (2023)" (slide sourcée TSMC Tech Symposium) |
| Script LLM (clip ASML) | "100 % des puces 3nm imprimées par ASML EUV" (source : NapForum) | Le chiffre est vrai mais : (a) porte sur les puces **≤7nm** (pas seulement 3nm), (b) NapForum ne soutient pas ce chiffre avec cette URL. Source correcte = **TrendForce**. | "100 % des puces avancées (≤7nm) imprimées par lithographie EUV ASML" · source : TrendForce / ASML 2025 Annual Report |
| Lelong (Le Déclic) | "1 req ChatGPT = 1L eau" | 10-50 mL/req | "Entraîner GPT-3 = 700 000 L d'eau douce (arXiv 2304.03271)" |
| Lelong (Le Déclic) | "300M emplois détruits (Goldman Sachs)" | 300M emplois **exposés** (pas détruits) | "300M emplois exposés à l'automatisation d'ici 2030 (Goldman Sachs)" |
| Lelong (Le Déclic) | "Le code ne vaudra plus rien" | Formule founder | "Le code bas de gamme se commoditise ; le code critique/embarqué reste stratégique" |

---

## À ajouter après chaque passe fact-check

Format d'entrée :
```
### [Source] — "[Titre]"
- **Date** : YYYY-MM-DD
- **URL** : ...
- **Chiffres clés** : ...
- **Vérifié le** : YYYY-MM-DD
- **Utilisable pour** : [acteurs/angles concernés]
```

Si un chiffre est corrigé, l'ajouter AUSSI au tableau "Chiffres corrigés" ci-dessus.
