# Seedance 2.0 — Patterns de prompting

Bibliothèque de 7 patterns vidéo + 1 pattern image + 1 référence accès plateforme (juil. 2026). Chaque pattern est project-agnostic par défaut — les mappings projet ne sont notés que quand ils ont été explicitement discutés en session. Source: veille X/Twitter jul 2026.

## Decision matrix

| Critère | A: Triple verrouillage | B: Escalation 6-shot | C: LLM storybreaker | D: Raw smartphone UGC | E: Travel vlog | F: Dark cinematic epic | G: Commercial brand content |
|---------|----------------------|---------------------|---------------------|----------------------|---------------------------|----------------------|---------------------------|
| **Personnages** | 2+ dans le même plan | 1 sujet central | N'importe quel | 1 seul + groupe | 1 seul récurrent | 2 adversaires + dispositif narratif | Produit + modèle récurrent |
| **Genre** | Scènes sociales, interactions | Récits épiques, batailles | N'importe quel genre | Urgence, événementiel, "mémoire" | Travel, journey, documentaire | Mythologie, combat, histoire | Publicité, promo, brand content |
| **Risque principal** | Fusion de visages/corps | Manque de spectacle | Définition manuelle des cuts lente | Trop cinématique (passe pas pour réel) | Dérive vestimentaire/identité | Rupture continuité spatiale | Texte à l'écran illisible |
| **Clé technique** | 3 couches redondantes + PROHIBITED list | Ancrage spatial réel + escalation caméra | LLM génère beats auto | Anti-cinematic tokens + jump cuts 1-2s | Verrouillage vestimentaire par inventaire | 180° rule + object permanence | Product hero shots + palette limitée |
| **Durée shot** | ~2s (anti-drift) | 2-3s (progression) | Variable | 1-2s (rapid-fire) | Bullet points séquentiels | 3-4s (actes) | 2-3s (montage produit) |
| **Cuts** | 8 | 6 | N/A | Rapides constants | N/A (montage fluide) | 5 actes | 6 environnements |
| **Niveau** | Prompting | Prompting | Architecture/pipeline | Prompting | Prompting | Prompting | Prompting |

**Règle:** choisir par nombre de personnages (1 vs 2+) × genre (spectacle vs authentique vs narratif vs commercial). Combinaisons possibles (ex: bataille avec 2 héros = A pour identité + B pour mise en scène + F pour continuité spatiale).

---

## Pattern A: Triple verrouillage d'identité multi-personnages

Le problème: tout le monde prompt l'action, personne ne verrouille l'identité → les scènes à 2+ personnages s'effondrent (visages qui fusionnent, corps qui se mélangent).

### Les 3 couches (toutes obligatoires, redondance volontaire)

**Couche 1 — Référence image:**
- Upload `image_1` et `image_2` comme références visuelles absolues
- "Use the attached images as absolute character references"

**Couche 2 — Liste de maintien exhaustive:**
```
CHARACTERS: Two realistic individuals from image_1 and image_2.
Use the attached images as absolute character references, and fully maintain
the facial features, hairstyles, hair colors, skin textures, body types,
height differences, outfits, color schemes, and age appearances of each person
across all cuts. No altering into different people, face swaps, outfit changes,
hairstyle changes, or mixing of the two individuals' features.
```

**Couche 3 — PROHIBITED list (failure modes exacts):**
```
PROHIBITED: Facial distortion, altering into different people, face or body
swaps, outfit changes, hairstyle changes, body type changes, limb multiplication,
duplicates, body fusion, penetration, warping, floating, unnatural landings,
anime style, CG style.
```

Chaque couche ferme une porte différente que le modèle sinon franchit.

### 4 principes

