# Registre Concurrentiel — Cortex Leman

> **Version 1.1 — 22 août 2026** · Document de référence unique (point de sync inter-laptops)
> Consolidation de : `moat-compliance-pitch.md` §2, `zenithia-competitive-analysis.md`, `marketing-playbook.md`, `cortex-leman-pricing.md`, `agent-readiness-offer.md` + recherche web 22/08/2026.
> **Règle** : toute nouvelle donnée concurrentielle s'ajoute ICI d'abord, puis se propage dans le doc d'offre concerné. Ne pas recréer d'analyses éparses.

---

## 0. Résumé exécutif

1. **Aucun concurrent ne combine : RGPD-IA + AI Act + FR-CH natif + prix PME.** Le milieu de gamme (890–3 500 €) est structurellement vide : les Big 4 commencent à 75 000 €+, les SaaS de gouvernance exigent de tout faire soi-même, les agences IA ignorent la compliance.
2. **Menace la plus proche : sidd.swiss** (DE) — seul cabinet suisse avec une vraie offre IA (AI Officer CHF 500/mois, AI Governance Check CHF 3 900, AI Security LLM/RAG/agents, ISO 42001 clé en main). Faiblesse : allemand natif, français "sur demande" → **la Romandie est leur flanc ouvert, notre tête de pont.**
3. **Le créneau agent-readiness (offre GEO)** est occupé côté US (Helium/ORCA, Logarithmic, Xpand/MentionLayer, Grindstone) mais **aucun ne fait le pont compliance** (AI Act art. 50 + RGPD art. 5.1.d) ni le FR-CH. Notre skill `agent-readiness-audit` (cua-driver) égale leur capacité de mesure réelle.
4. **Horloge réglementaire (correction importante)** : l'AI Act art. 50 (transparence) s'applique DEPUIS le 02/08/2026 — c'est LA live obligation (15 M€ / 3 % CA). Le reste est reporté : high-risk Annexe III → 02/12/2027, Annexe I → 02/08/2028 (Digital Omnibus, Règlement UE 2026/1744, en vigueur 27/07/2026). **Vendre l'urgence sur l'art. 50 + l'exactitude RGPD, pas sur les high-risk.**

---

## 1. Tableau maître

Légende menace : 🔴 directe (même cible, même créneau) · 🟠 adjacente (peut basculer) · 🟡 périphérique · ⚪ contexte (générateur de clients, pas concurrent)

