# Seedance 2.5 sur kie.ai — Workflow Production

**Confirmé live**: 11 août 2026 — https://kie.ai/seedance-2-5
**Modèle**: `bytedance/seedance-2-5`

## Pricing (août 2026)

| Résolution | Text-to-Video | Image-to-Video |
|---|---|---|
| 720p | $0.315/s (63cr/s) | $0.190/s (38cr/s) |
| 480p | $0.140/s (28cr/s) | $0.085/s (17cr/s) |

High-tier top-up = +10% bonus credits = ~10% cheaper.
Échecs = $0 (kie.ai ne facture pas les tâches ratées).

**Note pricing "with video"**: I2V est moins cher car facturé sur (Input+Output) vs T2V sur Output seul.

## Capacités 2.5 vs 2.0

| Feature | 2.0 | 2.5 |
|---|---|---|
| Durée max | 15s | **30s** |
| Résolution | 1080p | **480p / 720p** (4K natif supporté) |
| Références | 9 images | **50 multimodales** (images+vidéos+audio) |
| Audio natif | Non | **generate_audio=true** |
| First/Last frame | Non | **first_frame_url / last_frame_url** |
| 3D white-model | Non | **Oui** (prévisualisation caméra/scène) |
| Smart edit / marks | Non | **Oui** (édition locale) |

## 3 Techniques Production (nouveau 2.5)

### 1. Character Sheet References

Générer 3 images de référence du personnage principal (front, profile, three-quarter) via Seedream 5.0 Pro ou Midjourney AVANT les clips vidéo. Passer ces refs dans `reference_image_urls` sur chaque clip où le personnage apparaît.

**Syntax prompt**: `@Image1 @Image2 show the character. [Description de l'action...]`

**Validé**: 2-3 refs suffisent pour locker un visage à travers 11 clips.

### 2. First/Last Frame Chaining

Connecter des clips visuellement avec `first_frame_url` (frame de début) et `last_frame` (récupérée via `return_last_frame=true`).

**Pattern**:
```
Clip A (return_last_frame=true) → save last frame
Clip B (first_frame_url = last_frame of A) → continuité visuelle
```

**Usage**: Transitions narratives (mines → caravane → ville), passage de temps (coucher → aube). Ne pas en abuser — certains cuts sont mieux secs (ruptures symboliques).

### 3. Native Audio Generation

`generate_audio=true` génère l'audio ambiant synchronisé au visuel (sons de foule, nature, machines).

**Règle**: Activer sur les clips d'ambiance/paysage. Désactiver sur les clips où la VO porte le récit (sinon l'audio IA entre en conflit avec la VO).

## Aspect Ratios Supportés

16:9, 9:16, 1:1, 4:3, 3:4, 21:9, adaptive

## Checklist Génération (kie.ai Playground)

1. Aller sur https://kie.ai/seedance-2-5
2. Settings: Resolution (720p), Aspect ratio (9:16 vertical), Duration (slider 1-30s)
3. Upload character refs dans `reference_image_urls` (si applicable)
4. Pour chaining: uploader `first_frame_url`
5. `generate_audio`: selon le clip (voir règle ci-dessus)
6. Copier-coller le prompt, remplacer `@Image1` etc. par les refs
7. Run → attendre ~2-5min par clip selon durée
8. Sauver `clip_NN.mp4`
9. QA vision obligatoire (or_vision.py) avant intégration

## Modèle de Coût (projet type Sankofa Short)

| Projet | Clips | Durée totale | Coût 720p T2V | Coût 480p T2V |
|---|---|---|---|---|
| Short 11 clips (~90s) | 11 | 94s | ~$29.62 | ~$13.16 |
| Avec high-tier (-10%) | 11 | 94s | ~$26.66 | ~$11.84 |

## Pitfalls

- **2.5 est PLUS CHER que 2.0** ($0.315/s vs $0.05/s en 2.0). Réserver 2.5 pour les projets nécessitant character consistency ou audio natif. 2.0 reste viable pour B-roll et paysages.
- **50 refs = théorique**: En pratique, 2-3 refs de personnage suffisent. Trop de refs peut créer du bruit.
- **480p = draft quality**: Pour production finale, toujours 720p minimum.
- **Duration slider**: kie.ai playground default = 5s. Vérifier avant chaque génération.
- **nsfw_checker**: Activé par défaut dans le playground, ne peut être désactivé. "dark-skinned" dans les prompts peut parfois déclencher des faux positifs → reformuler si bloque.
