# Stratégie juin 2026 — Analyse multi-modèles & Premortem

**Date :** 16 juin 2026
**Auteur :** Session d'analyse (pi coding agent)
**Objet :** Analyse comparative Chine/Japon (automatisation IA), application aux 3 projets (Cortex Leman, DropAtom, ImportExport Pro), contre-analyse GPT-5.5, premortem Sonnet 4.6 + Opus 4.8.

---

## TL;DR — Le consensus des 4 modèles (Gemini + GPT-5.5 + Sonnet 4.6 + Opus 4.8)

> **Vous n'avez pas un portefeuille de projets, vous avez un mécanisme d'évitement de la vente déguisé en prototypes.**

### Hiérarchie de décision (consensus)

| Priorité | Projet | Verdict | Raison dominante |
|---|---|---|---|
| 🔥 **Tuer/Geler 1er** | **DropAtom/Pioche** | Modèle **prouvé** inviable | Break-even business = 34-60 abonnés à 99€, impossible à 49€ ; cible non rétentive |
| 🧊 **Geler ensuite** | **ImportExport Pro** | Incertain, 0 canal | Ni SaaS ni consulting défini ; base YouTube = risque légal |
| ✅ **Garder actif** | **Cortex Leman** | Survit **si** focus | Seul projet : acheteur solvable + problème réel + différenciateur défendable |
| ⛔ **Geler le code** | (tous) | 3 semaines min. | Jusqu'à 1 lettre d'intention payante |

### Cause racine commune des 3 échecs projetés
**Pas technique. Go-to-market + dispersion comme évitement de la vente.**
Signal objectif : 22 fichiers de code produits cette semaine, 0 appel prospect.

---

## Les 5 actions de la semaine (consensus dur)

1. **Geler Pioche + ImportExport** — `git tag freeze-2026-06` + `FREEZE.md` (critère de réouverture écrit). Pas delete.
2. **Choisir 1 verticale Cortex** noir sur blanc : compta **OU** avocat (pas les deux). Irrévocable.
3. **20 appels/messages à des acheteurs économiques réels** (associés de cabinet, pas LinkedIn gen). Question unique : *« Comment gérez-vous la confidentialité IA sur vos dossiers clients aujourd'hui ? »*
4. **Geler le code 3 semaines.** Zéro feature tant que pas de LOI.
5. **Tester à la main** : livrer 1 note de synthèse fiscale / revue de contrat *manuellement* à un cabinet contre paiement, avant d'automatiser.

### Métrique unique au 30/09/2026
**Combien de rendez-vous de démo avec un décideur réel ?** Si < 3 → Cortex meurt aussi.

---

## Ce que cette session a produit (livrables)

### Code (3 chantiers, validés par exécution)
| Projet | Livrable | Statut |
|---|---|---|
| DropAtom | `pioche/lib/unit_economics.py` — modèle économique unitaire pilotable | ✅ exécute, répond au débat break-even |
| ImportExport | `agents/compliance/` — chaîne HS assistée + traçable (9 fichiers) | ✅ 4/4 tests passent, tamper-detection OK |
| Cortex | `core/verticals/contract_review/` + `core/adoption/` (12 fichiers) | ✅ import OK, 12 règles JsonLogic conformes |

**2 bugs réels corrigés** : dataclass Pydantic (champs nus), journal WORM (dérive hash timestamp).

### Réponse empirique au débat break-even DropAtom
- Break-even **technique** (couvre ses propres coûts variables) = 1 abonné à ≥49€. *Le « 1 abonné » du PROJECT.yaml n'était pas complètement faux — mais c'est la définition la plus indulgente.*
- Break-even **business réel** (paie fondateur) = **34-60 abonnés à 99€**, impossible à 49€ médian, désastreux en pessimiste.
- **Recommandation chiffrée** : prix Pro ≥ 99€ (29€ et 49€ non viables).

---

## Contenu du dossier

### Analyses (à lire dans l'ordre)
- **`01-contre-analyse-gpt5.5.md`** — GPT-5.5 contre-analyse ma première grille Chine/Japon. M'a corrigé sur 4 points (binarité, break-even inventé, déterminisme douanier survendu, faiblesse des sources ImportExport). J'accepte 3.
- **`02-premortem-sonnet-4.6.md`** — Sonnet 4.6, premortem. Diagnostique la dispersion comme méta-risque. Recommende tuer ImportExport.
- **`03-premortem-opus-4.8.md`** — **Opus 4.8, premortem (le plus tranchant).** Inverse la hiérarchie : tuer Pioche (prouvé inviable) avant ImportExport (incertain). Détecte que la « réutilisation de code » est un faux levier.

### Prompts (`prompts/`) — pour traçabilité et reproduction
Les prompts exacts envoyés à chaque modèle. Permet de relancer l'analyse plus tard ou avec d'autres modèles.

---

## Note technique modèles
- « Sonnet 4.8 » et « Claude 4.8 » n'existent pas en Sonnet. Le dernier Sonnet concret est **4.6**. Les versions 4.7/4.8 ne sont sorties qu'en **Opus**. Le premortem final a été fait en **Opus 4.8** (`anthropic/claude-4.8-opus-20260528`) — le modèle le plus puissant disponible.
- Hiérarchie qualité du raisonnement observée : **Opus 4.8 > Sonnet 4.6** (plus prescriptif, probabilités plus honnètes, meilleur diagnostic psychologique).

---

## ⚠️ Point de sécurité (héritage de session)
Une clé API Google (`AIza...ynlF4`) a été partagée en clair pendant la session et stockée dans `~/.pi/web-search.json`. **Elle a été vidée du fichier local**, mais reste **active côté Google** tant qu'elle n'est pas révoquée sur https://aistudio.google.com/apikey. À faire impérativement.

---

## La seule phrase à retenir

> *Tue Pioche aujourd'hui, gèle ImportExport et SocialPulse, concentre 100% de ton attention sur UNE verticale de Cortex et obtiens une signature payante avant d'écrire une ligne de code de plus — sinon, dans 12 mois, tu auras 4 prototypes brillants et zéro euro.*
> — Opus 4.8
