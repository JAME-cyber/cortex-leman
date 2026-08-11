# Techniques de Prompting Avancées (Seedance 2.5 + alternatives)

Compilation de patterns validés sur le terrain (août 2026) pour maximiser la qualité vidéo IA.

---

## 1. Grid Story Prompting (multi-panel narrative)

**Source**: @chrisdadiva (3741 likes, tutoriel 24min, août 2026)

Au lieu de générer clip par clip, **un seul prompt décrit N scènes séquentielles** dans une grille narrative. Le modèle génère une cohérence de personnage/décor à travers tous les panels.

### Template
```
Create a N-story grid story of [PERSONNAGE] [ACTION PRINCIPALE]. 
[SCÈNE 1: lieu + action]. [SCÈNE 2: lieu + action]. 
[SCÈNE 3: lieu + action]. Keep the angles creative.
```

### Exemple validé
```
Create a 9-story grid story of the man in red lying on a hammock hung 
between two dry trees on the desert sand right behind the village house. 
He is lying on the hammock and smoking from his bouffarde. The old man 
with red headgear and the young man are seen in the distance holding axes 
and digging. The man in red turns and looks at them. Keep the angles creative.
```

### Usage
- Chaque panel peut ensuite être animé individuellement via I2V
- Garantit cohérence costume/décor/physionomie sans character sheet séparé
- Idéal pour prévisualiser une séquence narrative complète avant animation

---

## 2. One-Take Filmmaking (single-shot 30s)

**Source**: PJ Ace (@PJaccetturo, "One-Take Filmmaking with Seedance 2.5", août 2026)

Format viral : **30 secondes, un seul plan continu, zéro cut**. Seedance 2.5 permet des single-shot continus en 4K avec audio synchronisé.

### Formulaire prompt (5 couches)
```
Subject + Action + Camera + Lighting + Style (+ Audio)
```
En oublier une = le modèle improvise = drift.

### Règles
- **Max 1-2 moves caméra par clip**. Pan + orbit + crane = muddy. Un move décidé = premium.
- Vocabulaire cinéma compris par le modèle: `dolly-in`, `orbit`, `crane up`, `tracking shot`, `tilt up`, `slow push`
- Pour character consistency: `Image-to-Video` depuis une image de référence plutôt que T2V pur

### Template one-take
```
[SUBJECT description]. [ACTION continue sur 30s]. 
Slow [CAMERA MOVE: dolly-in / orbit / crane up / tracking] 
over [ENVIRONMENT]. [LIGHTING: golden hour / harsh midday / blue hour]. 
[STYLE: cinematic documentary / epic / intimate]. 4K detail, film grain.
```

---

## 3. Character Sheet via Nano Banana 2 (GRATUIT)

**Source**: @chrisdadiva

Au lieu d'utiliser Seedream 5.0 Pro (payant sur kie.ai) pour générer les character sheets de référence, utiliser **Nano Banana 2** (Gemini image generation) — **gratuit**.

### Workflow
1. Prompt Nano Banana 2: `Character sheet of [PERSONNAGE]. [Description physique détaillée]. Three angles: front view, profile, three-quarter. Neutral studio background. Cinematic lighting, ultra-detailed, 4K.`
2. Sauver les 3 angles comme images de référence séparées
3. Passer dans Seedance 2.5 `reference_image_urls` pour chaque clip où le personnage apparaît

**Économie**: Character sheets gratuits au lieu de ~$0.50-1.00 par sheet sur Seedream.

---

## 4. 3D Text + Format Chapitre (rétention)

**Source**: @BannedxMan (943 likes, 403 RT, août 2026)

Format où chaque chapitre = un sujet/pays/personnage, introduit par du **texte 3D imposant**.

### Structure
```
[HOOK question contre-factuelle] 
→ Chapitre 1: 3D TEXT [SUJET] → portrait → scène épique
→ Chapitre 2: 3D TEXT [SUJET] → portrait → scène épique
→ Chapitre 3: 3D TEXT [SUJET] → portrait → scène épique
→ Conclusion
```

### Application Sankofa
"Et si chaque empire africain avait dominé le monde ?"
- MALI → KONGO → ÉTHIOPIE → ZOULOU → KOUCH
- Chaque chapitre: nom d'empire en 3D → portrait héros → scène épique

### Note technique
Le 3D text n'est PAS généré par Seedance. À produire via:
- **Blender** (Euler 3D text + glow)
- **After Effects** (Element 3D)
- **CapCut Pro** (overlays texte animé)
Puis compositer en post-production.

---

## 5. Narrativ Time-Loop (5 beats)

**Source**: @Strength04_X via @itsPolloAI (Pollo.ai, août 2026)

Structure shot-by-shot sur 15s avec 5 beats:

```
SETUP → INCIDENT → FREEZE → REWIND → RESOLUTION
```

### Techniques
- **TIME FREEZE**: objets/liquides suspendus, personnages figés sauf protagoniste
- **LIQUID PHYSICS**: café/œufs en rubans, gouttelettes en slow-mo
- **CAMERA ORBITALE 360°** autour du point d'impact
- **REWIND EFFECT**: monde qui s'inverse

### Structure prompt
```
[SETUP global: lieu + style + film grain]
[0-3s] [SHOT TYPE] + action setup
[3-6s] [SHOT TYPE] + incident
[6-9s] [SHOT TYPE] + freeze, orbit
[9-12s] [SHOT TYPE] + rewind
[12-15s] [SHOT TYPE] + resolution
```

### Application récits historiques
Adoua, Nzinga, Chaka — SETUP → CRASH → FREEZE → REWIND → RESOLUTION

---

## Plateformes alternatives identifiées (août 2026)

| Plateforme | Modèle | Features uniques | Prix |
|---|---|---|---|
| **LOOVA** (loova.ai) | Seedance 1.5/2.0, Kling | Interface unifiée (Video + Image + Avatar) | À vérifier |
| **Higgsfield** | Seedance 2.5 | **Draw-to-Direct** (dessine trajectoire → caméra suit) | $49+/mo |
| **Dreamina** | Seedance 2.5 | Portail officiel ByteDance | $19/mo |
| **Pollo.ai** | Seedance 2.0/2.5 | Time-loop patterns | À vérifier |
| **kie.ai** | Seedance 2.0 + **2.5** | Moins cher, API | $0.05-0.315/s |

**Recommandation**: kie.ai reste le meilleur rapport qualité/prix pour production. Higgsfield pour Draw-to-Direct si budget client.
