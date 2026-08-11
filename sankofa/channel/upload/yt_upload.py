#!/usr/bin/env python3
"""Upload videos to YouTube via the Data API v3 (resumable upload).

No external deps beyond requests — uses the saved OAuth2 token.
"""
import requests
import json
import os
import time
import sys

import os
CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
TOKEN_PATH = os.path.expanduser("~/.config/youtubeuploader/broadcast.goauth")

def get_access_token():
    """Get valid access token, refresh if needed."""
    with open(TOKEN_PATH) as f:
        token_data = json.load(f)

    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]

    # Verify
    resp = requests.get("https://www.googleapis.com/oauth2/v1/tokeninfo",
                        params={"access_token": access_token})
    if resp.status_code == 200:
        return access_token

    # Refresh
    print("  Refreshing token...")
    resp = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    })
    data = resp.json()
    access_token = data["access_token"]

    # Save new token
    token_data["access_token"] = access_token
    token_data["expiry"] = time.strftime("%Y-%m-%dT%H:%M:%S.000Z",
                                          time.gmtime(time.time() + data.get("expires_in", 3600)))
    with open(TOKEN_PATH, 'w') as f:
        json.dump(token_data, f)

    return access_token


def upload_thumbnail(video_id, thumbnail_path, access_token):
    """Upload custom thumbnail."""
    url = f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={video_id}"
    with open(thumbnail_path, 'rb') as f:
        resp = requests.post(url, headers={"Authorization": f"Bearer {access_token}"},
                             files={"file": f})
    if resp.status_code == 200:
        print(f"  ✅ Thumbnail uploaded")
    else:
        print(f"  ⚠️ Thumbnail failed: {resp.status_code} {resp.text[:200]}")


