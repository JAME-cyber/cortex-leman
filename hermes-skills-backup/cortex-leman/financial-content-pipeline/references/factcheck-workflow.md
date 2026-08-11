# Fact-Check Workflow — Vérification des sources tierces

## Contexte

L'Effet Composé consomme régulièrement des contenus tiers (podcasts YouTube, articles, threads X) comme matière première pour des clips finance. Ces sources contiennent **systématiquement des chiffres inexacts ou exagérés** — soit par approximation orale (podcasts), soit par clickbait (X/articles). Le ratio observé sur le podcast "Le Déclic" (Francis Lelong) : **~25% des chiffres cités sont faux ou inexacts**.

**Règle absolue : aucun chiffre issu d'une source tierce n'entre dans un clip sans source externe vérifiée.** Un seul chiffre faux en commentaire YouTube = crédibilité zéro, et la chaîne se positionne sur la rigueur vs concurrents (Grand Angle Nova).

## 4 étapes de la passe fact-check

### 1. Extraction — Lister les assertions chiffrées

Repérer TOUT ce qui est chiffré ou factuel dans la source tierce :
- Chiffres absolus ("300M emplois détruits", "1L eau/requête")
- Ratios/pourcentages ("50% des patrons Fortune 500")
- Datations ("la France sera 3e mondiale")
- Causalités ("X provoque Y")
- Citations d'études (même vague : "une étude US montre…")

### 2. Consultation de la banque — `sources-factcheck-bank.md`

Avant toute recherche web, **consulter la banque**. Les sources longues à recroiser (IEA, WEF, Commission EU, arXiv, rapports annuels) y sont déjà stockées avec chiffres clés. Si une assertion correspond à un thème déjà couvert → réutiliser directement.

### 3. Recherche ciblée — Sources autoritaires par axe

