# Zankofa / Culture en Saveur — Build Details

## Contexte projet
- **Nom interne**: Zankofa ("Le Grand Livre des Saveurs")
- **Client**: Culture en Saveur (Linda, +41 76 756 22 82)
- **Activité**: ateliers cuisine enfants 4-12 ans, 10-14 août 2026, Petit-Lancy
- **Prix**: 85 CHF/jour
- **Décor**: Maison de Quartier OBLIGATOIRE (authenticité du lieu)
- **Musique**: afroswing_v2

## Séries Shorts

| Série | Thème | Clip Seedance | VO | Statut |
|---|---|---|---|---|
| T1 | Cuisine 3 pays (Égypte/Cameroun/Somalie) | 3 clips (koshari, ndolé, canjeero) | DeniseNeural | ✅ Validé utilisateur |
| T2 | Visio orphelinat Cameroun | 1/3 clips (visio_orphelinat.mp4) | DeniseNeural | ⏳ VO corrigée, 2 clips à générer |
| T3 | Nil / patrimoine égyptien | 1/3 clips (le_nil.mp4) | DeniseNeural | ⏳ VO corrigée, 2 clips à générer |

## Structure T1 (36.2s, template validé)

| Segment | Durée | Visuel | VO |
|---|---|---|---|
| Intro | 3.0s | Logo Steam & Spice | stinger |
| Title card | 4.5s | "3 SAVEURS 1 VOYAGE" + drapeaux + photo Maison Quartier | "Cet été, vos enfants vont voyager par la cuisine" |
| Égypte | 6.7s | Clip Seedance koshari | "En Égypte, le koshari..." |
| Cameroun | 6.2s | Clip Seedance ndolé | "Au Cameroun, le ndolé..." |
| Somalie | 5.6s | Clip Seedance canjeero | "En Somalie, le canjeero..." |
| CTA | 10.2s | Frame CTA (tarifs, contact) | "Trois pays, inscrivez-vous..." |

## Pipeline Seedance (Kie.ai)

### Workflow
1. **Upload images** via API `file-stream-upload` sur `kieai.redpandaai.co`
2. **Récupérer URLs** hébergées
3. **Lancer tâche** Seedance avec `first_frame_url`
4. **Polling** jusqu'à completion
5. **Télécharger** MP4 (720×1280, 24fps, 5s)

### Coûts
- 165 crédits par clip Seedance
- 5 clips = 825 crédits
- Solde après batch: ~8 crédits (limite basse)

### Script de génération
`scripts/gen_seedance_videos.py` — pipeline complet upload + generate + download.

## Drapeaux officiels

Source: `flagcdn.com/w640/{code}.png`
- `eg.png` — Égypte (avec Aigle de Saladin doré)
- `cm.png` — Cameroun (vert/rouge/jaune + étoile)
- `so.png` — Somalie (bleu + étoile blanche)

Cache local: `assets/flags/`

## Photo Maison de Quartier

Source: `guenin-architectes.ch/projet-104-maisondequartierdelancy.html`
- Photos: `2011images/rpc/104/14-25-maison_de_quartier_de_lancy.jpg`
- Meilleure: mq_16 (798×333, 233 KB)
- Cache: `assets/maison_quartier/`

## Layout title card (1080×1920)

```
Y=550:  "3 SAVEURS" (80px gold)
Y=640:  "1 VOYAGE" (80px gold)
Y=730:  ───────────── (orange line)
Y=800:  "Éveil aux Saveurs Africaines" (48px white)
Y=950:  [🇪🇬 180×120]  [🇨🇲 180×120]  [🇸🇴 180×120]  (spacing 120px)
Y=1110: ÉGYPTE  CAMEROUN  SOMALIE (36px orange)
Y=1400: "Culture en Saveur" (36px grey)
Y=1460: "10-14 août 2026" (36px grey)
Y=1520: "Maison de Quartier · Petit-Lancy" (36px grey)
```