1. **Actions distinctes par personnage par cut** — un wall-run left, l'autre right. Le modèle ne peut pas les moyenner en un seul.
2. **Cuts courts et timed (~2s)** — le drift d'identité s'infiltre dans le motion long. 8 shots de ~2s limite la dérive.
3. **Negative prompting précis** — nommer les failure modes exacts (face swap, body fusion, limb multiplication) > décrire ce qu'on veut.
4. **Référence image systématique > texte** — pour un personnage récurrent, toujours ré-uploader l'image plutôt que redécrire.

### Workflow complet (ChatGPT Image 2 → Seedance)

1. **Character ref sheet** dans GPT Image 2 (front + 3/4 profile, plain background)
2. **Frames par scène** dans GPT Image 2 (start frames, character ref uploadé)
3. **Seedance image-to-video**: upload character ref + start frame + motion prompt avec director tokens
4. Director tokens utiles: `dolly zoom`, `push-in`, `bullet time`, `one-take`, `dutch angle`
5. **Stitch** multiple shots en gardant le même character ref

Coût: ~$0.08-0.10/sec sur kie.ai. Refine tool pour local edit sans regénérer.

Source: @NexlowX, x.com/NexlowX/status/2080982143568949500 · Guide complet: x.com/NexlowX/status/2073443937340014779

---

### Addendum pratique: Split-shot pour 3+ personnages (validé juil 2026)

Le Pattern A verrouille 2 personnages dans le même plan. Mais quand une scène nécessite **3+ personnages avec des rôles distincts** (ex: cuisinier + parent + enfant), le drift identitaire explose même avec les 3 couches.

**Solution validée: diviser en shots séparés** plutôt que tout mettre dans un seul prompt:

| Shot | Personnages | Focus |
|------|-------------|-------|
| Shot 1 | Cuisinier seul | Préparation, gestes techniques, vapeur |
| Shot 2 | Parent + enfant | Commande, échange, émotion |

Chaque shot a **1-2 personnages max** → le Pattern A standard s'applique. L'histoire se reconstruit au montage.

**Quand utiliser ce split:**
- 3+ personnages avec actions distinctes
- Un personnage principale (cuisinier) + figurants (clients)
- Scène de service/kiosk/restaurant avec interaction client

**Quand NE PAS splitter:**
- 2 personnages qui interagissent directement → Pattern A standard
- Groupe homogène sans distinction de rôle → un seul shot avec group framing

Testé Culture en Saveur (Catering V3, juil 2026): 2 clips `kiosk_chef` + `kiosk_order` = résultat net, zéro drift, 410 crédits.

---

### Addendum pratique: Casting inclusif authentique

Pour intégrer la diversité (religion, origine, genre) dans les prompts vidéo IA de manière **non-tokenistique**:

1. **Nommer le personnage** — donner un prénom (ex: "Amina") au lieu de "the Muslim girl"
2. **Framing naturel** — décrire le voile/headscarf comme un détail vestimentaire parmi d'autres, pas comme l'identité entière du personnage
3. **Action > apparence** — le personnage fait quelque chose (cuisine, sourit, participe) au lieu d'être posé comme symbole
4. **Palette cohérente** — assortir la tenue à la palette du projet (ex: hijab terracotta sur un projet Terracotta)

**Exemple prompt (bon):**
```
A girl wearing a terracotta-colored hijab carefully places flatbread dough
on a stone, her hands gentle and focused. Next to her, a boy with curly hair
sprinkles spices. They smile at each other, sharing the task with natural
teamwork and joy.
```

**Exemple prompt (à éviter — tokenistique):**
```
A diverse group including a MUSLIM girl wearing a HIJAB demonstrating INCLUSION
and DIVERSITY in this MULTICULTURAL cooking scene.
```

Testé Culture en Saveur T2 V2 (juil 2026): clip `inclusion_cooking.mp4` avec fille voilée cuisinant → validé par l'utilisateur.

---

## Pattern B: Escalation 6-shot épique

Pour récits dramatiques avec un seul sujet central. Pas besoin de verrouillage multi-personnages — tout l'effort va sur l'échelle et le spectacle.

### Structure narrative

