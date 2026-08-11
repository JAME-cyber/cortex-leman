#!/usr/bin/env python3
"""Build Mansa Moussa SHORT (<60s): recut from original segments.

Keeps: 0(hook), 2(context), 3(pelerinage), 4(caire), 7(verdict), 8(new CTA)
Cuts:  1(promise), 5(renversement), 6(nuance)
"""
import json, os, subprocess, shutil
from pathlib import Path

BASE = Path("/home/tars/african-heroes/CHANNEL/video4_mansa_moussa")
BROLL_IMG_DIR = BASE / "broll"
AUDIO_DIR = BASE / "audio"
CLIPS_DIR = BASE / "clips"
TMP_DIR = BASE / "tmp_short"
CAPTIONS_DIR = BASE / "captions"
TMP_DIR.mkdir(parents=True, exist_ok=True)

BGM_PATH = Path("/home/tars/crypto-project/audio/bgm_stellardrone.mp3")
WATERMARK_PATH = Path("/home/tars/african-heroes/CHANNEL/branding/watermark_sankofa.png")

# Short recut config: (original_seg_index, image, caption, direction)
SHORT_BEATS = [
    {"id": "01_hook",       "image": "01_hook.png",       "direction": "zoom_in",  "caption_overlay": True},
    {"id": "03_context",    "image": "03_context.png",    "direction": "zoom_in",  "caption_overlay": False},
    {"id": "04_pelerinage", "image": "04_pelerinage.png",  "direction": "zoom_out", "caption_overlay": False},
    {"id": "05_caire",      "image": "05_caire.png",      "direction": "zoom_in",  "caption_overlay": False},
    {"id": "08_verdict",    "image": "08_verdict.png",    "direction": "zoom_out", "caption_overlay": False},
    {"id": "09_cta",        "image": "09_cta.png",        "fullscreen": True},
]

# Audio mapping: which audio file for each short beat
AUDIO_MAP = {
    "01_hook":       "01_hook.mp3",
    "03_context":    "03_context.mp3",
    "04_pelerinage": "04_pelerinage.mp3",
    "05_caire":      "05_caire.mp3",
    "08_verdict":    "08_verdict.mp3",
    "09_cta":        "09_cta_short.mp3",  # new short CTA
}


def get_dur(path):
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except (ValueError, AttributeError):
        return -1.0


def build_kenburns(image_path, dur, out_path, direction="zoom_in"):
    from PIL import Image as PILImage

    tmp_scaled = TMP_DIR / f"_kb_scaled_{image_path.stem}.png"
    with PILImage.open(str(image_path)) as src:
        src = src.convert("RGB")
        overscale = 1.08
        target_w = int(1080 * overscale)
        target_h = int(1920 * overscale)
        src_resized = src.resize((target_w, target_h), PILImage.LANCZOS)
        src_resized.save(str(tmp_scaled), "PNG")

    if direction == "zoom_in":
        crop_expr = (
            f"crop=w=1080:h=1920:"
            f"x='(iw-1080)/2*(1-t/{dur:.1f})':"
            f"y='(ih-1920)/2*(1-t/{dur:.1f})'"
        )
    elif direction == "zoom_out":
        crop_expr = (
            f"crop=w=1080:h=1920:"
            f"x='(iw-1080)/2*(t/{dur:.1f})':"
            f"y='(ih-1920)/2*(t/{dur:.1f})'"
        )
    else:
        crop_expr = (
            f"crop=w=1080:h=1920:"
            f"x='(iw-1080)/2':"
            f"y='(ih-1920)/2'"
        )

    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-framerate", "24",
        "-t", f"{dur:.3f}", "-i", str(tmp_scaled),
        "-vf", f"{crop_expr},format=yuv420p",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-r", "24", str(out_path)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    tmp_scaled.unlink(missing_ok=True)
    if r.returncode != 0:
        print(f"    ⚠️ Ken Burns fail, fallback scale")
        cmd2 = [
            "ffmpeg", "-y", "-loop", "1", "-framerate", "24",
            "-t", f"{dur:.3f}", "-i", str(image_path),
            "-vf", "scale=1080:1920:flags=lanczos,format=yuv420p",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20",
            "-pix_fmt", "yuv420p", "-r", "24", str(out_path)]
        r2 = subprocess.run(cmd2, capture_output=True, text=True)
        if r2.returncode != 0:
            raise RuntimeError(f"kenburns fallback fail: {r2.stderr[-300:]}")


def build_caption_segment(caption_png, dur, out_path):
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-framerate", "24",
        "-t", f"{dur:.3f}", "-i", str(caption_png),
        "-vf", "scale=1080:1920,format=yuv420p",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-r", "24", str(out_path)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"caption seg fail: {r.stderr[-300:]}")


