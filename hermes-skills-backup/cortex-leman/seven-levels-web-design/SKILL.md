---
name: seven-levels-web-design
description: "Use when building premium websites. 7-level quality system."
version: 1.0.0
---

# Seven Levels of Web Design — Framework

**Source**: Jack Roberts, YouTube 130k+ vues, juillet 2026. Adapté pour pipeline Cortex Leman.

## Principe clé

Chaque niveau **cumule** le précédent. On ne saute pas de niveaux — on ajoute des couches. Le passage du niveau 1 au 7 fait passer la qualité de 3/100 à 95/100.

---

## Level 0: Direction Esthétique Explicite (Anti-Slop Gate)

**Concept volé de**: Anthropic `frontend-design` (168k GH stars, août 2026) + notre analyse `signal-deliberation`.

**Le problème**: Sans direction explicite, l'IA produit toujours la même chose — gradient violet, Inter, layout startup générique. C'est le "AI slop".

**La règle**: Avant d'écrire une seule ligne de code, le modèle DOIT s'engager dans une direction esthétique. C'est un **gate obligatoire** — aucune génération sans choix explicite.

### Les 6 directions (adapter librement)

| Direction | Quand l'utiliser | Signatures visuelles |
|---|---|---|
| **Brutaliste** | Tech, developer tools, portfolio | Mono fonts, raw HTML feel, contrastes durs, pas de décoration |
| **Éditorial** | Media, consulting, juridique, luxe discret | Serif, whitespace généreux, hiérarchie typographique forte, grid stricte |
| **Rétro-futuriste** | Gaming, crypto, innovation | Neon, glows, CRT effects, grilles techniques, monospace accents |
| **Luxe** | Hôtellerie, bijouterie, premium | Or/argent, serif élégant, animations lentes, beaucoup de noir |
| **Maximaliste** | Créatif, agence, entertainment | Couleurs saturées, patterns denses, typographie expressive, couches |
| **Organique** | Bien-être, food, nature, éducation | Courbes, verts/terracotta, rounded corners, soft shadows |

### Prompt type (gate obligatoire)

Avant toute génération, demander au client/modèle:
```
AVANT DE CODER — Choisis UNE direction esthétique parmi:
brutaliste / éditorial / rétro-futuriste / luxe / maximaliste / organique

Justifie en 1 ligne pourquoi ce style pour ce projet.
Puis définis: palette (3-5 couleurs avec hex), typographie (1 display + 1 body),
et 3 principes de composition qui guideront chaque section.
```

**Pour les projets Tars existants:**
| Projet | Direction | Pourquoi |
|---|---|---|
| **AlConst** | Éditorial | Consulting digital FR-CH, ton sérieux, monochrome Josefin Sans + accent #E89560 |
| **Cortex Leman** | Éditorial + Organique | PME FR-CH, confiance, chaleur locale (Léman, montagnes) |
| **Baobab Kids** | Organique + Maximaliste | Enfants, couleurs vives, courbes, fun |

### Pitfall Level 0
- ❌ Ne JAMAIS accepter "moderne et épuré" comme direction — c'est du slop déguisé
- ❌ Ne pas mélanger plus de 2 directions — ça devient incohérent
- ❌ Le gate est NON-NÉGOCIABLE — pas de Level 1-7 sans Level 0 d'abord

---

## Level 1: Grab & Go (3/100)

**Ce qu'on fait**: Prompt direct — "Build me a website about X"
**Résultat**: Site générique, flottant, "AI website feel"
**À utiliser pour**: Prototype rapide, validation structure

## Level 2: Screenshots & References (10/100)

**Ce qu'on fait**: Fournir des images de référence (screenshots de sites primés)
**Sources**: godly.io, Landbook, Awwwards, Dribbble, Glido (par catégorie)
**Prompt type**: *"Update the website using this image as a reference style"*
**À utiliser pour**: Définir la direction visuelle avec le client

## Level 3: Design Skills (25/100)

**Ce qu'on fait**: Installer des skills de design pré-emballés dans Claude/Hermes
**Skills clés**:
- UI/UX Pro Max — 67 UI styles, 161 color palettes, font pairings
- Shadcn UI — système de composants
- Power Design — principes de design universels
**Prompt type**: *"Use all the best skills and design principles to build a beautiful website"*
**À utiliser pour**: Baseline qualité pour tout projet

## Level 4: Image & Video Generation (40/100)

**Ce qu'on fait**: Générer des assets visuels IA qui s'intègrent dans le site
**Outils**:
- Images: OpenArt (Nanabanana 2), GPT Image 2, Seedream
- Vidéo: Seedance 2.0, Kling (via MCP ou API)
- Format: générer 2-4 variations, white background, ratios adaptés
**Technique**: Connecter le générateur via MCP → Claude génère les assets programmatiquement pendant qu'il build le site
**Prompt type**: *"Build me this website and generate beautiful images that slot in and be relevant"*

## Level 5: UI Snapping + Animated Components (55/100)

