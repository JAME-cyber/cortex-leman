#!/usr/bin/env python3
"""Build vertical 9:16 clips for a stock-actor series.

Generalized from the OVHcloud B/C/D build (2026-07-18).
Reproduces Clip A's validated pipeline: edge-tts + HTML slides (Playwright capture)
+ Ken Burns pan (NOT zoompan) + burned subtitles (ASS PlayResY=1920) + BGM.

Usage:
    python3 build_clips_template.py B      # build one clip
    python3 build_clips_template.py B C D  # build several
    python3 build_clips_template.py all    # build all defined clips

To adapt for a new actor: copy this file, edit CLIPS dict (slide→voiceline pairs)
and create matching slide HTML files in SLIDES_DIR.
"""
import asyncio, os, subprocess, re, sys
from pathlib import Path
import edge_tts

BASE = Path("/home/tars/crypto-project/CHANNEL/video3")
SLIDES_DIR = BASE / "slides"
AUDIO_DIR = BASE / "audio"
CLIPS_DIR = BASE / "clips"
TMP_DIR = BASE / "tmp_clips"
for d in [AUDIO_DIR, CLIPS_DIR, TMP_DIR]:
    d.mkdir(parents=True, exist_ok=True)

VOICE = "fr-FR-HenriNeural"
RATE = "+10%"
BGM_PATH = "/home/tars/crypto-project/audio/bgm_stellardrone.mp3"

# Branding assets — INTRO (5s) prépendu + SIGNATURE (3.5s) appendé sur chaque clip
# Assets existants dans /home/tars/crypto-project/branding/ — TOUJOURS vérifier avant recréer.
INTRO_PATH = BASE / "clips" / "intro_9x16.mp4"
SIGNATURE_PATH = BASE / "clips" / "signature_3p5s.mp4"

# === Prononciation TTS (sigles écorchés par edge-tts) ===
# OVH = phonétique d'un bloc (validé). Autres = points espacés (sigle isolé).
# Ne JAMAIS ajouter un sigle sans test comparatif préalable (voir references/edge-tts-pronunciation.md).
PHONETIC_MAP = {
    "OVHcloud": "Ovéache Cloud",
    "OVH": "Ovéache",
    "Soitec": "Soitèce",
    "ASML": "A. S. M. L.",
    "AWS": "A. W. S.",
    "GCP": "G. C. P.",
    "GPU": "G. P. U.",
    "PEA": "P. E. A.",
    # ANSSI, FISA → BRUTS (native edge-tts validée meilleure que toute substitution, 2026-07-18)
}

def phonetic_normalize(text):
    for orig, phon in PHONETIC_MAP.items():
        text = text.replace(orig, phon)
    return text

# === Define one entry per clip: list of (slide_html_basename, voiceline) beats ===
CLIPS = {
    "B": {
        "name": "Example clip",
        "beats": [
            ("slide_00_hook", "Voiceover line one."),
            ("slide_01_body", "Voiceover line two with Ovéache Cloud in it."),
        ],
    },
}


def get_dur(path):
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", path], capture_output=True, text=True)
    return float(r.stdout.strip())


def fmt_time(s):
    h = int(s // 3600); m = int((s % 3600) // 60)
    sec = int(s % 60); ms = int((s % 1) * 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


async def gen_tts(beats, clip_audio_dir):
    results = []
    for i, (_, text) in enumerate(beats):
        clean = phonetic_normalize(re.sub(r'\*+([^*]+)\*+', r'\1', text))
        path = clip_audio_dir / f"beat_{i:02d}.mp3"
        await edge_tts.Communicate(clean, VOICE, rate=RATE).save(str(path))
        dur = get_dur(str(path))
        results.append((i, text, path, dur))
        print(f"    [beat {i}] {dur:.1f}s | {clean[:60]}...")
    return results


def capture_slides(slide_names, clip_img_dir):
    from playwright.sync_api import sync_playwright
    captured = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1920})
        for slide_name in slide_names:
            html_path = SLIDES_DIR / f"{slide_name}.html"
            if not html_path.exists():
                print(f"    ⚠️ Slide manquante: {html_path}")
                continue
            img_path = clip_img_dir / f"{slide_name}.png"
            page.goto(f"file://{html_path}")
            page.wait_for_timeout(600)
            page.screenshot(path=str(img_path), full_page=False)
            captured[slide_name] = img_path
        browser.close()
    return captured


