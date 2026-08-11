#!/usr/bin/env python3
"""Build Mami Wata SHORT (<60s): recut from original segments.

Keeps: 0(hook), 2(identity), 3(pacte), 7(diaspora), 8(new CTA)
Cuts:  1(revelation), 4(origine), 5(greffe), 6(vivant)
"""
import json, os, subprocess, shutil
from pathlib import Path

BASE = Path("/home/tars/african-heroes/CHANNEL/video2_mami_wata")
BROLL_VID_DIR = BASE / "broll_video"
AUDIO_DIR = BASE / "audio"
CLIPS_DIR = BASE / "clips" 
TMP_DIR = BASE / "tmp_short"
CAPTIONS_DIR = BASE / "captions"
TMP_DIR.mkdir(parents=True, exist_ok=True)
CLIPS_DIR.mkdir(parents=True, exist_ok=True)

BGM_PATH = Path("/home/tars/crypto-project/audio/bgm_stellardrone.mp3")
WATERMARK_PATH = Path("/home/tars/african-heroes/CHANNEL/branding/watermark_sankofa.png")

# Short recut config: mapping original segments to short
SHORT_BEATS = [
    {"orig_seg": 0, "id": "01_hook",      "video": "00_fisher_meets_mermaid.mp4",    "caption_overlay": True},
    {"orig_seg": 2, "id": "03_identity",  "video": "02_mami_wata_python.mp4",       "caption_overlay": False},
    {"orig_seg": 3, "id": "04_pacte",     "video": "03_water_spirit_temple.mp4",    "caption_overlay": False},
    {"orig_seg": 7, "id": "07_diaspora",  "video": "07_diaspora_voyage.mp4",        "caption_overlay": False},
    {"orig_seg": 8, "id": "09_cta",       "fullscreen": True},  # new short CTA
]

# Audio mapping: which audio file for each short beat
AUDIO_MAP = {
    "01_hook":      "01_hook.mp3",
    "03_identity":  "03_identity.mp3",
    "04_pacte":     "04_pacte.mp3", 
    "07_diaspora":  "07_diaspora.mp3",
    "09_cta":       "09_cta_short.mp3",  # new short CTA
}


def get_dur(path):
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except (ValueError, AttributeError):
        return -1.0


def extract_audio_from_segment(seg_path, out_path):
    """Extract audio from segment video file"""
    cmd = [
        "ffmpeg", "-y", "-i", str(seg_path),
        "-vn", "-acodec", "libmp3lame", "-b:a", "192k",
        str(out_path)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"audio extract fail: {r.stderr[-300:]}")


def build_video_segment(video_path, dur, out_path):
    """Build video segment with Ken Burns effect"""
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-vf", "scale=1080:1920:flags=lanczos,format=yuv420p",
        "-t", f"{dur:.3f}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-r", "24", str(out_path)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"video segment fail: {r.stderr[-300:]}")


def build_caption_segment(caption_png, dur, out_path):
    """Build fullscreen caption segment"""
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-framerate", "24",
        "-t", f"{dur:.3f}", "-i", str(caption_png),
        "-vf", "scale=1080:1920,format=yuv420p",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-r", "24", str(out_path)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"caption seg fail: {r.stderr[-300:]}")


def overlay_caption(base_video, caption_png, dur, out_path):
    """Overlay caption on video"""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(base_video),
        "-loop", "1", "-framerate", "24", "-t", f"{dur:.3f}",
        "-i", str(caption_png),
        "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]",
        "-map", "[v]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", "24", str(out_path)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"overlay fail: {r.stderr[-300:]}")


def main():
    print("\n[1/4] Extract audio from segments and build video segments...")
    
    # Prepare audio files from existing audio directory
    audio_files = []
    for beat in SHORT_BEATS:
        audio_filename = AUDIO_MAP[beat["id"]]
        audio_path = AUDIO_DIR / audio_filename
        if not audio_path.exists():
            raise RuntimeError(f"Audio missing: {audio_path}")
        audio_files.append(audio_path)

    # Build video segments
    seg_paths = []
    for i, beat in enumerate(SHORT_BEATS):
        audio_file = audio_files[i]
        dur = get_dur(str(audio_file))
        cap_png = CAPTIONS_DIR / f"cap_{beat['id']}.png"
        seg = TMP_DIR / f"seg_{i:02d}.mp4"

        if seg.exists() and get_dur(str(seg)) >= dur - 0.2:
            print(f"    [seg {i}] {beat['id']} (cached, {dur:.1f}s)")
            seg_paths.append(seg)
            continue

        if beat.get("fullscreen"):
            build_caption_segment(cap_png, dur, seg)
            print(f"    [seg {i}] {beat['id']} 📝 fullscreen CTA ({dur:.1f}s)")
        else:
            vid_path = BROLL_VID_DIR / beat["video"]
            if vid_path.exists():
                base_vid = TMP_DIR / f"base_{i:02d}.mp4" 
                build_video_segment(vid_path, dur, base_vid)
                if beat.get("caption_overlay", False):
                    overlay_caption(base_vid, cap_png, dur, seg)
                    print(f"    [seg {i}] {beat['id']} 🎬+📝 ({dur:.1f}s)")
                else:
                    # Copy base_vid to seg for consistency in concat
                    import shutil
                    shutil.copy2(base_vid, seg)
                    print(f"    [seg {i}] {beat['id']} 🎬 ({dur:.1f}s)")
            else:
                build_caption_segment(cap_png, dur, seg)
                print(f"    [seg {i}] {beat['id']} ⚠️ video missing, caption fallback")
        seg_paths.append(seg)

    # 2. Concat video
    print("\n[2/4] Concaténation vidéo...")
    concat_list = TMP_DIR / "concat.txt"
    with open(concat_list, "w") as f:
        for p in seg_paths:
            f.write(f"file '{p.resolve()}'\\n")
    video_concat = TMP_DIR / "video_only.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list), "-c", "copy", str(video_concat)
    ], capture_output=True, text=True, check=True)

    # 3. Concat audio
    print("\n[3/4] Concaténation audio...")
    audio_concat_list = TMP_DIR / "audio_concat.txt"
    with open(audio_concat_list, "w") as f:
        for audio_path in audio_files:
            f.write(f"file '{audio_path.resolve()}'\\n")
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
    out_path = CLIPS_DIR / "mami_wata_short.mp4"

    cmd = [
        "ffmpeg", "-y", "-i", str(video_audio), "-i", str(BGM_PATH),
        "-i", str(WATERMARK_PATH),
        "-filter_complex",
        f"[0:v][2:v]overlay=x=W-w-20:y=H-h-20[vout];"
        f"[1:a]volume=-28dB,afade=t=in:st=0:d=1,afade=t=out:st={dur_total-2}:d=2[bgm];"
        f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=0[aout]",
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
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