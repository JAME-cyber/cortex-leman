# Division du Travail — Tars vs OpenCode

> **Document de coordination inter-laptops.** Ce fichier vit dans le repo `cortex-leman`
> (syncé GitHub) pour être lisible depuis les deux machines. Il définit **qui fait quoi**
> pour ne pas gaspiller le travail structurel déjà effectué côté Tars.

**Date:** 2026-08-16 (v2)
**Statut:** Actif — à mettre à jour à chaque nouveau projet

---

## 1. Principe fondateur (v2)

> **Tars est l'exécutant par défaut sur TOUT. OpenCode est une capacité de débordement.**

La v1 séparait "structure" (Tars) et "web" (OpenCode). **Cette frontière était artificielle** :
Tars fait aussi le web (HTML/React/Vite, Playwright, déploiement Cloudflare Pages — alconst
et darkom déployés depuis Tars). Le périmètre "web" d'OpenCode n'apporte aucune compétence
que Tars n'a pas.

Ce que la 2e machine apporte réellement :

| Bénéfice | Réel ? | Détail |
|---|---|---|
| Parallélisme matériel | ✅ | 2 pipelines simultanés (render vidéo pendant qu'un front itère) |
| Redondance | ✅ | Une machine down ≠ arrêt total |
| Budget API séparé | ✅ marginal | GLM-4.5-flash sur n8n local |
| Compétences web exclusives | ❌ | Tars fait tout, y compris Playwright et les déploiements |

**Règle d'or :** OpenCode ne prend un projet que si Tars est saturé (render long, crawl,
batch) ou si le travail doit tourner en parallèle d'un gros job Tars. Sinon → Tars.

---

## 2. Matrice des projets (qui fait quoi)

| Projet | Nature | Propriétaire | Notes |
|---|---|---|---|
| **cortex-leman** | Système agentique + assets | 🔵 Tars | Skills, guardrails, anti-sycophancie, docs, vidéo Sankofa |
| **dropship-atom** | Pipeline agentic (7 agents) | 🔵 Tars | Scoring déterministe — ne pas dupliquer |
| **compliance-skills** | 12 skills réglementaires | 🔵 Tars | RGPD, AI Act, secret professionnel |
| **alconst-website** | Site vitrine | 🔵 Tars | HTML, Cloudflare Pages — reprise par Tars |
| **darkom-debarras** | Site métier | 🔵 Tars | React+TS+Vite, SEO/RGPD fait (07/07) |
| **idol-card-dreams** | App cards | 🔵 Tars | **candidat reprise n°1** (stagnant depuis 03/03) |
| **socialpulse-mvp** | Lead gen (7 agents) | 🔵 Tars | Agents Python + scoring + pages demo |
| **import-export-strategy** | Carte stratégique | 🔵 Tars | Stratégie + dashboard HTML |
| **12_agents** (D:\) | Pipeline n8n + GLM-4 | 🔵 Tars | Structure pipeline + couche GLM-4.5-flash |

OpenCode = **débordement à la demande** : gros renders, crawls longs, tests de charge —
attribués explicitement quand Tars est saturé, jamais par défaut.

---

## 3. Périmètre Tars (défaut sur tout)

- Skills Hermes Cortex Leman (Gardien des Normes, Narrateur, Oeil, Architecte)
- Anti-sycophancie et cost tracking
- Scoring déterministe dropship-atom, 12 skills compliance
- **Sites web : alconst, darkom, idol-card-dreams** (front, SEO, déploiement, Playwright)
- Front des projets hybrides : socialpulse demo/, import-export dashboard
- Tout raisonnement stratégique produit par Hermes/Pi

## 4. Périmètre OpenCode (débordement)

Uniquement sur assignation explicite (Tars saturé / travail parallèle nécessaire) :

- Gros renders vidéo, crawls longs, batches massifs, tests de charge
- Exécution de specs produites par Tars — jamais de refonte structurelle en autonomie
- **Jamais** : skills, guardrails, scoring, secrets, backups, déploiements

---

## 5. Interfaces entre les deux stacks

```
Tars (exécutant défaut — specs, plans, audits, web, déploiement)
    │  assignation de débordement: spec + contexte + clés via vault
    ▼
OpenCode (capacité parallèle — renders, crawls, batches)
    │  livrables + evidence (logs, captures)
    ▼
Repo cortex-leman (GitHub — point de sync unique)
```

**Pipeline de contenu (optionnel mais validé):**
```
n8n (13 agents) → GLM-4.5-flash → contenu structuré → alimente les sites
```

---

## 6. Règles d'engagement

1. **Un propriétaire par couche** — si Tars a déjà un plan/audit/scoring pour un sujet, OpenCode l'utilise, ne le recrée pas.
2. **Le repo cortex-leman est le point de sync** — toute décision structurante y est documentée (lisible depuis les deux laptops). Pull avant push.
3. **Demander avant de toucher** — un élément du périmètre Tars (skill, scoring, guardrail) ne se modifie pas sans accord.
4. **Preuve avant livraison** — livraison avec tests (Playwright) et evidence (logs, captures).
5. **Sécurité des clés** — jamais de clé API dans les repos publics (leçons apprises : clés ZAI/Kie exposées dans cortex-leman, purgées et révoquées 16/08).
6. **Les clés vivent UNIQUEMENT dans le vault chiffré** (`~/.hermes/vault/vault.py` sur chaque machine) — jamais en dur dans un fichier, un backup, ou un message. Config → `api_key_env_var` uniquement.
7. **Tout backup poussé sur GitHub passe un scan de secrets avant push** (`git grep` patterns de clés) — l'incident d'août est parti d'un backup non scanné.

---

## 7. Projets en attente / à cadrer

- [ ] Reprise **idol-card-dreams** (décision: relancer la partie front ?)
- [ ] Évolutions **alconst-website** (liste des sections à ajouter)
- [ ] Évolutions **darkom-debarras** (devis, photos, zones)
- [ ] Interface n8n→sites (brancher la génération GLM-4.5-flash sur un site réel)
- [x] ~~Révocation des clés API exposées~~ **FAIT 16/08** — clés révoquées (test API = 401), purge historique complète effectuée

---

## 8. Historique

| Date | Événement |
|---|---|
| 2026-08-16 | Création du document — division Tars (structure) / OpenCode (web) actée |
| 2026-08-16 | INCIDENT SÉCURITÉ clos: clés ZAI+Kie exposées → révoquées (vérifié API 401), historique git purgé (filter-repo, 0 clé complète restante), nouvelle clé ZAI vaultée |
| 2026-08-16 | **v2** — Refonte de la division : Tars = exécutant défaut sur tout (web inclus), OpenCode = capacité de débordement uniquement. Frontière "structure/web" abandonnée (artificielle). |