| # | Concurrent | Catégorie | Offre & prix | FR-CH | Compliance IA | Menace | Notre faille chez eux |
|---|---|---|---|---|---|---|---|
| 1 | **sidd.swiss** (Dr Staiger) | Cabinet CH | AI Officer CHF 500/mois · AI Governance Check dès CHF 3 900 · CPD externe CHF 500/mois · ISO 42001 clé en main · AI Security (LLM/RAG/agents) | ❌ DE/EN natif, FR sur demande | ✅ complète (LPD+RGPD+AI Act+NIS2) | 🔴 | Français natif absent = Romandie ouverte |
| 2 | **Comity Sàrl** (Lausanne) | Cabinet romand | DPO as a Service · Audit & Compliance · Privacy Engineering | ✅ Lausanne | 🟡 privacy seule, pas d'offre IA visible | 🟠 | Peut ajouter l'IA demain ; base clients romande existante |
| 3 | **Zenith Advisory** (Viventis) | Cabinet romand | Zenith-DPO · CISO externalisé · dark web monitoring · évaluation résilience PME | ✅ francophone | 🟡 pas d'angle IA | 🟠 | Idem — marque installée, pas de brique IA |
| 4 | **ZénithIA** (clem.entreprend, FR) | Agence IA FR | Automatisations n8n : 500 € – 50 k€ · CA 750 k€ · cible grands comptes HEC | ❌ France uniquement | ❌ RGPD évoqué 1 fois en 2h30 de conférence | 🟠 (si bascule compliance) | 5 avantages déjà documentés : récurrent, souveraineté CH, qualité>volume, droit suisse, RGPD-IA combiné |
| 5 | **Big 4** (Deloitte, PwC, EY, KPMG) + Accenture | Conseil global | AI Act readiness 75 k€ – 800 k$ · programmes 1–10 M$+ · TJM 200–400 € | Partiel (bureaux GE/LS, delivery international) | ✅ mais adapté grands comptes | 🟠 sur PME exportatrices | "Over-buy" structurel pour une PME de 40 pers. : un deck six chiffres non implémenté. Nous = le milieu de gamme implémenté |
| 6 | **Boutiques AI Act EU** (Alice Labs ~30–120 k$ ; ARCKONE BE ; Embed AI sprint fixe 9 900 €) | Ingénieurs-compliance | Readiness fixed-scope, doc Annexe IV livrée en construisant | ❌ | ✅ technique | 🟡 | Pas de droit suisse, pas de FR-CH, pas de socle RGPD romand |
| 7 | **SaaS gouvernance IA** (OneTrust, Vanta, Credo AI, Saidot, Holistic, IBM watsonx, ServiceNow, Truyo) | Logiciel | Licences 10–20 k€/an entrée → 250 k$/an (Truyo) · IBM 42 k$/an base | ❌ (EN) | 🟡 outils, pas de service | 🟡 | "Un registre ne fait pas la conformité" — l'art. 50 est un ticket d'ingénierie, pas un achat de licence. Ils n'implémentent rien |
| 8 | **Agences GEO/AI-SEO US** (Helium SEO/ORCA, Logarithmic, Xpand/MentionLayer, GrindstoneSEO, RevenueZen, Lucorp) | Audit visibilité IA | GEO audits 30 jours, 6–8 moteurs, benchmark concurrents, Xpand = audit gratuit (lead magnet) | ❌ US/EN | ❌ zéro angle réglementaire | 🟠 sur l'offre agent-readiness | Ils mesurent (comme notre skill cua-driver) mais ne vendent pas la conformité. Notre pitch = la capture EST un risque juridique |
| 9 | **Vendors IA non-conformes** (Vercel "V", OpenAI Enterprise, MS Copilot, wrappers OpenAI, agences digitales) | Cibles du pitch moat | Templates IA / GPT rebrandé / "solutions IA sur-mesure" | — | ❌ tous non-conformes art. 50 | ⚪ (ce sont des cibles, pas des concurrents) | Cf. `moat-compliance-pitch.md` §2 — tableau complet |
| 10 | **Concurrents harness** (Polsia, VibeMarketer, ÉLYSIA, Lead Mapping 99 €/mois ; objection régie Ventalon) | SaaS/services marketing | Polsia "AI co-founder" cloud US · Lead Mapping = ancre prix max FR-CH | ❌ | ❌ | 🟡 (offre harness) | Matrice complète dans `marketing-playbook.md` |
| 11 | **App-builders IA** (Newly 25–199 $/mois, Lovable, Bolt) | Générateurs de marché | Apps natives RN générées en jours, Supabase inclus | — | ❌ (art. 50, art. 28 cascade sous-traitants) | ⚪ **pipeline clients** | Chaque app générée = code non relu + données perso + IA embarquée → futur SKU "Audit App IA-générée" (1 500–2 500 €) |

---

## 2. Fiches détaillées par segment

### 2.1 Big 4 & intégrateurs — le surdimensionnement structurel

**Prix constatés (2026)** : readiness assessment 75–400 k$ (Big 4 / cabinets tech), classification Annexe III 75–400 k$/système, doc technique Annexe IV 50–200 k$/système, programmes complets 1–10 M$+. TJM 200–400 €. Big 4 = 30–100 % plus cher que les boutiques à périmètre égal.

**Réalité PME (source Flint Brief, 06/2026)** : pour une PME de 40 personnes avec 2 outils IA, le Big 4 est *"the classic over-buy: a six-figure deck that does not get implemented, delivered by people who would rather be on a Fortune 500 account"*.

**Budget réaliste d'un déployeur SME (source aiactblog.nl, 07/2026)** : 5–25 k€ an 1 (inventaire 2–10 k€, classification 3–15 k€, formation 49–1 395 €/pers). → **Notre audit à 890–3 500 € se situe sous le plancher du marché documenté, en positionnement pénétrant assumé** (cf. `cortex-leman-pricing.md` : "sous le marché pour pénétrer").

**Usage** : citer les tarifs Big 4 comme ancre haute dans les propositions ("un readiness Big 4 démarre à 75 k€ — notre Diagnostic : 890 €").

### 2.2 Concurrents suisses — le flanc romand