6 shots, 2-3s chacun, escalation progressive → climax:

| Shot | Rôle | Angle caméra typique |
|------|------|---------------------|
| 1 | Hook — établir le chaos/décors | Street-level, dynamic |
| 2 | Impact — première destruction | Low-angle tracking close-up |
| 3 | Échelle — montrer la taille | Worm's-eye view climbing |
| 4 | Contexte — largeur spatiale | Epic wide aerial |
| 5 | Menace — focus sujet | Dramatic close-up |
| 6 | Climax — explosion finale | Final epic wide cinematic |

### Clés techniques

1. **Ancrage spatial précis** — nommer des lieux réels reconnaissables force le modèle à générer du contexte détaillé ("downtown Manhattan" → transposer en "Mansa Musa à Tombouctou", "reine Nzinga au combat")
2. **Sur-spécification lumière** — volumetric, god rays, lens flares, sun flares. Volontairement excessif.
3. **Décroissance distance** — chaque shot rapproche puis éloigne: street → close-up → worm's-eye → aerial → macro → wide. Variation constante.
4. **Progressive escalation** — chaque shot monte en intensité, le dernier est le climax (explosion, fireball, etc.)

### Template prompt (transposable)

```
FORMAT: 15 seconds, 16:9, 1080p, 6-shot cinematic sequence, photorealistic 8K,
dramatic volumetric lighting with sun flares and god rays, realistic physics.

Shot 1 (0-3s): [Hook — établir décor + sujet]
Shot 2 (3-5s): [Impact — première action]
Shot 3 (5-7s): [Échelle — montrer taille/portée]
Shot 4 (7-9s): [Contexte — wide aerial]
Shot 5 (9-12s): [Menace — focus sujet]
Shot 6 (12-15s): [Climax — résolution spectaculaire]
```

Source: @Naiknelofar788, x.com/Naiknelofar788/status/2080991436426899500

---

## Pattern C: LLM storybreaker → Seedance executor (pipeline)

Pattern d'**architecture** (pas prompting): un LLM décompose le récit en beats automatiquement avant que Seedance n'exécute.

### Workflow

```
Script/récit → LLM (Claude) produit beats narratifs → Seedance exécute chaque beat
```

L'LLM devient **storybreaker** (directeur de board), pas juste prompteur. Il structure le récit en beats chronologiques (ex: chase → climb → kill, ou hook → education → CTA) avec un angle caméra par beat.

### Différence vs A/B

| Aspect | Patterns A/B | Pattern C |
|--------|-------------|-----------|
| **Qui définit les cuts** | L'utilisateur, manuellement | L'LLM, automatiquement |
| **Niveau** | Prompting | Architecture/pipeline |
| **Automation** | Non | Oui (script → beats → vidéo) |
| **Cohérence narrative** | Dépend de l'utilisateur | Garantie par l'LLM |

### Avantages
- Supprime la définition manuelle des cuts
- Cohérence narrative structurelle
- Automatisable: script markdown → beats JSON → Seedance API
- Coût: <$5, <10min render pour 15s vidéo

### Genre valide
Anime sakuga (cel shading, frame par frame) également validé par ce pattern. Le LLM structure les beats d'action, Seedance exécute le style visuel.

Source: @andy_neon_, x.com/andy_neon_/status/2081047583846207744

---

## Pattern D: Raw smartphone / faux UGC

Force le modèle à produire du footage amateur authentique — l'inverse du cinematic. Pour générer du contenu qui passe pour réel sur TikTok/Reels.

### Tokens anti-cinematic (clés du pattern)

```
Super casual real smartphone home video footage
Slight authentic handheld shake
Normal frame rate with smooth natural motion
Rapid-fire montage with constant quick jump cuts every 1-2 seconds
Unpolished authentic phone recording
Pure raw home video feel
```

### Negative prompt (anti-polish)

```
No cinematic polish
No professional stabilization
No beauty filters
No artificial effects
No AI artifacts or glitches
No cinematic color grading
```

