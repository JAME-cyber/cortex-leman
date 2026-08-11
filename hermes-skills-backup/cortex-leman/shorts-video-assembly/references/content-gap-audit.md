# Content Gap Audit — Vérifier la couverture exhaustive du brief

## Problème

Session juil. 2026 (Culture en Saveur): après avoir splitté un panorama vidéo unique (V2) en 4 clips thématiques (T1 cuisine, T2 visio, T3 Nil, + restes), le contenu "henné + tambours + contes" a été **perdu** — aucun des nouveaux clips ne couvrait ces activités pourtant présentes dans le brief. L'utilisateur a dû demander "elle est où la vidéo avec les tambours et henné?".

## Root cause

Le découpage d'une vidéo longue en clips thématiques se fait souvent par affinité visuelle (cuisine → T1, nature → T3), sans vérifier que **chaque activité du programme client** est couverte par au moins un clip. Les activités "secondaires" (henné, musique, contes, sorties nature) tombent dans les cracks.

## Solution: Audit couverture brief via LLM externe

### Pattern en 3 étapes

#### 1. Compiler le brief + les vidéos en un seul prompt

```python
# Compiler le brief client
brief = open("research/client_brief.md").read()

# Compiler les VOs et contenus de chaque vidéo
video_summaries = []
for script_path in sorted(Path("scripts").glob("build_*.py")):
    code = script_path.read_text()
    # Extraire VO segments
    vo_matches = re.findall(r'"[^"]*"\).*?"([^"]+)"', code)
    video_summaries.append(f"### {script_path.stem}\nVO: {vo_matches}")
```

#### 2. Envoyer à GPT-5.6 (ou Claude) via OpenRouter

```python
prompt = f"""Tu es un consultant en marketing éducatif FR-CH.
Vérifie que CHAQUE élément du brief est couvert par au moins une vidéo.

## BRIEF:
{brief}

## VIDÉOS:
{chr(10).join(video_summaries)}

## LIVRABLE:
1. ✅ CE QUI EST COUVERT (par quelle vidéo)
2. ❌ CE QUI MANQUE ENCORE
3. ⚠️ INCOHÉRENCES (dates, prix, handles, noms)
Format: tableau concis."""

# Via OpenRouter
r = requests.post("https://openrouter.ai/api/v1/chat/completions",
    headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
    json={"model": "openai/gpt-5.6",
          "messages": [{"role": "user", "content": prompt}],
          "max_tokens": 2000})
```

#### 3. Corriger les gaps trouvés

L'audit révèle typiquement:
- **Contenu perdu au split** — activité du brief non couverte → créer une vidéo (ex: T4 Traditions)
- **Handles incorrects** — Instagram/email avec ou sans underscore
- **CTA incomplets** — champ oublié (horaires, promo, tranche d'âge)
- **Incohérences de date** — année périmée codée en dur

## Quand lancer cet audit

- **Avant de livrer** un lot de vidéos pour un client
- **Après un split** d'une vidéo longue en clips thématiques
- **Après un quality upgrade** (régénération des clips visuels)
- **À la demande utilisateur** ("assure-toi qu'on a rien oublié")

## Checklist activités à couvrir (Culture en Saveur — modèle)

Pour un stage multi-jours, vérifier que CHAQUE activité du programme est visible:

| Jour | Activité brief | Vidéo qui la couvre | Statut |
|------|---------------|---------------------|--------|
| Lun | Cuisine Égypte (Koshari) | T1, Programme | OK |
| Lun | Anthropologue Égypte ancienne | Programme (VO) | OK |
| Mar | Cuisine Cameroun (Ndolé) | T1 | OK |
| Mar | Jeux culinaires | — | manquant |
| Mer | Cuisine Somalie (Canjeero) | T1 | OK |
| Mer | Henné + motifs | T4 | OK |
| Mer | Contes somaliens | T4 | OK |
| Jeu | Cuisine Égypte (variante) | Programme | OK |
| Jeu | Patrimoine égyptien | T3 | OK |
| Ven | Musique camerounaise | T4 (tambours) | OK |
| Ven | Thé aux épices | T4 (contes) | OK |
| Ven | Dégustation / kiosque | Catering, Programme | OK |
| Tous | Sortie Rhône | T4 | OK |
| Tous | Visio orphelinat | T2 | OK |

## Bugs trouvés par cet audit (session juil. 2026)

- **Instagram**: brief = `@culture_ensaveurs` (avec underscore), vidéos = `@cultureensaveurs` (sans). 7 vidéos affectées. **Correction**: `patch` sur les 7 scripts (`@cultureensaveurs` → `@culture_ensaveurs`), re-render batch complet.
- **Henné/tambours/contes**: perdus au split panorama → T4 créée
- **Horaires**: manquants des CTA (juste "85 CHF" sans "8h30-18h30")
- **Promo fratrie**: "-10% dès le 2e enfant" oublié sur tous les CTA
- **Cross-check contacts**: l'email (`cultureensaveur@gmail.com`, sans S) et l'Instagram (`@culture_ensaveurs`, avec underscore + sans S) ont des orthographes différentes. Toujours vérifier chaque champ individuellement contre le brief, ne pas assumer qu'un seul correctif s'applique partout.
