# Pipeline Vidéo Pub Hybride (Seedance + HyperFrames + Kokoro)

**Pattern éprouvé sur Darkom-Debarras (juillet 2026).**
Pipeline production d'une pub filmique 30s 9:16 pour service local B2C.
Réutilisable pour tout business local nécessitant une pub premium avec branding net.

## Pourquoi hybride (et pas 100% IA vidéo)

Les modèles de vidéo IA (Seedance, Veo, Kling) restent **imprécis sur le texte** :
noms de marque, numéros de téléphone, prix → caractères déformés/inventés.
Pour une pub dont le but est de **faire appeler un numéro**, c'est rédhibitoire.

→ **Seedance produit les scènes filmiques** (réel, émotion, transformation)
→ **HyperFrames pose les éléments de marque** (wordmark, téléphone, CTA, stats) en overlay net
→ **Kokoro TTS produit la VO** (voix française, gratuite, qualité broadcast)

## Architecture en 3 couches

| Couche | Rôle | Où | Fiabilité |
|--------|------|----|-----------|
| **1. ADN couleur dans les clips** | Reconnaissance subconsciente via couleurs + objets répétés | DANS les prompts Seedance | ✅ IA gère |
| **2. Wordmark permanent** | Logo en coin, tout le long | Overlay HyperFrames | ✅ net |
| **3. Callouts cinétiques** | Lower-thirds synchronisés aux beats clés | Overlay HyperFrames | ✅ net |

**Principe clé :** reconnaissance marque ≠ logo lisible. On ancre la couleur
(et un motif répété) pour que le cerveau retienne la marque. Le logo net arrive en overlay.

## Fichiers de production

| Fichier | Rôle |
|---------|------|
| `DESIGN.md` | Source de vérité brand : couleurs, typo, motion signature, what NOT to do |
| `key-events.md` | Shot list narrative : scènes, durée, on-screen, VO beat |
| `shots.json` | Prompts structurés machine-readable pour l'API IA vidéo |
| `kie_pipeline.py` | Pilote API : submit / poll / download / run |
| `overlay/index.html` | Composition HyperFrames : footage + overlay marque + audio |
| `audio/vo-*.wav` | Un fichier WAV par scène (VO Kokoro) |
| `audio/vo-script.txt` | Script VO structuré par scène |

## Workflow de production (5 étapes)

```
[1] Itération look (cheap)
    shots.json → API IA vidéo (seedance-2-fast ou équivalent)
    → valider palette/lumière sur 1-2 shots avant de tout lancer

[2] Génération finale
    Pipeline complet sur tous les shots (seedance-2 qualité ou équivalent)
    → clips/shot-01.mp4 … shot-05.mp4

    ⚠️ Vérifier le solde crédits AVANT de soumettre un batch.
    Kie.ai n'expose pas d'endpoint balance — la seule façon de savoir
    c'est de regarder le dashboard web. Si insuffisant: code 500 + msg explicite.

[3] (Optionnel) Cohérence renforcée
    figer un first_frame par shot → image-to-video
    → utile seulement si drift cross-shot

[4] Overlay marque — DEUX PISTES
    PISTE A — HyperFrames (riche, GSAP, animé):
      overlay/index.html → wordmark + phone + CTA + callouts synchronisés
      render → pub finale avec overlay
      Requiert serveur HyperFrames actif (npm run dev)

    PISTE B — ffmpeg drawtext (rapide, zéro dépendance):
      build.sh avec drawtext filter chains pour texte + CTA + watermark
      Template réutilisable: templates/ffmpeg-ad-assembly.sh
      Édition: changer couleurs hex, textes, timing dans le script
      Avantage: pas de serveur, pas de npm, 2 min de render

    PISTE HYBRIDE (éprouvée V2 Darkom): générer nouveaux clips IA +
    réutiliser clips existants d'autres projets + ffmpeg drawtext overlay.
    Permet de produire une 2ème pub même avec crédits limités.

[5] Audio
    VO Kokoro par scène + musique avec ducking automatique sous la VO
    ⚠️ Kokoro TTS uniquement sur python3.12. Batch de 6+ clips peut hang.
```

## DESIGN.md — Format de référence

Document dérivé du brand existant (CSS theme, marketing copy). Contient :

- **Style Prompt** : description sémantique du positionnement
- **Colors** : tokens avec hex, rôle, et règles de polarité (texte sur fond)
- **Typography** : font family, weights, tailles, tabular-nums pour stats
- **Motion signature** : type d'entrées (power3.out/expo.out), transitions
- **Key messages** : tagline, preuves, zone, feature phare
- **What NOT to do** : couleurs interdites, AI tells à éviter, polarité