Fond: photo Maison Quartier assombrie à 55% (blend 0.55 avec overlay #1a0a00).

## Scripts

| Script | Usage |
|---|---|
| `scripts/gen_seedance_videos.py` | Upload images + génération Seedance + download |
| `scripts/build_t1_v3.py` | Assemblage T1 (intro + title + 3 clips + CTA + VO + subs) |
| `scripts/build_t2_visio.py` | Assemblage T2 (visio orphelinat) — prêt, non lancé |
| `scripts/build_t3_nil.py` | Assemblage T3 (Nil/écosystème) — prêt, non lancé |

## Leçons spécifiques Zankofa

1. **L'utilisateur a d'abord vu "Somalie manquante"** → c'était un problème de sync VO, pas de clip manquant. Le clip Somalie était là mais sa VO jouait sur le clip Égypte. Diagnostic: vérifier l'alignement VO↔clip par segment.

2. **L'utilisateur voulait un clip de transition** → entre l'intro et le premier pays, pour que la VO d'intro ne chevauche pas le clip Égypte. Solution: title card dédié de 4.5s.

3. **Les overlays drapeaux sur les clips ont été rejetés** → "en fait de compte tu peux enlever le drapeau sur chaque clip". Garder les drapeaux uniquement sur le title card.

4. **Le drapeau Égyptien dessiné en PIL était rejeté** → "non c pas bon il faut que tu fasse mieux que ça". L'Aigle de Saladin doit être net et détaillé. Solution: flagcdn.com officiels.

5. **L'utilisateur a demandé la Maison de Quartier en fond** → pas sur un clip spécifique, mais sur le title card. Rechercher la photo en ligne (site des architectes).

6. **55% d'assombrissement = trop sombre** → "on voit pas très bien la maison de quartier". Réduit à 30%, bâtiment visible et texte toujours lisible.

7. **L'utilisateur a demandé d'arrêter les builds T2/T3** → "non arrête le build si tu n'a pas lancé". Toujours garder le session_id pour kill immédiat. Ne pas relancer sans instruction explicite.

8. **Title card T2/T3** → accent couleurs différentes par série: T1=#FFD700 (or), T2=#4FC3F7 (bleu), T3=#66BB6A (vert). Même layout, même fond photo Maison Quartier.

9. **VO T2/T3 générés en série** → `edge-tts --write-media` commandes enchaînées (pas en parallèle background, terminal foreground séquentiel). 5 fichiers × 2 séries = 10 VO en ~30s.

10. **VO T2/T3 v1 INVENTÉE — rejet utilisateur** → Les VO originales T2 et T3 étaient inventées au lieu d'être basées sur le brief. Exemples d'erreurs: T3 décrivait "animaux, plantes, écosystèmes" (inventé) au lieu de "pyramides, hiéroglyphes, Nil" (agenda réel). T2 disait "en classe" au lieu de "Lundi 11h30" et omettait le nom de l'orphelinat "Joie de Vivre". T3 omettait la sortie au Rhône. **Lesson: relire le brief intégral avant d'écrire la moindre ligne de VO.** VO corrigées dans `assets/vo_t2_v2/` et `assets/vo_t3_v2/`.

11. **Clip looping = gaspillage de crédits** → Les builds T2/T3 v1 loopaient le même clip 3x pour remplir 3 segments. L'utilisateur a immédiatement remarqué ("pourquoi nous avons un seul clip à la fois") et a dit "on a gaspillé des crédits pour rien". Solution: guardrail `scripts/validate_clips.py` qui bloque les builds si clips insuffisants. **Lesson: ne jamais lancer un build sans avoir un clip unique par segment.**

12. **Prompts Seedance prêts** → 3 prompts T2 et 3 prompts T3 dans `scripts/T2_visio_script_CORRIGE.md` et `scripts/T3_nil_script_CORRIGE.md`. Attendre crédits utilisateur pour générer.

13. **T2 uniquement, T3 après** → L'utilisateur veut valider T2 d'abord avant de lancer T3. Ne pas paralléliser la génération de clips entre thèmes.

14. **Guardrail anti-loop maintenant permanent** → `scripts/validate_clips.py` dans le skill `shorts-video-assembly/scripts/`. Exécuter avant chaque build.