### Autres éléments

- **Verrouillage identité single-character**: "Use the provided reference photo as the STRICT ONLY visual reference for the main woman. Maintain her exact appearance with zero deviation."
- **Audio prompté au même niveau que visuel**: distant crowd voices, wind, rushing water, city environmental audio
- **Jump cuts rapides 1-2s**: monté comme un souvenir humain, pas une chorégraphie

Source: @Diplomeme, x.com/Diplomeme/status/2080862907764720120

---

## Pattern E: Travel vlog / documentary réaliste

Ultra-réaliste live-action avec ancrage équipement caméra réel. Technique clé: verrouillage vestimentaire par inventaire.

### Verrouillage vestimentaire par inventaire

Décrire chaque pièce vestimentaire avec **nom + couleur + type + détail technique**:

```
Wearing the EXACT SAME professional paragliding outfit throughout:
- matte white certified paragliding helmet
- navy blue lightweight windproof paragliding jacket with subtle reflective details
- black moisture-wicking performance base layer
- black certified tandem paragliding harness with properly secured leg straps and chest buckle
- black stretch outdoor pants
- gray high-ankle hiking boots with strong ankle support
- lightweight black paragliding gloves
- sport sunglasses tucked into the jacket collar
```

"black stretch outdoor pants" > "black pants". La précision force la consistance.

Complète le Pattern A (verrouillage facial/corporel) avec une couche vestimentaire — utile quand un personnage revient à travers plusieurs clips sans changer de tenue.

### Autres éléments

- **Ancrage équipement caméra réel**: "ARRI Alexa 35, ARRI Signature Prime lenses, subtle film grain" — nommer du matériel réel force la qualité cinématographique
- **Mix caméra**: "Natural handheld vlog camera mixed with cinematic tracking shots" — combine Pattern D (UGC) et Pattern B (cinematic) dans une seule vidéo
- **Montage bullet points séquentiels**: actions concrètes (pas cuts timed)

Source: @Goodmanprotocol, x.com/Goodmanprotocol/status/2081028788771815678

---

## Pattern F: Dark cinematic epic / continuité spatiale narrative

Le pattern le plus avancé de la bibliothèque. Synthétise tous les autres (identity lock A + epic escalation B + equipment lock E) et y ajoute **la continuité spatiale narrative** — un problème qu'aucun autre pattern n'abordait.

### Nouveautés techniques uniques

| Technique | Détail |
|-----------|--------|
| **180-degree rule explicite** | "motivated by established 180-degree axis", "no random camera-axis crossings" — règle cinématographique professionnelle nommée dans le prompt |
| **Object permanence** | "strict object permanence, continuous lighting, seamless spatial continuity" — verrouille la géographie physique de la scène |
| **Mirror/narrative device** | Ex: le bouclier miroir de Perseus (regarder Medusa UNIQUEMENT par réflexion). Un constraint narratif qui force une composition créative |
| **Post-action micro-détail** | "petrification creeps like gray stone across edge of gauntlet, stops before reaching skin" — micro-détail dans le dernier shot |
| **Render specs** | "24fps, 2.39:1 anamorphic, 4K, 180-degree shutter motion blur, anamorphic breathing, cinematic intraframe compression" |

### Structure 5 acts

```
Act 1 (enter) → Act 2 (spot) → Act 3 (combat) → Act 4 (kill/resolution) → Act 5 (aftermath)
```

Chaque acte est un shot motivé narrativement (pas juste esthétique). L'enchaînement suit une logique dramatique, pas un montage visuel.

### Combinatoire

Ce pattern **inclut** les techniques de:
- **Pattern A** — identity lock pour les 2 adversaires (description exhaustive + "preserve across every cut" + "remain continuous")
- **Pattern B** — escalation et ancrage spatial
- **Pattern E** — verrouillage vestimentaire ET d'équipement ("short bronze sword right hand, polished circular bronze shield mirror-like inner surface left arm")

