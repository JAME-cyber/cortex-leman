# Kie.ai Suno API — Programmatic Music Generation

Générer de la musique via Suno (V4.5+) sans compte Suno, en utilisant la même clé `KIE_AI_API_KEY` que les images/vidéos.

## Endpoint

```
POST https://api.kie.ai/api/v1/jobs/createTask
GET  https://api.kie.ai/api/v1/jobs/recordInfo?taskId=<TASK_ID>
```

**Model slug**: `ai-music-api/generate`

⚠️ **PAS `/api/v1/generate`** — cet endpoint existe mais exige un `callBackUrl` (webhook). Utiliser `createTask` qui supporte le polling.

## Request Format

```json
{
  "model": "ai-music-api/generate",
  "input": {
    "title": "Song Title",
    "tags": "comma, separated, style, keywords",
    "instrumental": true,
    "custom_mode": true,
    "vocalGender": "m"
  }
}
```

### Champs

| Champ | Type | Requis | Notes |
|-------|------|--------|-------|
| `title` | string | oui (custom mode) | Titre du morceau |
| `tags` | string | oui (custom mode) | Description style, mots-clés séparés par virgules |
| `instrumental` | boolean | **oui** | `true` = instrumental, `false` = avec voix. Omettre = erreur 422 |
| `custom_mode` | boolean | non | `true` = title+tags, `false` = prompt simple |
| `vocalGender` | string | non | `"m"` ou `"f"` |

### Pièges

1. **`/api/v1/generate` = PIÈGE** — exige `callBackUrl`. Utiliser `/api/v1/jobs/createTask`.
2. Le champ est `instrumental`, PAS `make_instrumental`. Mauvais nom = 422.
3. `instrumental` est **obligatoire** même si `false` — l'omettre = 422.
4. Le sélecteur web affiche `V4_5PLUS` etc., mais l'API prend le slug `ai-music-api/generate`.

## Response Parsing

`resultJson` est une **string JSON** (nécessite `json.loads()`). Structure :

```json
{
  "code": 200,
  "data": [
    {
      "audio_url": "https://tempfile.aiquickdraw.com/r/<id>.mp3",
      "stream_audio_url": "https://cdn1.suno.ai/<id>.mp3",
      "duration": 180.72,
      "image_url": "https://cdn2.suno.ai/image_<id>.jpeg",
      "model_name": "chirp-auk-turbo",
      "title": "Song Title"
    }
  ]
}
```

**2 variations par request.** Télécharger via `audio_url` immédiatement — les liens `tempfile.aiquickdraw.com` sont time-limited.

## Coût

12 crédits par request (~$0.06). Retourne 2 variations.

## Polling

~90-150 secondes. Poll tous les 5s via `recordInfo?taskId=...`. State: `generating` → `success`/`fail`.

## Reference-Track Prompting (méthode validée)

Quand l'utilisateur fournit un lien YouTube ou un nom d'artiste comme référence de style :

1. **Extraire metadata** : `yt-dlp --dump-json --no-download <URL>` → title, channel (artist), tags, categories
2. **Traduire en tags Suno** : artist name + genre keywords + mood + tempo + production style
3. Exemple (session 2026-07-24) : user a envoyé GIMS - "Sois pas Timide" → tags devenus `"modern african pop, afro-pop dance beat, gims maître gims style, sunny warm synths, rhythmic guitar groove, danceable percussions, feel-good party vibe, 120 bpm dance groove"`

**Les références tracks produisent des résultats bien supérieurs aux descriptions de genre abstraites.** Toujours extraire et traduire la référence dans le champ tags.

## Multi-Country Cultural Blend Prompting

Pour du contenu couvrant plusieurs pays/cultures, nommer des instruments et rythmes spécifiques de chaque pays :

- 🇨🇲 **Cameroun** : makossa rhythm, west african guitar picking
- 🇸🇴 **Somalie** : oud melodies, horn of africa vocal harmonies
- 🇪🇬 **Égypte** : darbuka percussion, ney flute, nubian handclaps
- 🌍 **Générique** : sahel desert blues, kalimba, marimba, djembe, talking drum, highlife guitar

Pattern : `[pays1 instrument/rythme] + [pays2 instrument/rythme] + [pays3 instrument/rythme] + [mood] + [production style]`

## Itération — adapter le prompt au feedback user

L'utilisateur peut rejeter un premier batch (trop ambient, trop générique). Itérer en reformulant les tags selon le feedback :

| Feedback user | Ajustement tags |
|---|---|
| "Trop doux/ambient" | Ajouter "upbeat, dance beat, energetic, catchy" |
| "Trop générique" | Citer l'artiste/référence track dans les tags |
| "Je veux le style des 3 pays" | Noms d'instruments spécifiques par pays |
| Lien YouTube fourni | Extraire metadata yt-dlp → traduire en tags |

Ne pas hésiter à relancer 2-3 fois (12 cr chacune) — le coût est marginal (~$0.06/request).
