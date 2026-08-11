# YouTube Video Upload — Headless via Data API v3

Upload videos to YouTube from a headless server (no browser GUI). Validated August 2026 on Sankofa (3 videos published).

## Why Not youtubeuploader CLI?

The `youtubeuploader` Go binary (porjo/youtubeuploader) is designed for desktop — it tries to open a browser for OAuth consent and hangs forever in headless mode (`Error: no DISPLAY environment variable specified`). Even with `-oauthUrl` flag, background processes can't write to stdin to paste the auth code.

## Working Approach: Manual OAuth Exchange + Data API v3

### Step 1: Create OAuth2 Credentials (one-time, user required)

1. Google Cloud Console → New Project → Enable **YouTube Data API v3**
2. OAuth consent screen → External → Add user email as test user
3. Credentials → Create OAuth client ID → **Desktop app**
4. Note `client_id` + `client_secret`

### Step 2: Exchange Auth Code for Tokens (Python)

User opens the consent URL in their browser, authorizes, gets a code. Then:

```python
import requests

resp = requests.post("https://oauth2.googleapis.com/token", data={
    "code": code,
    "client_id": client_id,
    "client_secret": client_secret,
    "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
    "grant_type": "authorization_code"
})
tokens = resp.json()  # access_token, refresh_token, expires_in
```

Save tokens to `~/.config/youtubeuploader/broadcast.goauth` (JSON).

### Step 3: Resumable Upload via Data API v3

```python
# Start resumable session
resp = requests.post(
    "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
    headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
    json={
        "snippet": {"title": "...", "description": "...", "tags": [...], "categoryId": "27"},
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
    }
)
upload_url = resp.headers["Location"]

# Upload in 8MB chunks
with open(video_path, 'rb') as f:
    while uploaded < file_size:
        chunk = f.read(8 * 1024 * 1024)
        resp = requests.put(upload_url, headers={
            "Content-Range": f"bytes {uploaded}-{end_byte}/{file_size}"
        }, data=chunk)
        if resp.status_code in (200, 201):
            video_id = resp.json()["id"]  # done!
```

### Step 4: Thumbnail Upload (requires channel verification)

```python
resp = requests.post(
    f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={video_id}",
    headers={"Authorization": f"Bearer {access_token}"},
    files={"file": open(thumbnail_path, 'rb')}
)
# 403 = channel not verified (needs phone verification in YouTube Studio)
```

## Token Refresh

Tokens expire in ~1 hour. Refresh silently:

```python
resp = requests.post("https://oauth2.googleapis.com/token", data={
    "client_id": client_id, "client_secret": client_secret,
    "refresh_token": refresh_token, "grant_type": "refresh_token"
})
new_access_token = resp.json()["access_token"]
```

## Pitfalls

| Problem | Fix |
|---------|-----|
| `youtubeuploader` hangs in background | Use Python Data API v3 directly |
| OAuth consent "Access blocked" | Add user email as test user in consent screen |
| Thumbnail 403 | Channel must be phone-verified (YouTube Studio → Settings → Channel → Verification) |
| Token expires between uploads | Check tokeninfo endpoint, refresh if needed |
| `redirect_uri` mismatch | Must be `urn:ietf:wg:oauth:2.0:oob` (not `http://localhost`) |
| categoryId unknown | 27 = Education, 22 = People & Blogs, 24 = Entertainment |

## Complete Upload Script

Working script at `african-heroes/CHANNEL/upload_pack/yt_upload.py` — handles 3-video batch upload with 10s delay between each, thumbnail attachment, and token refresh.