Le pattern F est donc le **plus complet** — utiliser lui seul plutôt que de combiner A+B+E manuellement quand le scénario est un affrontement narratif.

Source: @GumVue, x.com/GumView/status/2080774924054991075

---

## Pattern G: Commercial / brand content premium

Publicité brand content haut de gamme. Le produit est le sujet #1. Régistre "vibe marketing": une idée → commercial premium en minutes.

### Techniques clés

| Technique | Détail |
|-----------|--------|
| **Product hero shots** | Extreme close-up du produit avec matériaux détaillés: "faceted crystal", "diamond-cut glass", "golden amber liquid" |
| **Brand consistency** | Le nom de marque répété et ancré visuellement ("engraved in elegant gold serif font", "massive golden LED billboard") |
| **Multi-environment seamless** | Studio → rooftop → cityscape → store display. Le produit + modèle voyagent à travers 6 décors sans rupture |
| **Color palette as brand identity** | "Gold and black color palette" partout — la palette devient l'identité de marque |
| **Text-on-screen** | Demande du texte généré ("AURUM" sur le flacon, sur le billboard) |

### ⚠️ Caveat: texte à l'écran

Le texte à l'écran reste le **point faible** des modèles vidéo IA. Seedance 2.0 peut mal rendre le texte. Pour une prod client finale:
1. Générer la vidéo SANS texte (ou accepter le risque)
2. Ajouter le texte en post-production (PIL overlay ou ffmpeg drawtext)

### Application Culture en Saveur / Cortex Leman

- **Promo événement** — commercial "vibe" pour les ateliers (testé jul 2026, voir `scripts/test_seedance_promo.py`)
- **Clients Cortex Leman** — remplacerait un tournage à plusieurs milliers de CHF pour PME locales
- **Cas d'usage types**: horlogerie, gastronomie, tourisme FR-CH

Source: @noorlewisx, x.com/noorlewisx/status/2080880873579417849

---

### Addendum pratique: Ancrage géographique réel (CRITIQUE)

Les prompts commerciaux pour un événement physique réel (kiosk, stand, restaurant) doivent **ancrer le décor dans le lieu réel** — pas laisser le modèle défault vers un décor générique.

**Piège validé (juil 2026):** Un prompt "African street food kiosk" génère une rue africaine, même si l'événement est à Petit-Lancy, Genève. Correction utilisateur: décor suisse attendu.

**3 éléments obligatoires dans le prompt:**
1. Nom du lieu réel: "in Petit-Lancy, Geneva, Switzerland"
2. Marqueurs visuels locaux: "Swiss-style residential buildings", "clean paved plaza", "Swiss traffic signs"
3. Negative prompt anti-générique: "no African slum setting, no tropical background"

**Applicable à tous les patterns** (pas seulement G) dès que le clip montre un décor extérieur reconnaissable. Voir `references/ffmpeg-zoompan-subtitles.md` §3 pour le template complet.

---

## Pattern H (IMAGE): Mixed-media editorial collage

**⚠️ Registre IMAGE, pas vidéo** — pour Gemini / Grok / GPT Image 2.0, pas Seedance.

### Technique

Sujet réaliste (top) → dissolution en collage abstrait (bottom) via double-exposure + watercolor + paper-cut + grunge overlays.