| Axe | Source prioritaire | Backup |
|---|---|---|
| Énergie / data centers | **IEA** (iea.org, rapports récents) | Commission EU Energy, AIE |
| Emploi / macro IA | **WEF Future of Jobs** (annuel) | Goldman Sachs, OCDE, McKinsey |
| Semi-conducteurs | **ASML/TSMC corporate** (rapports annuels, investor day, Technology Symposium) + **TrendForce** (parts de marché litho) | DigiTimes, AnandTech, The Register, SemiAnalysis |
| Eau / empreinte IA | **arXiv** (études) — attention aux chiffres [10-50mL/req](https://arxiv.org/abs/2304.03271) vs "1L" | ModuleEdge, The Shift Project |
| Valorisation boursière | **Euronext + communiqués corporate** | Bloomberg consensus (citer explicitement) |
| Réglementation EU | **Commission EU** (energy.ec.europa.eu, digital-strategy.ec.europa.eu) | EBA, ENISA |

⚠️ **NapForum / think-tanks geopol** : utiles comme **angle narratif**, mais **ne JAMAIS** s'y fier pour un chiffre précis — un script LLM y a attribué des chiffres que l'URL ne soutenait pas. Pour les semi-conducteurs, privilégier corporate primaire (ASML 2025 AR, TSMC Tech Symposium) + TrendForce. Voir entrée corrigée dans `sources-factcheck-bank.md`.

Outil : `mcp__apify__apify__rag_web_browser` (query précise, 3-4 résultats). Le RAG browser retourne le markdown nettoyé, l'utiliser pour extraire le chiffre exact + URL + date.

### 4. Verdict structuré — Tableau

Pour chaque assertion, rendre un verdict :

| Assertion | Verdict | Source vérifiée |
|---|---|---|
| "X" | ✅ Exact / ⚠️ Partiel / ❌ Faux / ⚠️ Non vérifiable | [URL + date] |

**Si faux ou exagéré** : donner le chiffre correct défendable ET le reformuler pour le clip. Exemple : "1L eau/req ChatGPT" → "10-50 mL/req" (factor 20-100x), reformuler en "entraîner GPT-3 a consommé 700 000 L d'eau douce".

**Si non vérifiable** : ne pas reprendre, ou reformuler en interrogative ("certains analystes évoquent…").

## Patterns d'erreurs typiques (podcasts finance FR)

- **Approximation orale x10-x100** : "1L" pour "10 mL", "300M emplois" pour "300M emplois exposés" (pas détruits).
- **Confusion corrélation/causalité** : "l'IA détruit des emplois" vs "l'IA transforme des emplois" (WEF est nuancé).
- **Citations d'études non identifiables** : "une étude US dit que 50% des patrons…". Demander la source, sinon skip.
- **Chiffres périmés** : un chiffre 2022 repris en 2026 sans mise à jour. Toujours dater la source.
- **Formules founder shock** : "le code ne vaudra plus rien". C'est une formule orale, pas un fait — tempérer.
- **Confusion de métrique** (très fréquent sur les semi-conducteurs) : un même acteur peut avoir 3 chiffres radicalement différents selon la métrique. Exemple ASML/TSMC : TSMC = **56 % de la base installée EUV** (2023) ≠ **~24 % des ventes nettes totales ASML** (2025). Les deux sont vrais simultanément. Toujours préciser la métrique (installed base / revenue / unit shipments) avant de comparer deux chiffres — un mythe du type "80 % des EUV partent chez TSMC" naît souvent de la confusion entre ces trois.
- **Mythes sectoriels "bien connus"** : certains chiffres circulent sans source vérifiable (ex : "80 % des EUV ASML vers TSMC/Taïwan" — ASML ne ventile JAMAIS sa production EUV par client). Les traiter comme **non vérifiables par défaut** jusqu'à source corporate primaire.

## Cas spécial : contenu X/Twitter

Les tweets à fort engagement (RT, likes) sont rarement sourcés. Traiter comme bruit SAUF si :
- Le tweet cite explicitement un rapport/étude avec lien
- Le compte est un analyste reconnu (vérifier via profil/historique)
- Le chiffre est recontextualisable via source tierce vérifiable

Sinon : skip pur. Un tweet "creator economy / AI hustle" (majuscules, "omg", "most useful thing") = signal de bruit, pas d'information.

## Pattern subagent pour fact-check ciblé (chiffre unique bloquant)

Quand **un seul chiffre** d'un draft de script bloque la production et que la recherche nécessite du temps (plusieurs sources à recroiser), dispatcher un subagent leaf dédié plutôt que de bloquer le fil principal.

**Quand l'utiliser** : un chiffre circulant largement cité mais que tu ne peux pas confirmer en 1-2 fetches. Typique des mythes sectoriels ("80% des EUV vers TSMC", "1L eau/req ChatGPT").

**Template de délégation** :
- **Contexte** : fichier script en cours + skill de référence (format, guardrail AMF, prononciation). Lister explicitement les règles de reformulation.
- **Objectif** : vérifier CE chiffre précisément via recherche web/datasets. Donner les axes de sources autoritaires (corporate primaire > think-tanks).
- **Règle de reformulation obligatoire** : si le chiffre ne peut être vérifié avec confiance, reformuler en qualitatif ("la majorité", "plus de la moitié") plutôt que risquer un chiffre faux défendable.
- **Scope strict** : validation factuelle + correction du script Markdown SEULEMENT — PAS de génération audio/visuels.
- **Livrable attendu** : chiffre final retenu + source primaire + liste exhaustive des corrections appliquées au script.

**Après retour du subagent** :
1. Le subagent modifie le script directement → **re-lire le fichier** avant de le considérer final (il a pu toucher d'autres sections : base factuelle, sources YouTube, notes de production, points de vigilance).
2. Lire le résumé tronqué ; si besoin, `read_file` sur le cache subagent pour les détails omis (`~/.hermes/cache/delegation/subagent-summary-*.txt`).
3. Vérifier conformité AMF (le subagent l'a faite, mais double-check).

**Cas validé (2026-07-18)** : chiffre "80% des EUV ASML vers TSMC" → subagent a trouvé 56% de base installée EUV (TSMC Tech Symposium 2024), corrigé 6 sections du script, coût ~7 min de wall-clock en arrière-plan. Le script drafté pendant ce temps sur le fil principal.

## Mise à jour de la banque

Après chaque passe fact-check, **ajouter les nouvelles sources vérifiées** à `sources-factcheck-bank.md` (format : Source, Date, URL, chiffres clés, date d'accès). Cela évite de relancer les mêmes recherches IEA/WEF sur les prochains clips.