**Ce qu'on fait**: Copier-coller des composants UI réels et animés depuis des librairies open-source
**Innovation**: Ne pas réinventer la roue — réutiliser du code battle-tested. Les composants animés font passer un site de "template IA" à "studio d'agence".

### Librairies de composants (toutes gratuites)

| Librairie | URL | Stack | Points forts |
|---|---|---|---|
| **Originkit** ⭐ | originkit.dev | React + Tailwind + **MCP server** | Plus grosse collection. L'agent peut installer directement via MCP. Hero sections, animations complexes. |
| **Animate UI** | animate-ui.com | React + TypeScript + Motion + Shadcn CLI | Composants fully animated, install via Shadcn CLI |
| **React Bits** | reactbits.dev | React open-source | Composants interactifs, high quality |
| **21st.dev** | 21st.dev | 12,000+ React/Tailwind | Plus grand catalogue, install en une commande |
| **beUI** | beui.dev | React + Next.js + Motion | Composants animated pour Next.js |
| **Magic UI** | magicui.design | React + Tailwind | Micro-interactions, effets visuels |

### Technique

1. Trouver un composant (hero animé, carte interactive, effet de scroll, background dynamique)
2. Copier le code OU installer via CLI (`npx shadcn add ...`)
3. Donner l'URL du composant à l'agent qui l'intègre
4. **Originkit MCP** — connecter le serveur MCP Originkit pour que l'agent navigue et installe les composants programmatiquement

**Prompt type**: *"Integrate this animated hero component from Originkit at the top of the page" + URL*
**Pattern @Praha37v** (août 2026): Choisir un composant animé → copier → intégrer = hero section premium en 2 min, gratuitement.

## Level 6: Finding the Data (75/100)

**Ce qu'on fait**: Scraper les sites concurrents gagnants et perdants pour extraire les patterns de conversion
**Outil**: `scripts/competitor_scraper.py` (rempari local sans dépendance — validé sur tailwindcss.com, vercel.com, linear.app). Voir `batch-design` pour comparer N sites en un run. Alternative upgrade: Firecrawl MCP (service payant).
**Prompt type** (roasting + research):
```
I'm launching a [business type] in [location].
Go online and find the 10 most successful [niche] businesses in [city].
Find 10 that are NOT doing well.
Do comprehensive research: What do winners have that losers don't?
What do they have in common? Order of website elements? CTA placement?
Create a scoring matrix for what makes a great website.
Output: a clear blueprint to pass to another model to create a winning formula.
Everything must be evidenced. Cross-validate with a different model.
Use the Firecrawl MCP to do the research.
```
**À utiliser pour**: Tout site client — ne JAMAIS livrer sans cette étape

## Level 7: Design Extraction (95/100)

**Ce qu'on fait**: Extraire l'identité de design complète d'un site award-winning et la répliquer
**Technique**:
1. Trouver un site de référence (ex: Anti-gravity Google)
2. Demander à Claude d'extraire: typography, colors, golden ratios, spacing, animations, design rules
3. Créer un "design blueprint" (document de spécifications)
4. Passer ce blueprint + les skills + les données niveau 6 à Fable 5 / Claude
**Prompt type**:
```
I'm giving you a website. Understand the design: typography, colors, ratios, spacing, animations.
Extract a design blueprint following all instructions in this file.
Then build a website that levels this up. Our website is about [topic].
```
**Résultat**: Site premium one-shot qui comprend les principes de design invisibles (golden ratio, white space, animation timing)

---

## Workflow Cortex Leman — Application pratique

### Pour un site client PME FR-CH

1. **Niveau 6 d'abord** — Firecrawl scrape 10 gagnants + 10 perdants dans la niche du client
2. **Niveau 7** — Extraire le design blueprint d'un site award-winning pertinent
3. **Niveau 3** — Installer les skills design (UI/UX Pro Max, Shadcn)
4. **Niveau 4** — Générer assets visuels (produits, équipe, lieux via Seedance/GPT Image)
5. **Niveau 5** — Snapper les composants UI manquants (animations, interactions)
6. **Build final** — Combiner blueprint + data + skills + assets + composants en un prompt

### Outils nécessaires

| Outil | Rôle | Statut Hermes |
|---|---|---|
| `competitor_scraper.py` | Scraping concurrentiel | ✅ Script local |
| OpenArt / GPT Image 2 | Asset visuels | ✅ (kie.ai) |
| Seedance 2.0 | Vidéo produit | ✅ (kie.ai) |
| Originkit (MCP) | Composants animés + hero sections | ✅ MCP server |
| 21st.dev / Animate UI | Composants UI + animations | ✅ Gratuit |
| React Bits / beUI | Composants React animés | ✅ Gratuit |
| UI/UX Pro Max skill | Design principles | À créer comme skill |
| Fable 5 | Modèle build | Claude/Anthropic |

### Pitfalls

- **Ne pas sauter le niveau 6** — un beau site sans data conversion = Ferrari sans moteur
- **Le modèle n'est qu'un multiplicateur** — Fable 5/Claude accélère mais les skills font la qualité
- **Toujours 2-4 variations d'images** — ne jamais utiliser la première génération
- **White background pour assets produits** — facilite l'intégration CSS