⚠️ **Polarité inversée obligatoire** : sur fonds sombres, texte clair JAMAICS texte sombre.
Contraste insuffisant = invisible. Le vérifier dans DESIGN.md avant de composer.

## Contraintes techniques

| Paramètre | Valeur type | Note |
|-----------|-------------|------|
| Durée finale | ~30s | assemblage de 5-6 shots |
| Ratio | **9:16 vertical** (priorité Reels/TikTok/Shorts) | générer aussi 16:9 si besoin |
| Résolution | 720p génération → 1080p render | 4K inutile pour mobile |
| VO | Kokoro `ff_siwis` (FR) ou Edge TTS `fr-CH-*` | une fichier WAV par scène |
| Musique | ducking automatique sous VO (volume 0.28 → 0.12) | fade-out final 1.8s |
| Flash transitions | overlay couleur accent à chaque cut | cache les coupes, signature |

## VO Kokoro — Script structuré

Format : un fichier WAV par scène, VO démarre +0.3s après l'apparition de la scène.

```
[SCENE 1 - Hook, 0-3s] Que faire de tout ça ?
[SCENE 2 - Solution, 3-7s] Débarras. On vide, vous respirez.
[SCENE 3 - Services, 7-12s] Maison, cave, succession. On s'occupe de tout.
[SCENE 4 - Proof, 12-16s] Rapide. Devis gratuit. Et cent pour cent écoresponsable.
[SCENE 5 - Differentiateur, 16-19s] Un artisan local. Sérieux, discret, fiable.
[SCENE 6 - CTA, 19-22s] Devis gratuit en trente secondes.
```

## Budget crédits (estimé Seedance via kie.ai)

- 1 clip seedance-2-fast = ~165 crédits
- Itération look (2 shots test) ≈ 330 crédits
- 5 shots finals × 1 passe ≈ 825 crédits
- Rerolls réalistes (×2-3 par shot) ≈ **2 500-4 000 crédits** au total

⚠️ Vérifier le solde kie.ai avant de lancer la vague finale.

## Distribution post-production (funnel)

La vidéo seule ne suffit pas. Pipeline de distribution recommandé :

```
Pub 30s (vertical 9:16)
    ↓
Meta Ads (Facebook/Instagram) — cible démographique fine
    ↓
Commentaire-clé ("DEVIS") sur la pub
    ↓
Auto-réponse → DM avec lien lead magnet
    ↓
Lead magnet (Google Doc : checklist, guide) contre email + tél
    ↓
Follow-up phone → devis → signature
```

**3 métriques qui comptent** (pas de vanity) :
1. Leads/devis par campagne
2. Taux conversion devis → signé
3. Coût d'acquisition par client

## Différences avec MoneyPrinterTurbo

| Aspect | MoneyPrinterTurbo | Pipeline Hybride |
|--------|-------------------|------------------|
| Source footage | Stock Pexels/Pixabay | Clips IA générés (Seedance) |
| Branding | Aucun (watermark à ajouter) | 3 couches (couleur + wordmark + callouts) |
| Typo/CTA | MoviePy text basique | HyperFrames overlay net, animé |
| VO | Edge TTS (correct) | Kokoro (broadcast quality) ou Edge TTS |
| Contrôle design | Minimal | Total (DESIGN.md + HyperFrames) |
| Cas d'usage | Vidéo générique, contenu social | Pub service local premium, brandée |
| Coût | Gratuit (Pexels + Edge TTS) | Crédits IA vidéo (2500-4000) |

→ MoneyPrinterTurbo pour du contenu rapide et gratuit.
→ Pipeline hybride pour une pub payante qui doit convertir.

## Référence projet

- **Démo live V1 :** `/home/tars/darkom-launch-video/` (Darkom-Debarras, 16:9, HyperFrames overlay)
- **Démo live V2 :** `/home/tars/darkom-launch-video-v2/` (Darkom-Debarras, 9:16 vertical, ffmpeg overlay)
- **Vidéo finale V2 :** `darkom-launch-video-v2/renders/darkom-pub-v2.mp4` (720×1280, 30s, 9MB)
- **DESIGN.md template :** `/home/tars/darkom-launch-video/DESIGN.md`
- **ffmpeg build script :** `/home/tars/darkom-launch-video-v2/build.sh`
- **Kie.ai API quirks :** `references/kie-api-quirks.md` (dans ce skill)
- **ffmpeg ad template :** `templates/ffmpeg-ad-assembly.sh` (dans ce skill)