| Élément | Exemple |
|---------|---------|
| **Art direction** | Liste explicite des mediums: "double exposure photography, watercolor textures, acrylic brush strokes, paper-cut collage, architectural line drawings, grunge overlays" |
| **Palette** | Hex codes précis — Burnt Orange (#D77A2B / #D88A22), Warm Amber, Soft Ivory, Charcoal Black |
| **Composition** | 4:5, negative space abondant, "minimalist gallery background" |
| **Quality tokens** | "Behance featured, ArtStation quality, museum-quality, 8K" |
| **Negative** | "No text, no watermark, no logo, no border" |

### Usage

Posters, flyers, logos, cover images, thumbnails. Séparé de la bibliothèque Seedance (image vs vidéo).

Source: @ElsaSofia__AI, x.com/ElsaSofia__AI/status/2080972756305461680

---

## Pattern I (IMAGE): Papercraft travel poster (Seedream 5.0)

**⚠️ Registre IMAGE, pas vidéo** — pour Seedream 5.0 / Gemini / Grok. Comme le Pattern H mais opposé esthétique: chaleureux, whimsical, nostalgique vs dark/éditorial/abstrait.

### Technique

Template réutilisable — `{DESTINATION}` est une variable, le reste du prompt est figé → génère une série cohérente en changeant juste la destination.

| Élément | Token |
|---------|-------|
| **Medium** | "3D paper quilling and layered papercraft" + "rolled paper coils" + "embossed paper textures" + "precision paper cutouts" + "layered cardstock" |
| **Composition** | "storybook-like composition with a sense of depth and perspective" + "vertical poster" |
| **Éléments locaux** | "flowers, trees, waterways, mountains, traditional transportation, wildlife, cultural motifs unique to the destination" |
| **Lumière** | "warm golden-hour lighting, soft pastel skies" |
| **Typo intégrée** | "destination name in large bold vintage travel-poster typography at the top" |
| **Quality tokens** | "premium craftsmanship, whimsical, colorful, nostalgic, editorial-quality travel art, ultra-high resolution" |

### ⚠️ Guardrail: cohérence visuelle avec l'existant

Ce pattern est un style **illustratif**. Ne JAMAIS l'appliquer aveuglément sur un projet existant sans d'abord:

1. **Auditer l'identité visuelle en place** — logo, photos réelles, feed FB/IG existant, palette établie
2. **Vérifier la compatibilité** — un style illustratif/whimsical RUPTURE avec un feed photo-réaliste authentique
3. **Définir le périmètre d'usage** — feed = rester en photo-réaliste; supports hors-feed (flyers, posters, cartes, couvertures album) = illustratif acceptable
4. **Adapter la palette** — remplacer les couleurs du prompt original par la charte du projet (ex: pas de "pastel skies" si la charte est terracotta/cacao/crème)

**Exemple concret (Culture en Saveur, juil 2026):** L'utilisateur a corrigé après que l'agent ait recommandé le pattern papercraft pour le feed — "faut garder le visuel qui a été fait auparavant comme sur leur page Facebook". Le feed existant est photo amateur authentique (enfants en activité, lumière naturelle, tons chauds). Le papercraft a été reclassé: supports impression uniquement, pas feed.

Source: @Naiknelofar788, x.com/Naiknelofar788/status/2081306869503799549

### ✅ VALIDÉ (juil 2026 — Culture en Saveur)

Testé avec Seedream 5.0 Pro via kie.ai sur 3 pays + triptyque programme complet:

| Image | Format | Crédits | Temps gen | Résultat |
|-------|--------|---------|-----------|----------|
| Égypte (pyramides + koshari) | 3:4 | 28 | ~150s | ✅ Palette crème dominante conforme |
| Cameroun (Mt Cameroon + ndolé + Ndop) | 3:4 | 28 | ~290s | ✅ |
| Somalie (Laas Geel + dhow + canjeero) | 3:4 | 28 | ~160s | ✅ |
| Triptyque 3-pays + titre + dates | 16:9 | ~28 | 300s+ (timeout wrapper) | ⚠️ Nécessite script standalone avec timeout=600s |

**Leçons techniques de la génération:**
- `4:5` = REJETÉ par l'API (pas dans les ratios supportés). Utiliser `3:4`.
- `negative_prompt` = NON supporté par `gen_image()`. Fold dans le prompt principal.
- Format 16:9 complexe (triptyque multi-sujet) = génère en 300s+, le `_poll_task()` du wrapper timeout à 300s hardcoded. Bypass avec script raw API `timeout=600`.
- `ThreadPoolExecutor(max_workers=2)` fonctionne pour génération parallèle.
- camelCase trap: raw API retourne `data["taskId"]`, le wrapper KieClient normalise en interne.

Voir `references/seedream_image_generation.md` (dans `kieai-seedance-video-generation` skill) pour les détails API complets et les prompts templates.

---

## Accès Seedance 2.0

### kie.ai (défaut)
- Proxy tiers, accès API/scripting
- ~$0.08-0.10/sec
- Résolution 1080p

### Dreamina (alternative)
- Plateforme officielle ByteDance (dreamina.ai)
- **4K UHD natif** (3840×2160) depuis jun 2026
- Cible: "professional post-production and brand visuals"
- Régions: Southeast Asia, Middle East, Africa, Europe, South America
- Accès web uniquement (pas d'API scripting)
- kie.ai reste l'option pour usage programmatique. Dreamina pour livrables premium nécessitant résolution supérieure.

Source: @dreamina_ai (annonce 214K vues, jun 2026), test @JSFILMZ0412

---

## Application aux projets Tars

> **Règle**: les mappings ci-dessous ne sont notés que pour les patterns explicitement discutés dans le contexte d'un projet pendant la session. Les patterns project-agnostic restent project-agnostic.

### Culture en Saveur (Pattern A — discuté)
- **T2 visio orphelinat** — 2 groupes d'enfants (Genève + Cameroun) → risque de fusion
- **Scènes atelier multi-enfants** — enfants qui cuisinent ensemble
- **Si présentateur/mascotte récurrent** → référence image systématique

### african-heroes (Patterns A + B + F — discutés)
- **Batailles** (Mansa Musa, reine Nzinga, Shaka Zulu) → Pattern B pour le spectacle
- **Scènes à plusieurs personnages** (rencontres, dialogues, échanges) → Pattern A pour l'identité
- **Affrontements narratifs** (Nzinga face aux Portugais, bataille d'Adoua, Chaka Zulu) → Pattern F pour la continuité spatiale + 180° rule + dispositif narratif
- **Mythes/légendes** → Pattern B avec ancrage spatial adapté
- Enjeu spécifique african-heroes: fidélité historique — un visage qui mute = faute de rigueur, pas juste défaut esthétique

### Culture en Saveur (Patterns A + G — discutés)
- **T2 visio orphelinat** — 2 groupes d'enfants (Genève + Cameroun) → Pattern A anti-fusion
- **Scènes atelier multi-enfants** — enfants qui cuisinent ensemble → Pattern A
- **Promo événement** (commercial vibe) → Pattern G testé jul 2026 (script `test_seedance_promo.py`)
- **Si présentateur/mascotte récurrent** → référence image systématique

### Culture en Saveur — Standard "Programme V0" (juil 2026, VALIDÉ)
La vidéo `programme_v0.mp4` (54s) est devenue le **standard de qualité de référence** pour tout le lot Culture en Saveur. Ses clips ont été jugés largement supérieurs ("n'a rien à voir") aux clips des autres vidéos (T1, T2, T3).

**Recette du prompt "Programme V0" (appliquer à tous les nouveaux clips):**
- Environnement détaillé et nommé: "in a bright classroom at Maison de Quartier le Plateau, Petit-Lancy, Geneva" (pas juste "classroom")
- Éclairage naturel spécifié: "warm natural morning light through large windows, soft shadows"
- Animatrice visible et active: "a certified female instructor in apron guiding children" (pas juste enfants seuls)
- Triple Identity Lock Pattern A appliqué même pour 1-2 personnages
- Negative prompts stricts: "no face swaps, no duplicates, no AI artifacts, no cartoon style"

**Upgrade qualité batch:** pour remonter un lot existant à ce standard, voir `references/batch-quality-upgrade.md`. Le workflow préserve le contenu narratif (VO, structure, CTA) et ne remplace que les clips vidéo sources.
