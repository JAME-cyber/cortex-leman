#!/usr/bin/env python3
"""Upload videos to YouTube via Data API v3 (resumable upload, no browser needed).

DEPENDENCIES: requests only. OAuth2 token stored at ~/.config/youtubeuploader/broadcast.goauth

WHY THIS EXISTS: youtubeuploader CLI (porjo/youtubeuploader) requires xdg-open/browser
display to complete OAuth flow. On headless servers, it hangs or crashes even when the
token file already exists. This Python script uses the saved token directly and never
needs a browser — the reliable path for headless uploads.

SETUP (one-time):
1. Google Cloud Console → Create project → Enable YouTube Data API v3
2. OAuth consent screen → External → Add your Gmail as test user
3. Credentials → Create OAuth client ID → Desktop app → note client_id + client_secret
4. Exchange auth code for tokens (do this ONCE from any machine with a browser):
   a. Visit (replace CLIENT_ID):
      https://accounts.google.com/o/oauth2/auth?access_type=offline&client_id=CLIENT_ID&prompt=consent&redirect_uri=urn:ietf:wg:oauth:2.0:oob&response_type=code&scope=https://www.googleapis.com/auth/youtube.upload+https://www.googleapis.com/auth/youtube
   b. Authorize → Google gives you a code
   c. Exchange code for tokens:
      POST https://oauth2.googleapis.com/token
      Body: code=CODE&client_id=ID&client_secret=SECRET&redirect_uri=urn:ietf:wg:oauth:2.0:oob&grant_type=authorization_code
   d. Save response to ~/.config/youtubeuploader/broadcast.goauth (JSON format):
      {"access_token":"...","token_type":"Bearer","refresh_token":"...","expiry":"..."}

USAGE:
  from yt_upload import upload_video, upload_thumbnail, get_access_token
  vid = upload_video("/path/to/video.mp4", {"title":"...", "description":"...", "tags":[...]})
  upload_thumbnail(vid, "/path/to/thumbnail.png", get_access_token())

NOTES:
  - Category ID 27 = Education
  - Token auto-refreshes when expired
  - 8MB chunked resumable upload
  - Rate limit: wait ~10s between sequential uploads
"""
import requests
import json
import os
import time

CLIENT_ID = os.environ.get("YT_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("YT_CLIENT_SECRET", "")
TOKEN_PATH = os.path.expanduser("~/.config/youtubeuploader/broadcast.goauth")


def get_access_token():
    """Get valid access token, refresh if needed."""
    with open(TOKEN_PATH) as f:
        token_data = json.load(f)

    access_token = token_data["access_token"]
    refresh_token = token_data.get("refresh_token", "")

    # Verify token validity
    resp = requests.get("https://www.googleapis.com/oauth2/v1/tokeninfo",
                        params={"access_token": access_token})
    if resp.status_code == 200:
        return access_token

    # Token expired → refresh
    resp = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    })
    data = resp.json()
    access_token = data["access_token"]

    # Persist refreshed token
    token_data["access_token"] = access_token
    token_data["expiry"] = time.strftime(
        "%Y-%m-%dT%H:%M:%S.000Z",
        time.gmtime(time.time() + data.get("expires_in", 3600))
    )
    with open(TOKEN_PATH, 'w') as f:
        json.dump(token_data, f)

    return access_token


def upload_thumbnail(video_id, thumbnail_path, access_token):
    """Upload custom thumbnail for a video."""
    url = f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={video_id}"
    with open(thumbnail_path, 'rb') as f:
        resp = requests.post(url, headers={"Authorization": f"Bearer {access_token}"},
                             files={"file": f})
    if resp.status_code == 200:
        print(f"  ✅ Thumbnail uploaded")
    else:
        print(f"  ⚠️ Thumbnail failed: {resp.status_code} {resp.text[:200]}")


def upload_video(video_path, metadata, thumbnail_path=None):
    """Upload a video to YouTube with resumable upload.

    Args:
        video_path: Path to .mp4 file
        metadata: dict with keys: title, description, tags, categoryId (default "27"), privacyStatus (default "public")
        thumbnail_path: Optional path to .png thumbnail

    Returns:
        video_id string or None on failure
    """
    access_token = get_access_token()
    file_size = os.path.getsize(video_path)

    print(f"  Uploading: {os.path.basename(video_path)} ({file_size // 1024 // 1024} MB)")

    # Step 1: Start resumable session
    metadata_body = {
        "snippet": {
            "title": metadata["title"],
            "description": metadata["description"],
            "tags": metadata["tags"],
            "categoryId": metadata.get("categoryId", "27"),
        },
        "status": {
            "privacyStatus": metadata.get("privacyStatus", "public"),
            "selfDeclaredMadeForKids": False,
        }
    }

    resp = requests.post(
        "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        json=metadata_body
    )

    if resp.status_code not in (200, 201):
        print(f"  ❌ Failed to start upload: {resp.status_code}")
        print(f"     {resp.text[:500]}")
        return None

    upload_url = resp.headers.get("Location")
    if not upload_url:
        print(f"  ❌ No upload URL in response headers")
        return None

    # Step 2: Upload file in 8MB chunks
    chunk_size = 8 * 1024 * 1024
    uploaded = 0

    with open(video_path, 'rb') as f:
        while uploaded < file_size:
            chunk = f.read(chunk_size)
            chunk_len = len(chunk)
            end_byte = min(uploaded + chunk_len - 1, file_size - 1)

            resp = requests.put(
                upload_url,
                headers={"Content-Range": f"bytes {uploaded}-{end_byte}/{file_size}"},
                data=chunk
            )

            if resp.status_code in (200, 201):
                video_data = resp.json()
                video_id = video_data["id"]
                print(f"  ✅ Uploaded! Video ID: {video_id}")
                print(f"     URL: https://www.youtube.com/watch?v={video_id}")
                return video_id
            elif resp.status_code == 308:
                uploaded = end_byte + 1
                pct = (uploaded / file_size) * 100
                print(f"  ... {pct:.0f}%", end="\r")
            else:
                print(f"\n  ❌ Upload error: {resp.status_code} {resp.text[:300]}")
                return None

    return None