def build_video_segment(img_path, dur, out_path, zoom="in"):
    """Ken Burns via scale+crop (NOT zoompan — 10x too slow in vertical)."""
    if zoom == "in":
        vf = ("scale=1404:-2,"
              f"crop=1080:1920:x='(in_w-1080)/2 - (in_w-1080)/2*0.15*(t/{dur})':y='(in_h-1920)/2',"
              "format=yuv420p")
    else:
        vf = ("scale=1404:-2,"
              f"crop=1080:1920:x='(in_w-1080)/2 + (in_w-1080)/2*0.15*(t/{dur})':y='(in_h-1920)/2',"
              "format=yuv420p")
    subprocess.run([
        "ffmpeg", "-y", "-loop", "1", "-framerate", "24", "-t", f"{dur:.3f}",
        "-i", str(img_path), "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "21",
        "-pix_fmt", "yuv420p", "-r", "24", str(out_path)
    ], capture_output=True, text=True, check=True)


def generate_srt(beats_audio, out_path, chunk_size=4):
    """Proportional SRT — edge-tts 7.x WordBoundary is broken."""
    entries, idx, cumulative = [], 1, 0.0
    for i, text, path, dur in beats_audio:
        words = text.split()
        chunks = [" ".join(words[j:j+chunk_size]) for j in range(0, len(words), chunk_size)]
        total_chars = sum(len(c) for c in chunks)
        offset = cumulative
        for chunk in chunks:
            chunk_dur = dur * (len(chunk) / total_chars)
            entries.append((idx, offset, offset + chunk_dur, chunk))
            offset += chunk_dur; idx += 1
        cumulative += dur
    with open(out_path, "w") as f:
        for idx, start, end, text in entries:
            f.write(f"{idx}\n{fmt_time(start)} --> {fmt_time(end)}\n{text}\n\n")


def srt_to_ass_proper(srt_path, ass_path):
    """SRT→ASS with PlayResY=1920 so FontSize is real pixels (not scaled 6.67x)."""
    subprocess.run(["ffmpeg", "-y", "-i", srt_path, ass_path],
                   capture_output=True, text=True, check=True)
    with open(ass_path) as f:
        lines = f.readlines()
    events, in_events = [], False
    for line in lines:
        if line.strip().startswith("[Events]"):
            in_events = True
        if in_events:
            events.append(line)
    header = """[Script Info]
Title: Subs
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes
WrapStyle: 2
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,42,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,3,0,2,40,40,60,1

"""
    with open(ass_path, "w") as f:
        f.write(header)
        for line in events:
            f.write(line)


