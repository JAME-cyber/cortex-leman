# YouTube Upload — youtubeuploader + OAuth2

## Tool: youtubeuploader (porjo/youtubeuploader)

Binary Go, pas besoin de Go installé — télécharger le release précompilé.

```bash
# Install (v1.25.5, Linux amd64)
curl -sL "https://github.com/porjo/youtubeuploader/releases/download/v1.25.5/youtubeuploader_1.25.5_Linux_amd64.tar.gz" -o /tmp/yu.tar.gz
cd /tmp && tar xzf yu.tar.gz
cp youtubeuploader ~/.local/bin/ && chmod +x ~/.local/bin/youtubeuploader
youtubeuploader -version
```

## OAuth2 Setup (one-time, user must do manually)

youtubeuploader a besoin d'un `client_secret.json` (OAuth2 Desktop app).

### Étapes utilisateur (≈5 min)

1. https://console.cloud.google.com/ → créer projet
2. APIs & Services → Library → **YouTube Data API v3** → Enable
3. APIs & Services → OAuth consent screen → External → remplir
4. APIs & Services → Credentials → Create Credentials → **OAuth client ID** → Desktop app
5. Télécharger le JSON → sauver comme `client_secret.json`
6. Placer dans le dossier du projet

### Premier run

Au premier appel, youtubeuploader ouvre un browser pour l'auth OAuth2.
Sur serveur headless : utiliser l'option `-oob` (out-of-band) ou copier l'URL
dans un browser local, autoriser, coller le code.

Le token `request.token` est créé automatiquement et réutilisé.

## Upload avec métadonnées

youtubeuploader accepte un fichier JSON `-meta` avec tous les champs :

```json
{
  "title": "Titre de la vidéo | Sankofa",
  "description": "Description complète avec hashtags...",
  "tags": ["tag1", "tag2"],
  "categoryId": "27",
  "privacyStatus": "public"
}
```

### Commande d'upload

```bash
youtubeuploader \
  -filename video.mp4 \
  -meta metadata.json \
  -thumbnail thumbnail.png \
  -clientSecret client_secret.json \
  -oob
```

## Pack métadonnées multi-vidéos

Pour un lancement de chaîne (3+ vidéos), préparer un dossier `upload_pack/` :

```
upload_pack/
  client_secret.json      # OAuth2 credentials
  request.token           # Auto-généré au 1er run
  meta_video1.json
  meta_video2.json
  meta_video3.json
```

### Catégorie YouTube utile

| ID | Catégorie |
|----|-----------|
| 27 | Education |
| 22 | People & Blogs |
| 24 | Entertainment |

## Pitfalls

- **Limite taille vidéo** : YouTube accepte jusqu'à 256GB, pas de souci pour nos vidéos (10-60MB)
- **Quota API** : 10,000 units/jour par défaut. Un upload = 1600 units. Donc ~6 uploads/jour max
- **Thumbnail** : doit être < 2MB, PNG ou JPG, ratio 16:9 recommandé (1280×720)
- **OAuth consent screen** : si "Testing" status, seuls les emails whitelistés peuvent uploader. Passer en "Production" pour publier
- **Token expiry** : le refresh token expire si inactif 6 mois. Re-run avec `-oob` pour régénérer
