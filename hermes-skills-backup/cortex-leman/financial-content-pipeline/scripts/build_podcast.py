#!/usr/bin/env python3
"""Podcast 2-voix (HOTE + ANALYSTE) via edge-tts + BGM + mix ffmpeg.

Usage:
    python build_podcast.py path/to/script.md [output.mp3]

Le script Markdown doit contenir des lignes **[HOST]** et **[CLAIRE]**.
Le disclaimer AMF doit être intégré dans le script (lu par HOST en intro).
"""
import os, re, sys, asyncio, subprocess
from pathlib import Path
import edge_tts

# --- Config ---
VOICE_HOST = "fr-FR-HenriNeural"
VOICE_CLAIRE = "fr-FR-DeniseNeural"
RATE = "+5%"  # plus posé que les clips Shorts
BGM_PATH = "/home/tars/crypto-project/audio/bgm_stellardrone.mp3"
BGM_DUCK = 0.08  # ~-22 dB

def parse_script(text):
    """Extrait les répliques [HOST] et [CLAIRE] du markdown."""
    lines = []
    current_speaker = None
    current_text = []
    for line in text.splitlines():
        m = re.match(r'\*\*\[(HOST|CLAIRE)\]\*\*\s*(.*)', line.strip())
        if m:
            if current_speaker and current_text:
                lines.append((current_speaker, " ".join(current_text)))
            current_speaker = m.group(1)
            current_text = [m.group(2)] if m.group(2) else []
        elif current_speaker and line.strip() and not line.strip().startswith(('#','---','**','[')):
            current_text.append(line.strip())
    if current_speaker and current_text:
        lines.append((current_speaker, " ".join(current_text)))
    return lines

async def gen_voices(lines, out_dir):
    clips = []
    for i, (spk, txt) in enumerate(lines):
        clean = re.sub(r'\*+([^*]+)\*+', r'\1', txt)
        voice = VOICE_HOST if spk == "HOST" else VOICE_CLAIRE
        path = out_dir / f"line_{i:02d}_{spk.lower()}.mp3"
        comm = edge_tts.Communicate(clean, voice, rate=RATE)
        await comm.save(str(path))
        clips.append((spk, str(path)))
        print(f"  [{i:02d}] {spk} ({voice}): {clean[:60]}...")
    return clips

def get_dur(path):
    r = subprocess.run(
        ["ffprobe","-v","quiet","-show_entries","format=duration","-of","csv=p=0", path],
        capture_output=True, text=True)
    return float(r.stdout.strip())

def assemble(clips, out_path, tmp_dir):
    # 1. Concat voice clips
    concat_list = tmp_dir / "voice_concat.txt"
    with open(concat_list, "w") as f:
        for _, p in clips:
            f.write(f"file '{os.path.abspath(p)}'\n")
    voice_full = tmp_dir / "voice_full.mp3"
    subprocess.run([
        "ffmpeg","-y","-f","concat","-safe","0","-i",str(concat_list),
        "-c","copy", str(voice_full)
    ], check=True, capture_output=True)
    voice_dur = get_dur(str(voice_full))
    print(f"\nVoix totale: {voice_dur:.1f}s")

    # 2. BGM ducked + looped
    bgm_ducked = tmp_dir / "bgm_ducked.mp3"
    subprocess.run([
        "ffmpeg","-y","-stream_loop","-1","-i",BGM_PATH,
        "-t", str(voice_dur + 2),
        "-af", f"afade=in:st=0:d=2,volume={BGM_DUCK},afade=out:t=out:st={voice_dur-2}:d=2",
        "-c:a","libmp3lame","-b:a","96k",
        str(bgm_ducked)
    ], check=True, capture_output=True)

    # 3. Mix
    subprocess.run([
        "ffmpeg","-y",
        "-i", str(voice_full),
        "-i", str(bgm_ducked),
        "-filter_complex",f"[0:a]volume=1.0[voice];[1:a]volume=1.0[bgm];"
                          "[voice][bgm]amix=inputs=2:duration=shortest:dropout_transition=0",
        "-c:a","libmp3lame","-b:a","192k",
        str(out_path)
    ], check=True, capture_output=True)

    final_dur = get_dur(str(out_path))
    size_mb = os.path.getsize(out_path) / (1024*1024)
    print(f"\n✅ Podcast: {out_path}")
    print(f"   Durée: {final_dur:.1f}s ({final_dur/60:.1f} min) | Taille: {size_mb:.1f} MB")

async def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: build_podcast.py <script.md> [output.mp3]")
    script_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else script_path.with_suffix(".mp3")
    tmp_dir = script_path.parent / "_podcast_tmp"
    tmp_dir.mkdir(exist_ok=True)

    text = script_path.read_text(encoding="utf-8")
    lines = parse_script(text)
    print(f"Parsed {len(lines)} lignes ({sum(1 for s,_ in lines if s=='HOST')} HOST, "
          f"{sum(1 for s,_ in lines if s=='CLAIRE')} CLAIRE)")
    print("\nGénération voix...")
    clips = await gen_voices(lines, tmp_dir)
    print("\nAssemblage...")
    assemble(clips, out_path, tmp_dir)

if __name__ == "__main__":
    asyncio.run(main())