def build_clip(clip_id):
    cfg = CLIPS[clip_id]
    print(f"\n{'='*60}\n  CLIP {clip_id} — {cfg['name']}\n{'='*60}")
    clip_dir = TMP_DIR / f"clip{clip_id}"; clip_dir.mkdir(exist_ok=True)
    audio_dir, img_dir, seg_dir = (clip_dir / s for s in ("audio", "img", "segments"))
    for d in (audio_dir, img_dir, seg_dir): d.mkdir(exist_ok=True)

    print("\n[1/5] Voix edge-tts...")
    beats_audio = asyncio.run(gen_tts(cfg["beats"], audio_dir))
    print(f"   Total: {sum(b[3] for b in beats_audio):.1f}s")

    print("\n[2/5] Capture slides...")
    slide_names = []
    for sn, _ in cfg["beats"]:
        if sn not in slide_names: slide_names.append(sn)
    captured = capture_slides(slide_names, img_dir)

    print("\n[3/5] Segments vidéo (Ken Burns)...")
    seg_paths = []
    for i, (slide_name, _) in enumerate(cfg["beats"]):
        img_path = captured.get(slide_name)
        if not img_path: continue
        zoom = "in" if i % 2 == 0 else "out"
        seg_path = seg_dir / f"seg_{i:02d}.mp4"
        build_video_segment(img_path, beats_audio[i][3], seg_path, zoom=zoom)
        seg_paths.append(seg_path)

    print("\n[4/5] Concat vidéo + audio...")
    cl = clip_dir / "concat.txt"
    cl.write_text("".join(f"file '{p.resolve()}'\n" for p in seg_paths))
    vc = clip_dir / "video.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(cl),
                    "-c", "copy", str(vc)], capture_output=True, text=True, check=True)
    al = clip_dir / "audio_concat.txt"
    al.write_text("".join(f"file '{p.resolve()}'\n" for _, _, p, _ in beats_audio))
    af = clip_dir / "audio_full.mp3"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(al),
                    "-c", "copy", str(af)], capture_output=True, text=True, check=True)
    va = clip_dir / "video_audio.mp4"
    subprocess.run(["ffmpeg", "-y", "-i", str(vc), "-i", str(af),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                    "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p",
                    "-r", "24", "-shortest", str(va)], capture_output=True, text=True, check=True)

    print("\n[5/6] Subs + BGM (sur le body, pas sur intro/signature)...")
    srt_path, ass_path = clip_dir / "subs.srt", clip_dir / "subs.ass"
    generate_srt(beats_audio, str(srt_path))
    srt_to_ass_proper(str(srt_path), str(ass_path))
    body_final = clip_dir / "body_final.mp4"   # intermédiaire — sans intro/signature
    dur = get_dur(str(va))
    ass_esc = str(ass_path).replace("/", "\\/").replace(":", "\\:")
    if os.path.exists(BGM_PATH):
        cmd = ["ffmpeg", "-y", "-i", str(va), "-i", BGM_PATH,
               "-vf", f"subtitles='{ass_esc}'",
               "-filter_complex",
               f"[1:a]volume=-24dB,afade=t=in:st=0:d=1,afade=t=out:st={dur-1.5}:d=1.5[bgm];"
               f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=0[aout]",
               "-map", "0:v", "-map", "[aout]",
               "-c:v", "libx264", "-preset", "medium", "-crf", "20",
               "-c:a", "aac", "-b:a", "192k", "-shortest", str(body_final)]
    else:
        cmd = ["ffmpeg", "-y", "-i", str(va), "-vf", f"subtitles='{ass_esc}'",
               "-c:v", "libx264", "-preset", "medium", "-crf", "20",
               "-c:a", "aac", "-b:a", "192k", str(body_final)]
    subprocess.run(cmd, capture_output=True, text=True, check=True)

    # --- [6/6] Prépend INTRO + append SIGNATURE ---
    # IMPORTANT: utiliser filter_complex (PAS le demuxer concat). L'audio AAC de
    # l'intro peut contenir des frames défectueuses qui font échouer le demuxer
    # concat (exit 234, "NaN/+Inf", "Invalid data"). filter_complex re-encode
    # proprement et normalise codecs/resolution/fps/sample_rate.
    print(f"\n[6/6] Ajout intro ({INTRO_PATH.name}) + signature ({SIGNATURE_PATH.name})...")
    out_path = CLIPS_DIR / f"clip{clip_id}_FINAL.mp4"
    if INTRO_PATH.exists() and SIGNATURE_PATH.exists():
        r = subprocess.run([
            "ffmpeg", "-y",
            "-i", str(INTRO_PATH), "-i", str(body_final), "-i", str(SIGNATURE_PATH),
            "-filter_complex",
            # Normaliser chaque segment v+a (scale 1080x1920 + pad navy + fps 24 + audio stéréo 44100)
            "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
            "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=#04102B,setsar=1,fps=24[v0];"
            "[0:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo[a0];"
            "[1:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
            "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=#04102B,setsar=1,fps=24[v1];"
            "[1:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo[a1];"
            "[2:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
            "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=#04102B,setsar=1,fps=24[v2];"
            "[2:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo[a2];"
            "[v0][a0][v1][a1][v2][a2]concat=n=3:v=1:a=1[v][a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p", "-r", "24",
            str(out_path)
        ], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"   FFmpeg err: {r.stderr[-1500:]}")
            raise RuntimeError("final concat failed")
    else:
        import shutil
        shutil.copy2(body_final, out_path)
        print("   ⚠️ Intro/signature manquants — body seul copié")

    size = os.path.getsize(out_path) / (1024*1024)
    print(f"\n✅ CLIP {clip_id}: {out_path}\n   {get_dur(str(out_path)):.1f}s | {size:.1f} MB")
    return out_path


if __name__ == "__main__":
    todo = sys.argv[1:] if len(sys.argv) > 1 else ["all"]
    if "all" in todo: todo = list(CLIPS)
    for cid in todo:
        if cid not in CLIPS:
            print(f"Inconnu: {cid}. Disponibles: {list(CLIPS)}"); continue
        build_clip(cid)
