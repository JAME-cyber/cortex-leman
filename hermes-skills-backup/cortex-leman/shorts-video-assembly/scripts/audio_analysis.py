#!/usr/bin/env python3
"""
Audio diagnostic tool for video builds.
Detects: silent audio, buried VO (music too loud), spectral profile.

Usage:
    # Extract audio first
    ffmpeg -y -i video.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 /tmp/audio.wav
    # Then analyze
    python3 audio_analysis.py /tmp/audio.wav

Or with defaults (reads /tmp/t1_orig_audio.wav):
    python3 audio_analysis.py
"""
import sys
import wave
import numpy as np

def analyze(path):
    with wave.open(path, 'rb') as w:
        sr = w.getframerate()
        samples = np.frombuffer(
            w.readframes(w.getnframes()),
            dtype=np.int16
        ).astype(np.float32) / 32768.0
        duration = len(samples) / sr

    overall_rms = np.sqrt(np.mean(samples**2))
    overall_peak = np.max(np.abs(samples))

    print(f"Duration: {duration:.1f}s | Sample rate: {sr}")
    print(f"Overall RMS: {20*np.log10(overall_rms+1e-10):.1f} dB")
    print(f"Overall Peak: {20*np.log10(overall_peak+1e-10):.1f} dB")

    # Verdict
    if overall_rms < 0.001:
        print("\n❌ CRITICAL: Audio is essentially SILENT")
    elif 20*np.log10(overall_rms+1e-10) < -20:
        print("\n⚠️  WARNING: Audio too quiet for mobile (< -20 dB)")
    else:
        print("\n✅ Audio level OK for mobile")

    # Per-segment
    print("\n--- Per 5s segment ---")
    for start in range(0, int(duration), 5):
        end = min(start + 5, int(duration))
        seg = samples[start*sr:end*sr]
        if len(seg) == 0:
            continue
        srms = np.sqrt(np.mean(seg**2))
        speak = np.max(np.abs(seg))
        status = "SILENCE" if srms < 0.001 else ("QUIET" if srms < 0.01 else "AUDIBLE")
        print(f"  {start:3d}-{end:3d}s: RMS={20*np.log10(srms+1e-10):6.1f} dB  "
              f"Peak={20*np.log10(speak+1e-10):6.1f} dB  {status}")

    # FFT spectral analysis on middle segment
    mid_start = int(duration * 0.3)
    mid_end = min(mid_start + 5, int(duration))
    seg = samples[mid_start*sr:mid_end*sr]
    if len(seg) > 0:
        fft = np.abs(np.fft.rfft(seg))
        freqs = np.fft.rfftfreq(len(seg), 1.0/sr)

        speech_mask = (freqs > 300) & (freqs < 3400)
        speech_energy = np.sum(fft[speech_mask]**2)
        total = np.sum(fft**2)
        speech_pct = 100 * speech_energy / total if total > 0 else 0

        top_indices = np.argsort(fft)[-5:][::-1]
        top_freqs = [f"{freqs[i]:.0f}Hz" for i in top_indices]

        print(f"\n--- Spectral analysis ({mid_start}-{mid_end}s) ---")
        print(f"Speech band (300-3400Hz): {speech_pct:.1f}% of energy")
        print(f"Top 5 frequencies: {top_freqs}")

        if speech_pct < 40:
            print("⚠️  VOICE BURIED: <40% speech band = music/noise dominates")
        elif top_freqs and any(
            int(f.replace('Hz', '')) < 100 for f in top_freqs
        ):
            print("⚠️  LOW-FREQ HUM: top frequencies <100Hz suggest music "
                  "overpowering VO")
        else:
            print("✅ Spectral profile OK for voice content")

    # Recommendations
    print("\n--- Fix recommendations ---")
    db = 20*np.log10(overall_rms+1e-10)
    if db < -20:
        boost = min(20, -14 - db)
        print(f"  Apply: volume={boost:.0f}dB,alimiter=limit=0.95")
        print(f"  Target: -14 to -17 dB (broadcast mobile)")
    if speech_pct < 50:
        print("  Fix amix: normalize=0, VO volume=2.5, music volume=0.12")
        print("  See pitfall #19 in shorts-video-assembly SKILL.md")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/t1_orig_audio.wav"
    analyze(path)
