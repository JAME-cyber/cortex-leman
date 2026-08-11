# Offre Cortex Leman — Audit Agent-Readiness PME FR-CH

> Source d'inspiration : Greg Isenberg, *"Cloudflare will make 1000+ AI millionaires"* (2026-08-10),
> idée #2 « agent readiness for businesses ». Adapté au moat compliance Cortex Leman.
> Skill exécutable : `agent-readiness-audit`. Créé le 2026-08-10.

---

## Le constat qui vend

Les acheteurs demandent désormais à **une IA** : *« meilleur fiduciaire à Lausanne »*,
*« recommande-moi un cabinet RGPD en Suisse romande »*, *« compare X et Y »*.
Si la PME **n'apparaît pas**, est **mal représentée** (tarif faux, service erroné),
ou n'est **pas lisible par les agents** → elle perd des affaires qu'elle ne sait
même pas qu'elle rate.

**Et ce n'est plus seulement du marketing : c'est de la conformité.** L'**AI Act
art. 50** (transparence) et le **RGPD art. 5.1.d** (exactitude) font que
l'information publique **périmée ou trompeuse** devient un **risque juridique**.
Là est le moat Cortex Leman : on ne vend pas du « AI-SEO », on vend une
**mise en conformité de la présence IA**.

## Pitch en une phrase

> *« Voici exactement ce que les assistants IA disent de vous aujourd'hui — et
> ce que la réglementation vous oblige à corriger. »*

La **capture d'écran** (= ce que ChatGPT/Gemini répondent) **est le pitch**.
Pas de deck. Pas d'argumentaire. Le constat parle.

## Ce qu'on livre (l'audit)

| Bloc | Contenu |
|---|---|
| **1. Snapshot IA** | 15–20 prompts d'intention d'achat lancés sur ChatGPT, Gemini, Claude, Perplexity → apparaît-on ? recommandé ? faits corrects ? (captures) |
| **2. Scorecard /20** | `llms.txt`, `robots.txt` crawlers IA, schema.org, parsabilité pricing, docs, pages comparaison, FAQ structurée, endpoint MCP/search |
| **3. Risques conformité** | croisement **AI Act art. 50 + RGPD art. 5.1.d** — chaque écart flagué `⚠ RISQUE` avec article + correctif |
| **4. Feuille de route** | quick wins → moyen terme → avancé, **chiffrés** (effort + rationale compliance) |

Outil d'exécution : le skill `agent-readiness-audit`, qui pilote le navigateur
via le MCP `cua-driver` pour interroger **réellement** les IA (pas une approximation).

## Tarification (cohérente avec `plan-pricing`)

| Offre | Prix | Cible |
|---|---|---|
| **Audit one-shot** | **1 500 – 3 500 CHF** | PME FR-CH, entrée de gamme |
| **Correctifs** (implémentation) | sur devis | selon scorecard |
| **Loop mensuelle** (re-mesure + suivi) | **290 – 590 CHF/mois** | fidélisation, MRR |

Ancrage valeur : une PME qui signe **1 client de plus / an** grâce à une meilleure
visibilité IA amortit l'audit ×10. Le correctif compliance **évite un risque
juridique** non chiffrable → le pricing se défend seul.

## Le wedge GTM (l'astuce Greg)

Ne pas (seulement) vendre à la PME finale. **Vendre d'abord à ceux qui vendent
aux PME FR-CH** :
- **Fiduciaires** (ils ont déjà la relation de confiance PME)
- **Agences marketing / web locales**
- **Conseillers TIC / digitalisation** (Office digital cantonal, etc.)
- **Avocats d'affaires PME**

Ils **revendent** l'audit à leur portfolio → distribution immédiate, pas de
prospection froide. Argument : *« enrichissez votre offre existante d'un
diagnostic IA que vos clients réclament déjà »*.

## Trajectoire productisation (crawl → walk → run)

1. **Services main** : audit livré à la main, 10 clients dans 1 vertical
   (ex. fiduciaires VS/VD/GE)
2. **Dashboard** : le snapshot automatisé mensuel = le MRR
3. **API / MCP** : l'outil de scoring exposé comme ressource agent
   → là où rejoint le **pay-per-request** (Stripe metered aujourd'hui,
   HTTP 402 Cloudflare demain)

C'est exactement la séquence du skill `plan-pricing` (services → produit → API).

## Pourquoi c'est défendable (moat)

1. **Compliance, pas SEO** — les agences font du AI-SEO générique ; nous
   articulons **AI Act + RGPD**, terrain personne ne tient.
2. **Capacité d'exécution** — pilotage navigateur réel des IA (`cua-driver`),
   pas un wrapper.
3. **Vertical FR-CH** — régulation + langue + marché local = doublable
   difficilement par un acteur générique.

## Risques / contre-position

- **Les IA évoluent vite** → la loop mensuelle n'est pas un gadget, c'est la
  défense contre l'obsolescence du snapshot.
- **Greg vend du hype (402/wallets agents pas mûrs)** → on monétise en
  **Stripe aujourd'hui**, pas en attente du 402.
- **Risque de devenir commodity** → d'où l'angle compliance : seul rempart
  durable contre la banalisation.

## Prochaines étapes

- [ ] Premier audit **pilote gratuit** sur une PME connue (cas client + capture)
- [ ] Page de capture (1 page, le screenshot = hero)
- [ ] 10 prospects dans le wedge (fiduciaires) — cold email avec leur propre
      capture IA en PJ
- [ ] Brancher `plan-pricing` si on veut valider/formaliser les tiers

---
*Lié : `moat-compliance-pitch.md`, `marketing-playbook.md`, skill `agent-readiness-audit`,
skills `plan-pricing` + `setup-stripe` (monétisation).*
