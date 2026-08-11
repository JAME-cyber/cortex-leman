# Benchmark concurrentiel : Tech In Check French (chaîne IA full-auto)

Analyse de production vidéo long-form tech FR. Source: "La Chine A Secrètement Créé Un Transistor Sans Silicium — Même Intel Et TSMC Le Jugent Impossible" (25:35, 3690 mots, label YouTube "IA").

Méthodologie: vidéo téléchargée (yt-dlp -f18 android), 13 frames extraites (ffmpeg), PIL ImageStat (luminance/contraste/color-variance), transcript complet (youtube-transcript-api .fetch()), contact sheet livré.

## Profil : le concurrent le plus proche de notre pipeline

Tech In Check French est **full AI** (aucun humain, TTS synthétique, label "IA" disclosed par YouTube). C'est le canal analysé qui ressemble le plus à notre setup — et il montre les limites du format.

| Critère | Tech In Check | Notre pipeline |
|---------|--------------|----------------|
| Présentation | Aucun humain | Aucun humain (TTS + slide) |
| Voix | TTS IA synthétique | edge-tts HenriNeural |
| Label YouTube | "IA" (disclosed) | — (pour l'instant) |
| Engagement | 10 likes / 25 min | — |
| BGM | Permanent (61 tags [musique]) | Permanent (-28dB) |
| Profondeur technique | Très élevée | Moyenne |
| Alternance visuelle | Oui (lum 38–163, contraste 35–69) | Non (slide unique statique) |

## Structure narrative observée (6 blocs)

| Bloc | Timing | Fonction |
|------|--------|----------|
| Hook | 0:00–0:35 | Chiffre (40%) + échelle historique (10 milliards de milliards depuis 1959) |
| Tease + CTA précoce | 0:55–1:10 | "vous comprendrez pourquoi... à la fin" + "Likez et abonnez-vous vite" |
| Contexte | 1:10–4:00 | Pourquoi le silicium a gagné (nuance/crédibilité) |
| Substance | 4:00–20:00 | 16 min de physique (MoS₂, GAA, DFT, interface grille) |
| Synthèse | 20:00–24:30 | Résolution du tease |
| CTA final + question ouverte | 24:30–25:34 | "Donnez votre avis en commentaire" sur débat technique |

## Patterns identifiés

### 1. Hook chiffré DOUBLE (chiffre + échelle de référence)
Pas juste un chiffre, mais un chiffre + une échelle qui donne la mesure. "40% plus vite" (chiffre) + "10 milliards de milliards fabriqués depuis 1959" (échelle). Plus puissant qu'un chiffre seul. **À intégrer** dans notre cold_open.

### 2. Tease → résolution
Identique à Yassine Sdiri. Confirme que c'est un standard du format long-form tech FR. Déjà intégré dans notre patch (juil. 2026).

### 3. CTA multiples (5x au lieu d'1)
CTA à 1:02, 19:06, 25:08/11/34. Bombardement. Yassine : 1 seule à la fin. Nous : 0.
**Évaluation**: à utiliser avec parcimonie pour le contenu financier (risque crédibilité AMF). Maximum 2x : 1 discrète au milieu, 1 finale.

### 4. Question ouverte finale (engagement commentaires)
"Dites-moi en commentaire... la vraie barrière c'est le délai ou l'économie ?" Question technique binaire qui force l'engagement. Signal algo YT important (commentaires = boost). **À intégrer** dans notre verdict.

### 5. Alternance visuelle (LE point faible de notre pipeline)
Frames à luminosité variable (38–163/255), contraste élevé (35–69). Variation visuelle continue malgré l'absence d'humain. Notre slide unique statique = pas de variation. **Intégration implémentée** : multi-slide par section avec codes couleur contrastés + texte-clé.

### 6. Pacing robotique (À ÉVITER)
270–310 mots par bloc de 2 min, variance minime. Monotone. Probable facteur des 10 likes. Notre monologue posé avec variations de rythme est un avantage différenciant.

## Leçon clé : le risque du label "IA"
Tech In Check a 10 likes pour 25 min de contenu de qualité technique. Le label "IA" de YouTube pénalise probablement la distribution. Notre pipeline doit éviter ce label aussi longtemps que possible : voix HenriNeural (neutre), contenu original (pas de réécriture d'articles), conformité AMF (crédibilité humaine/professionnelle).