def upload_video(video_path, metadata, thumbnail_path=None):
    """Upload a video to YouTube with resumable upload."""
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

    # Step 2: Upload the file in chunks
    chunk_size = 8 * 1024 * 1024  # 8MB chunks
    uploaded = 0

    with open(video_path, 'rb') as f:
        while uploaded < file_size:
            chunk = f.read(chunk_size)
            chunk_len = len(chunk)
            end_byte = min(uploaded + chunk_len - 1, file_size - 1)

            resp = requests.put(
                upload_url,
                headers={
                    "Content-Range": f"bytes {uploaded}-{end_byte}/{file_size}",
                },
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


if __name__ == "__main__":
    videos = [
        {
            "id": "nzinga",
            "video": "/home/tars/african-heroes/CHANNEL/video1_nzinga/clips/nzinga_v7.mp4",
            "thumbnail": "/home/tars/african-heroes/CHANNEL/branding/youtube/thumbnail_nzinga.png",
            "title": "NZINGA — La Reine Guerrière qui a vaincu les Portugais | Sankofa",
            "description": """👸🏾 NZINGA M'BANDE (1583-1663) — La reine qui a refusé de plier.

Dans les hautes terres du Ndongo (actuelle Angola), une femme est devenue le cauchemar de l'empire colonial portugais. Diplomate brillante, stratège militaire, elle a mené la résistance armée pendant plus de 40 ans.

Nzinga n'a pas seulement combattu. Elle a négocié, formé des alliances, adapté la guerre à son terrain. Quand les Portugais ont cru la briser, elle a disparu dans la forêt pour revenir plus forte.

🔴 Son arme principale : l'intelligence.

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎬 SANKOFA — Retourne la chercher.
L'histoire africaine comme on ne te l'a jamais racontée.

Abonne-toi pour ne rien manquer des prochaines vidéos !

#Nzinga #HistoireAfrique #Angola #ReineGuerrière #Sankofa""",
            "tags": ["Nzinga", "histoire Afrique", "Angola", "Ndongo", "reine guerrière",
                      "résistance africaine", "colonisation portugaise", "Sankofa",
                      "histoire africaine", "Black History", "femmes puissantes",
                      "reines d'Afrique", "histoire mondiale", "éducation", "documentaire histoire"],
            "categoryId": "27",
            "privacyStatus": "public"
        },
        {
            "id": "mami_wata",
            "video": "/home/tars/african-heroes/CHANNEL/video2_mami_wata/clips/mami_wata_noloop.mp4",
            "thumbnail": "/home/tars/african-heroes/CHANNEL/branding/youtube/thumbnail_mami_wata.png",
            "title": "MAMI WATA — L'Esprit des Eaux qui fascine l'Afrique | Sankofa",
            "description": """🌊 MAMI WATA — La mère des eaux.

Pas une simple légende. Un archétype spirituel présent du Sénégal au Congo, du Bénin aux Caraïbes. Mami Wata n'appartient à aucun pays. Elle traverse l'océan et le temps.

Belle. Terrifiante. Génereuse. Elle attire, séduit, et exige le respect.

Mami Wata est devenue l'un des symboles les plus durables de la spiritualité africaine et sa diaspora — un pont entre les mondes, un miroir de nos désirs les plus profonds.

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎬 SANKOFA — Retourne la chercher.

Abonne-toi pour ne rien manquer !

#MamiWata #SpiritualitéAfricaine #HistoireAfrique #Sankofa""",
            "tags": ["Mami Wata", "esprit des eaux", "spiritualité africaine",
                      "croyances africaines", "vodun", "Sankofa", "histoire Afrique",
                      "mythologie africaine", "déesse", "diaspora africaine",
                      "religions traditionnelles", "folklore"],
            "categoryId": "27",
            "privacyStatus": "public"
        },
        {
            "id": "abla_pokou",
            "video": "/home/tars/african-heroes/CHANNEL/video3_abla_pokou/clips/abla_pokou.mp4",
            "thumbnail": "/home/tars/african-heroes/CHANNEL/branding/youtube/thumbnail_abla_pokou.png",
            "title": "ABLA POKOU — La Reine qui a sacrifié son fils pour son peuple | Sankofa",
            "description": """👶🏾🩸 ABLA POKOU — Le sacrifice qui a créé une nation.

XVIIIe siècle, Côte de l'Or (actuel Ghana). La Confédération ashanti avance, implacable. Abla Pokou, princesse du peuple Akan, mène les siens vers l'ouest, vers la survie.

Mais la rivière Comoé bloque la route. En crue. Mortelle. Les poursuivants se rapprochent.

La légende dit qu'Abla Pokou a fait l'inimaginable. Elle a donné son fils unique au fleuve. Et l'eau s'est ouverte.

De l'autre côté, son peuple est devenu les Baoulé — "Ba ouli", "l'enfant est mort". Une nation est née d'un sacrifice.

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎬 SANKOFA — Retourne la chercher.

Abonne-toi pour ne rien manquer !

#AblaPokou #Baoulé #HistoireAfrique #Ghana #Sankofa #ReineAfricaine""",
            "tags": ["Abla Pokou", "Baoulé", "histoire Afrique", "Ghana", "Côte de l'Or",
                      "Sankofa", "reine africaine", "peuple Akan", "sacrifice",
                      "Ashanti", "histoire Côte d'Ivoire", "légendes africaines"],
            "categoryId": "27",
            "privacyStatus": "public"
        }
    ]

    results = []
    for i, v in enumerate(videos):
        print(f"\n[{i+1}/3] {v['id'].upper()}")
        video_id = upload_video(v["video"], v)
        if video_id and os.path.exists(v["thumbnail"]):
            access_token = get_access_token()
            upload_thumbnail(video_id, v["thumbnail"], access_token)
            results.append({"id": v["id"], "video_id": video_id,
                           "url": f"https://www.youtube.com/watch?v={video_id}"})
            # Wait between uploads to avoid rate limiting
            if i < len(videos) - 1:
                print("  Waiting 10s...")
                time.sleep(10)
        else:
            print(f"  ❌ Upload failed for {v['id']}")
            results.append({"id": v["id"], "error": "upload failed"})

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    for r in results:
        if "url" in r:
            print(f"  ✅ {r['id']}: {r['url']}")
        else:
            print(f"  ❌ {r['id']}: FAILED")
