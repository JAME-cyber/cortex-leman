# Benchmark concurrentiel : Yassine Sdiri (256k abonnés)

Analyse de production vidéo long-form IA/tech FR. Source: "Deepseek a résolu le plus gros problème de l'IA" (16:50, 3617 mots, ~215 mots/min).

Méthodologie: vidéo téléchargée (yt-dlp -f18), 10 frames extraites (ffmpeg), PIL ImageStat (luminance/contraste/color-variance), transcript complet (youtube-transcript-api .fetch()), contact sheet livré à l'utilisateur.

## Structure narrative observée (8 blocs)

| Bloc | Timing | Fonction |
|------|--------|----------|
| Hook | 0:00–0:30 | Chiffre choc ("600M$ en fumée en 1 jour") + promesse |
| Présentation | 0:30–2:00 | Contexte, démo interface |
| Suspens/tease | 1:30–2:00 | "ça sent le piège... je vous le montre à la fin" |
| Substance tech | 2:00–6:00 | Comment ils ont fait (vulgarisation) |
| Nuance | 6:00–8:00 | "pas eux qui ont inventé" → crédibilité |
| Analyse business | 8:00–10:00 | Stratégie challenger, casser les prix |
| Bénéfice viewer | 10:00–14:00 | "factures token /10", self-hosting, 1M tokens |
| Résolution tease + CTA | 14:00–16:50 | "données partent en Chine" + école IA sponsor |

## Patterns empruntables pour LEC

### 1. Hook chiffré + conséquence
Yassine ouvre avec un chiffre concret + son impact boursier. Applicable aux Shorts bull: "+340% en 48h", "X milliards de capex annoncé".

### 2. Mécanisme de tease (rétention 12+ min)
Plante une question à l'intro ("ça sent le piège"), résout à la toute fin. NOTRE pipeline n'a pas ce mécanisme — la structure actuelle est linéaire (intro→arguments→verdict). Pour le podcast bear: teaser un "élément qu'on vous cache" au cold open, le révéler dans le verdict.

### 3. Alternance visuelle talking head / screen capture
Ses frames basculent entre studio sombre (lum 30–50/255) et écrans clairs (lum 160+/255). Ce contraste maintient l'attention. Notre pipeline: slide statique unique = moins de variation visuelle. Piste: alterner entre slide sombre (sections bear) et captures d'écran claires (data points, graphiques).

### 4. Bénéfice viewer explicite
"Vos factures de token divisées par 10" (15:45). Toujours reformuler l'analyse en "ce que ça change pour VOUS". Notre pipeline reste théorique — le verdict pourrait être plus actionnable.

## Ce qu'on garde (avantages différenciants LEC)

- **Dual bull/bear** — Yassine fait du pure bull (DeepSeek = solution). Notre format LE CONTRE-POINT (bear case) est différenciant sur YT FR finance.
- **Conformité AMF L541-1** — Yassine ne mentionne aucun disclaimer. Notre guardrail conformité est un avantage crédibilité long terme.
- **Pipeline automatisé ~3min** — Yassine écrit + enregistre + monte manuellement (studio, caméra, montage). Notre skill produit en ~3min sans intervention humaine.
- **Critères falsifiables** — Notre bear case inclut des conditions mesurables datées. Yassine n'a pas d'équivalent.

## Ce qui nous manque vs Yassine

- **Face caméra / personnalité** — il a un studio + présence humaine. Nous: full TTS + slide.
- **Screen capture de démo** — il montre l'interface produit. Nous: que du b-roll financier.
- **Storytelling tease** — structure plus sophistiquée que notre intro→arguments→verdict linéaire.
