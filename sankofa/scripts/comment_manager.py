#!/usr/bin/env python3
"""YouTube Comments Manager for Sankofa channel.

Checks new comments, classifies commenters (returning vs new),
generates contextual replies, and posts them.

Usage:
    python3 comment_manager.py           # Check + reply (dry-run)
    python3 comment_manager.py --post    # Actually post replies
"""
import json
import requests
import os
import time
from datetime import datetime

TOKEN_PATH = os.path.expanduser("~/.config/youtubeuploader/broadcast.goauth")
CLIENT_SECRET_PATH = os.path.expanduser("~/african-heroes/CHANNEL/upload_pack/client_secret.json")
DB_PATH = os.path.expanduser("~/sankofa/commenters_db.json")

# Videos to monitor (public videos only)
VIDEOS = {
    "m3krL3cx_p4": "AMANIRÉNAS",
    "72ErHAysRiU": "NZINGA (longue)",
    "k4bhvsb-cZE": "NZINGA (courte)",
    "j6uIeqVgGwc": "MAMI WATA (longue)",
    "E4m25eP05oI": "MAMI WATA (courte)",
    "R8dqUlHOAwI": "ABLA POKOU (longue)",
    "Eb_1LmHWjxc": "ABLA POKOU (courte)",
    "b2pxJ1XYYPY": "MANSA MOUSSA",
}


def get_token():
    d = json.load(open(TOKEN_PATH))
    cs = json.load(open(CLIENT_SECRET_PATH))["installed"]
    resp = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": cs["client_id"],
        "client_secret": cs["client_secret"],
        "refresh_token": d["refresh_token"],
        "grant_type": "refresh_token"
    })
    return resp.json()["access_token"]


def load_db():
    if os.path.exists(DB_PATH):
        return json.load(open(DB_PATH))
    return {"commenters": {}, "replied_comments": []}


def save_db(db):
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)


def get_all_comments(token):
    """Fetch all comments across all monitored videos."""
    all_comments = []
    for vid, vid_name in VIDEOS.items():
        page_token = None
        while True:
            params = {
                "part": "snippet",
                "videoId": vid,
                "maxResults": 100,
                "order": "time",
            }
            if page_token:
                params["pageToken"] = page_token

            resp = requests.get(
                "https://www.googleapis.com/youtube/v3/commentThreads",
                headers={"Authorization": f"Bearer {token}"},
                params=params
            )
            if resp.status_code != 200:
                break

            data = resp.json()
            for item in data.get("items", []):
                snippet = item["snippet"]["topLevelComment"]["snippet"]
                all_comments.append({
                    "comment_id": item["id"],
                    "video_id": vid,
                    "video_name": vid_name,
                    "author": snippet.get("authorDisplayName", "?"),
                    "author_channel_id": snippet.get("authorChannelId", {}).get("value", ""),
                    "text": snippet.get("textOriginal", ""),
                    "text_display": snippet.get("textDisplay", ""),
                    "likes": snippet.get("likeCount", 0),
                    "published_at": snippet.get("publishedAt", ""),
                })

            page_token = data.get("nextPageToken")
            if not page_token:
                break
    return all_comments


def classify_commenter(author_id, db):
    """Determine if commenter is returning (likely subscriber) or new."""
    if author_id and author_id in db["commenters"]:
        count = db["commenters"][author_id].get("comment_count", 0)
        return "returning", count
    return "new", 0