| Cabinet | Base | Offre data/AI | Prix | Menace |
|---|---|---|---|---|
| **sidd.swiss** | DE (FR sur demande) | CPD externe, AI Officer, AI Governance Check, AI Security LLM/RAG/agents, ISO 42001, NIS2, pentests | CPD/AI Officer dès CHF 500/mois · AI Governance Check dès CHF 3 900 | 🔴 |
| **Comity Sàrl** | Lausanne (Galerie St-François) | DPO as a Service, Audit & Compliance, Privacy Engineering | n.c. | 🟠 |
| **Zenith Advisory** (Viventis Group) | Saillon VS (vérifié 22/08 — pas Lausanne/GE) | Zenith-DPO, Zenith-CISO, Zenith-Guardian's (dark web/EASM) · simulateur maturité gratuit en ligne = lead magnet. **Aucun service IA.** | n.c. | 🟠 |
| **datago sa** | Genève + Lausanne (13 pers., fondée 2019, croissance LinkedIn ~+50 %/an) | Gouvernance + DPO + sécurité IT + gestion de crise — mix juristes/tech/développeurs. Profil le plus capable de basculer vers l'IA | n.c. | 🟠 (bascule la plus rapide) |
| **Meanquest SA** | Ecublens, Meyrin, Givisiez (3 sites romands) | DPO as a Service désigné auprès du PFPDT, au sein d'une boîte IT généraliste | n.c. | 🟠 |
| **Data Protection Company** (data-protection-agency.ch) | Suisse romande — se dit « 1ère agence romande » nLPD/RGPD, cible PME assumée | DPO externe, DPIA, revue annuelle, contrats sous-traitants | n.c. | 🟠 |
| **Altheis** | Romandie | DPO externe LPD/RGPD, gestion violations, formation — pitch : « amendes CHF 250 k à titre personnel des dirigeants » (argument à récupérer pour l'art. 50) | n.c. | 🟡 |
| **datalex** | Genève | DPO-as-a-service via avocats partenaires, réseau mondial PrivacyRules | n.c. | 🟡 |
| **e-secure** | Le Grand-Saconnex (GE) | Cyberdiagnostic + DPO as a Service + ISO 27001 — profil cyber | n.c. | 🟡 |
| **DPO Consulting** | CH | LPD & RGPD, DPO externalisé | n.c. | 🟡 |
| **datenschutzkonform.ch** | DE/KMU | DPO as a Service abonnement | dès CHF 290/mois | 🟡 (ancre basse prix) |
| **Fidens / tvh consulting** | CH (Suisse alémanique surtout) | RSSI/DPO externalisé, pool 40 consultants | dès 1 jour/semaine | 🟡 |
| **DP&S** | CH | DPO externe, gouvernance données, formations | n.c. | 🟡 |

**Lecture stratégique** : sidd.swiss valide le marché (offre IA-gouvernance complète + prix publiés — leur AI Governance Check à CHF 3 900 ≈ notre Audit à 3 500 € = benchmark direct). Personne ne tient le créneau **francophone romand + PME + implémentation**. Le marché DPO romand est **commoditisé** (8+ joueurs, plusieurs positionnés PME) : y entrer = fosse, pas gap. **Aucun n'affiche d'offre AI Act / IA en production** (vérifié 22/08) — la thèse centrale tient. Risque de bascule le plus rapide : **datago** (mix tech+juridique, en croissance) — surveillance rapprochée. Ce crowd = **cibles prioritaires du canal « Co-pilote DPO IA »** (leur apporter la couche IA avant qu'ils la construisent en interne).

### 2.3 SaaS de gouvernance IA — le leurre d'achat

OneTrust (registre, Visionary Gartner MQ 2026), Vanta (150+ contrôles, 16 politiques, 4 tiers), Credo AI, Saidot (EU-natif), Holistic AI (40+ tests techniques), IBM watsonx.governance (42 k$/an, 5 use cases, +15 960 $/use case), ServiceNow AI Control Tower (bundlé 2026), Truyo (250 k$/an).

**Verdict marché (Beri, 08/2026)** : *"The obligation that landed on 2 August 2026 is Article 50 transparency, and no governance platform discharges it… it is an engineering ticket, not a procurement."* Pour une PME avec 5 systèmes IA, un registre structuré dans l'outillage existant suffit. L'entrée SaaS à 10–20 k€/an sans implémentation = le piège d'achat.

**Usage** : réponse à l'objection "je prendrai un outil" — l'outil ne fait ni l'inventaire réel, ni l'art. 50, ni les correctifs.

### 2.4 Agences GEO/AI-SEO — occupent la mesure, pas la compliance

| Agence | Produit | Particularité |
|---|---|---|
| Helium SEO (ORCA) | GEO mesuré sur 8 moteurs, questions ICP réelles, vérification factuelle des claims, sessions achat multi-tours | Le plus sophistiqué (US) |
| Logarithmic | GEO Audit 2 semaines, 7 catégories pondérées, rapport 18–24 p., plan 30 jours | Cible entreprises |
| Xpand Digital (MentionLayer) | Audit visibilité IA + SaaS ; Index Q1 2026 : **65,9 % de 1 004 entreprises invisibles dans la recherche IA** | **Audit gratuit = lead magnet** (stat à réutiliser dans notre pitch) |
| GrindstoneSEO | Audit 30 jours, 12 checks, 3 couches, query set épinglé, white-label agences | Méthode documentée publiquement |
| RevenueZen, Lucorpmedia | Audits + outils gratuits, services mensuels | Bas de gamme |

**Notre différenciation vs tous** : ils mesurent la visibilité (marketing) ; nous vendons la **mise en conformité de la présence IA** (AI Act art. 50 + RGPD art. 5.1.d exactitude — info publique périmée/trompeuse = risque juridique). Leurs méthodes (query sets épinglés, benchmark 3 concurrents, citation share) sont à **recopier** dans le skill `agent-readiness-audit`. La stat Xpand (65,9 % invisibles) = hook de contenu.

### 2.5 ZénithIA — fiche de référence (déjà documentée)

Voir `hermes-skills-backup/cortex-leman-business-generator/references/zenithia-competitive-analysis.md` (fiche complète) : CA 750 k€, tiers 500 €–50 k€, n8n+Claude, zéro compliance, FR-only. **À copier** : pipeline proposition auto (transcript appel → Claude → Gamma → signature), technique "miroir des mots du client", funnel contenu→communauté→B2B, clarté des 3 tiers.

### 2.6 Ancres pricing consolidées

| Repère | Prix | Source |
|---|---|---|
| Sanction art. 50 AI Act | jusqu'à 15 M€ / 3 % CA (live) | Règlement UE 2024/1689 |
| Sanction pratiques interdites | 35 M€ / 7 % CA | idem |
| Sanction CNIL moyenne (ROI) | 30–200 k€ | doc interne pricing |
| Readiness Big 4 | 75–800 k$ | Alice Labs benchmark 07/2026 |
| SME déployeur an 1 (réaliste) | 5–25 k€ | aiactblog.nl 07/2026 |
| Sprint fixe boutique EU | 9 900 € (Embed AI) | aiactblog.nl |
| AI Governance Check CH | CHF 3 900 (sidd.swiss) | sidd.swiss 08/2026 |
| AI Officer CH | CHF 500/mois (sidd.swiss) | idem |
| DPO externe CH | CHF 290–500/mois (DE) · 400–1 500 €/mois (FR) | datenschutzkonform.ch · doc interne |
| SaaS gouvernance entrée | 10–20 k€/an | aiactblog.nl |
| **Nos audits compliance** | **890 € / 3 500 € / 750 €/mois** | cortex-leman-pricing.md |
| **Notre audit agent-readiness (GEO)** | **1 500–3 500 CHF one-shot · 290–590 CHF/mois loop** | agent-readiness-offer.md (SKU distinct des audits compliance) |
| GEO audit US | diagnostic 2–4 semaines, souvent gratuit en lead magnet | Helium, Xpand 2026 |

---

## 3. Mise à jour réglementale critique (à propager dans le moat pitch)

Le `moat-compliance-pitch.md` (v1.0, 09/08) **portait** des échéances **périmées** sur deux points (corrigées en v1.1 le 22/08 — voir Action ci-dessous) :

| Point | Moat doc (09/08) | Réalité (08/2026, vérifiée) |
|---|---|---|
| Évaluation d'impact IA | "2 février 2027" | High-risk Annexe III → **02/12/2027** (report Digital Omnibus) |
| Registre des usages IA | "2 août 2027" | Annexe I embarqué → **02/08/2028** |
| Art. 50 transparence | "en vigueur 2 août 2026" | ✅ confirmé — seule obligation majeure LIVE, 15 M€/3 %, marking des systèmes pré-08/2026 toléré jusqu'au 02/12/2026 |

**Action** : ~~mettre à jour le tableau §1.1 du moat pitch~~ **FAIT 22/08 (accord utilisateur)** — moat passé en v1.1 : les deux échéances corrigées (évaluation d'impact → 02/12/2027, registre → 02/08/2028), mentions de l'ancienne date conservées entre parenthèses pour traçabilité. Le raisonnement central (moat compliance) en sort **renforcé** : l'art. 50 est exactement ce que les concurrents ignorent et ce que nous auditons.

---

## 4. Monitoring — qui watcher, où, à quelle fréquence

| Cible | Canal | Fréquence | Signal déclencheur |
|---|---|---|---|
| sidd.swiss | /fr/services | trimestrielle | offre FR native = 🔴→rouge vif, réagir (contenu romand + SEO local) |
| Comity, Zenith Advisory, datago, Data Protection Company | sites + LinkedIn | trimestrielle | apparition d'une offre "IA" / "AI Act" |
| clem.entreprend (ZénithIA) | YouTube | trimestrielle | premier contenu "RGPD" ou "compliance" sérieux |
| Newly / Lovable / Bolt | pricing pages | semestrielle | maturité compliance de leurs sorties (génère ou tarit notre SKU audit d'apps) |
| Agences GEO | Helium, Xpand (MentionLayer) | semestrielle | un GEO player qui ajoute un angle légal = bascule 🟠→🔴 sur agent-readiness |
| Big 4 CH | publications Genève/Lausanne | semestrielle | offre "SME AI Act" packagée sous 20 k€ |
| Réglementaire | Journal officiel UE / OFCOM / Préposée LPD | continue via skill veille | citation de normes CEN-CENELEC (la première EN 18286 publiée 07/2026, non citée), textes d'application LPD révisée |

---

## 5. Trous restants (v1.0)

- [ ] Concurrents GEO/AI-SEO **francophones** (agences FR/CH faisant du GEO) — recherche dédiée à faire
- [ ] Cabinets romands supplémentaires (VEVEY/Montreux, Fribourg, Neuchâtel) — inventaire terrain
- [ ] Tarifs publics de Comity / Zenith / DP&S (demandes d'offre simulées)
- [ ] Positionnement d'ISACA Switzerland / CLUSIS / associations cybersécu romandes sur l'AI Act
- [x] ~~Analyse de Profilage (CH) et autres DPO-as-a-service romands sur les places genevoises~~ **FAIT 22/08 (v1.1)** — 7 cabinets ajoutés §2.2 : datago, Meanquest, Data Protection Company, Altheis, datalex, e-secure, DPO Consulting. Résiduel : « Profilage (CH) » introuvable sous ce nom en recherche web — à recouper avec Tars.

---

## 6. Sources (recherche 22/08/2026)

- alicelabs.ai/en/insights/eu-ai-act-compliance-consultants-2026 (13 cabinets classés, prix)
- flintbrief.com/articles/ai-act-compliance-help-eu-smes-2026 (3 lanes, sur-achat Big 4)
- aiactblog.nl/en/posts/what-does-eu-ai-act-compliance-cost-realistic-numbers (budgets réels)
- beri.net/article/eu-ai-act-governance-platforms-inventory-vs-policy-packs (plateformes, Digital Omnibus)
- omidsaffari.com/blog/eu-ai-act (8 outils comparés)
- sidd.swiss/fr/services · comity.ch · zenithadvisory.ch · datenschutzkonform.ch · tvhconsulting.ch · dps.expert
- Recherche DPO romands 22/08 (v1.1) : datago.ch · meanquest.ch/securite/dpo-as-a-service · data-protection-agency.ch · altheis.ch/protection-des-donnees · datalex.ch/expertises/dpo-as-a-service · e-secure.ch/services · dpoconsulting.ch — aucun service IA/AI Act affiché. zenithadvisory.ch vérifié en direct 22/08 : base Saillon VS, aucun service IA, lead magnet simulateur cyber.
- helium-seo.com/generative-engine-optimization-services · logarithmic.com/geo-audit · xpanddigital.io/ai-visibility-audit · grindstoneseo.com/services/geo-audit
- newly.app/app-creator (analyse du 22/08 — générateur de marché)
- Docs internes : moat-compliance-pitch.md, zenithia-competitive-analysis.md, marketing-playbook.md, cortex-leman-pricing.md, agent-readiness-offer.md