def overlay_caption(base_video, caption_png, dur, out_path):
    cmd = [
        "ffmpeg", "-y",
        "-i", str(base_video),
        "-loop", "1", "-framerate", "24", "-t", f"{dur:.3f}",
        "-i", str(caption_png),
        "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]",
        "-map", "[v]",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", "24", str(out_path)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"overlay fail: {r.stderr[-300:]}")


def main():
    dur_data = json.loads((AUDIO_DIR / "durations.json").read_text())
    dur_map = {b["id"]: b["duration"] for b in dur_data}

    # 1. Build segments
    print("\n[1/4] Build segments (Short recut)...")
    seg_paths = []
    for i, beat in enumerate(SHORT_BEATS):
        bid = beat["id"]
        audio_file = AUDIO_MAP[bid]
        audio_path = AUDIO_DIR / audio_file
        dur = get_dur(str(audio_path))
        cap_png = CAPTIONS_DIR / f"cap_{bid}.png"
        seg = TMP_DIR / f"seg_{i:02d}.mp4"

        if seg.exists() and get_dur(str(seg)) >= dur - 0.2:
            print(f"    [seg {i}] {bid} (cached, {dur:.1f}s)")
            seg_paths.append(seg)
            continue

        if beat.get("fullscreen"):
            build_caption_segment(cap_png, dur, seg)
            print(f"    [seg {i}] {bid} 📝 fullscreen CTA ({dur:.1f}s)")
        else:
            ipath = BROLL_IMG_DIR / beat["image"]
            if ipath.exists():
                kb_vid = TMP_DIR / f"kb_{i:02d}.mp4"
                direction = beat.get("direction", "zoom_in")
                build_kenburns(ipath, dur, kb_vid, direction)
                if beat.get("caption_overlay", False):
                    overlay_caption(kb_vid, cap_png, dur, seg)
                    print(f"    [seg {i}] {bid} 🖼️+📝 ({direction}, {dur:.1f}s)")
                else:
                    seg = kb_vid
                    print(f"    [seg {i}] {bid} 🖼️ ({direction}, {dur:.1f}s)")
            else:
                build_caption_segment(cap_png, dur, seg)
                print(f"    [seg {i}] {bid} ⚠️ image missing, caption fallback")
        seg_paths.append(seg)

    # 2. Concat video
    print("\n[2/4] Concaténation vidéo...")
    concat_list = TMP_DIR / "concat.txt"
    with open(concat_list, "w") as f:
        for p in seg_paths:
            f.write(f"file '{p.resolve()}'\n")
    video_concat = TMP_DIR / "video_only.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list), "-c", "copy", str(video_concat)
    ], capture_output=True, text=True, check=True)

    # 3. Concat audio
    print("\n[3/4] Concaténation audio...")
    audio_concat_list = TMP_DIR / "audio_concat.txt"
    with open(audio_concat_list, "w") as f:
        for beat in SHORT_BEATS:
            mp3_path = (AUDIO_DIR / AUDIO_MAP[beat["id"]]).resolve()
            f.write(f"file '{mp3_path}'\n")
    audio_full = TMP_DIR / "audio_full.mp3"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(audio_concat_list),
        "-c:a", "libmp3lame", "-b:a", "192k", str(audio_full)
    ], capture_output=True, text=True, check=True)

    # Merge video + audio
    video_audio = TMP_DIR / "video_audio.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-i", str(video_concat), "-i", str(audio_full),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p", "-r", "24", "-shortest", str(video_audio)
    ], capture_output=True, text=True, check=True)

    # 4. BGM + watermark
    print("\n[4/4] BGM + watermark...")
    dur_total = get_dur(str(video_audio))
    out_path = CLIPS_DIR / "mansa_moussa_short.mp4"

    cmd = [
        "ffmpeg", "-y", "-i", str(video_audio), "-i", str(BGM_PATH),
        "-i", str(WATERMARK_PATH),
        "-filter_complex",
        f"[0:v][2:v]overlay=x=W-w-20:y=H-h-20[vout];"
        f"[1:a]volume=-28dB,afade=t=in:st=0:d=1,afade=t=out:st={dur_total-2}:d=2[bgm];"
        f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=0[aout]",
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k", "-shortest",
        "-pix_fmt", "yuv420p", "-r", "24", str(out_path)]

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ERR final: {r.stderr[-800:]}")
        raise RuntimeError("final assembly failed")

    size_mb = os.path.getsize(out_path) / (1024 * 1024)
    final_dur = get_dur(str(out_path))
    print(f"\n{'='*50}")
    print(f"✅ SHORT FINAL: {out_path}")
    print(f"   Durée: {final_dur:.1f}s | Taille: {size_mb:.1f} MB")
    print(f"   Under 60s: {'✅' if final_dur < 60 else '❌'}")
    return out_path


if __name__ == "__main__":
    main()