def generate_reply(comment, status, prev_count):
    """Generate a contextual reply based on commenter status."""
    author = comment["author"]
    text = comment["text"].lower()
    video = comment["video_name"]

    # Base reply patterns by sentiment
    if any(w in text for w in ["❤️", "❤", "love", "j'aime", "super", "génial", "bravo", "bien", "instructif"]):
        sentiment = "positive"
    elif "?" in text:
        sentiment = "question"
    elif any(w in text for w in ["👍", "🔥", "💪", "✊", "👏"]):
        sentiment = "positive"
    else:
        sentiment = "neutral"

    if status == "returning":
        # Returning commenter = likely subscriber
        if sentiment == "positive":
            replies = [
                f"Toujours là {author.split()[0]} ! 🙏🏾 Merci pour ton soutien continu. La suite arrive bientôt !",
                f"Merci pour ta fidélité ! 🦁 D'autres héros et héroïnes arrivent, reste connecté(e) !",
                f"Content de te revoir ! ✊🏾 Ton soutien signifie beaucoup pour Sankofa.",
            ]
        elif sentiment == "question":
            replies = [
                f"Excellente question ! 🤔 On prépare justement du contenu qui y répondra. Abonne-toi pour ne pas le rater !",
                f"Bonne question ! 🔍 On creuse ce sujet dans un prochain épisode.",
            ]
        else:
            replies = [
                f"Merci d'être toujours là ! 🙏🏾 D'autres histoires arrivent très bientôt.",
            ]
    else:
        # New commenter = likely NOT subscribed
        if sentiment == "positive":
            replies = [
                f"Merci beaucoup ! 🙏🏾 Si tu aimes ce genre de contenu, abonne-toi — d'autres reines et rois africains arrivent !",
                f"Merci ! 🦁 Pour ne rien rater des prochaines histoires, c'est le bon moment pour s'abonner !",
                f"Cool que ça te plaise ! ✊🏾 Abonne-toi, on ne fait que commencer !",
            ]
        elif sentiment == "question":
            replies = [
                f"Bonne question ! 🔍 Abonne-toi, un épisode pourrait y répondre bientôt !",
            ]
        else:
            replies = [
                f"Merci pour ton commentaire ! 🙏🏾 Abonne-toi pour découvrir d'autres héros africains oubliés !",
            ]

    # Pick first reply (deterministic, no randomness for reproducibility)
    return replies[0]


def post_reply(token, comment_id, text):
    """Post a reply to a comment."""
    resp = requests.post(
        "https://www.googleapis.com/youtube/v3/comments?part=snippet",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "snippet": {
                "parentId": comment_id,
                "textOriginal": text
            }
        }
    )
    return resp.status_code == 200, resp.text


def main(post=False):
    token = get_token()
    db = load_db()
    comments = get_all_comments(token)

    # Filter out already-replied comments
    new_comments = [c for c in comments if c["comment_id"] not in db["replied_comments"]]

    if not new_comments:
        # Silent when nothing to report (watchdog pattern)
        return

    print(f"{len(new_comments)} nouveau(s) commentaire(s) à traiter:\n")

    for c in new_comments:
        status, prev_count = classify_commenter(c["author_channel_id"], db)
        reply = generate_reply(c, status, prev_count)

        status_label = "🔗 FIDÈLE" if status == "returning" else "🆕 NOUVEAU"
        print(f"📹 {c['video_name']}")
        print(f"  👤 {c['author']} ({status_label}, {c['likes']}👍)")
        print(f"  💬 {c['text']}")
        print(f"  ↩️  {reply}")

        if post:
            success, err = post_reply(token, c["comment_id"], reply)
            if success:
                print(f"  ✅ Réponse publiée")
                db["replied_comments"].append(c["comment_id"])
            else:
                print(f"  ❌ Erreur: {err[:200]}")
        else:
            print(f"  ⏸️  (dry-run — pas publié)")

        # Update commenter DB
        aid = c["author_channel_id"]
        if aid:
            if aid not in db["commenters"]:
                db["commenters"][aid] = {
                    "name": c["author"],
                    "comment_count": 1,
                    "first_seen": c["published_at"],
                    "last_seen": c["published_at"],
                }
            else:
                db["commenters"][aid]["comment_count"] += 1
                db["commenters"][aid]["last_seen"] = c["published_at"]

        print()

    save_db(db)
    print(f"Base: {len(db['commenters'])} commentateur(s) connu(s).")


if __name__ == "__main__":
    import sys
    post_mode = "--post" in sys.argv
    main(post=post_mode)
