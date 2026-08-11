#!/usr/bin/env python3
"""Synthétise 3 signatures audio "warm/organic" pour marques familiales/culinaire/communauté.
Instruments & textures: Marimba + Sizzle, Dinner bell + Kalimba, Wind chimes + Pad
Chaque stinger ~2.0s, 44100Hz, stéréo.

Utilisation:
    python3 gen_stingers_warm.py

Dépendances: numpy uniquement (stdlib wave pour WAV, ffmpeg pour MP3).
Voir references/audio-stinger-synthesis.md pour la théorie complète.

PATTERN MÉLODIQUE: gammes MAJEURES (joyful, warm, inviting).
Contraire de gen_stingers.py qui utilise pentatonique (mystical, epic).
Choisir la famille selon la personnalité de la marque:
  - gen_stingers.py     → histoire, heritage, dramatique, épique
  - gen_stingers_warm.py → famille, cuisine, communauté, ludique, accueillant
"""
import numpy as np
import wave
from pathlib import Path
import subprocess

OUT = Path("./stingers")  # Ajuster selon le projet
OUT.mkdir(parents=True, exist_ok=True)

SR = 44100
DURATION = 2.0
N = int(SR * DURATION)


def wavfile_write(path, sr, data):
    audio_int = np.clip(data * 32767, -32768, 32767).astype(np.int16)
    with wave.open(str(path), 'w') as w:
        w.setnchannels(2 if data.ndim > 1 else 1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(audio_int.tobytes())


def envelope(n, attack=0.01, release=0.3):
    env = np.ones(n)
    a = int(attack * n)
    r = int(release * n)
    if a > 0:
        env[:a] = np.linspace(0, 1, a)
    if r > 0:
        env[-r:] = np.exp(-np.linspace(0, 4, r))
    return env


def karplus_strong(freq, dur, decay=0.996, sr=44100):
    n = int(dur * sr)
    buf_len = max(int(sr / freq), 2)
    buf = np.random.uniform(-1, 1, buf_len)
    out = np.zeros(n)
    for i in range(n):
        buf[i % buf_len] = decay * 0.5 * (buf[i % buf_len] + buf[(i + 1) % buf_len])
        out[i] = buf[i % buf_len]
    return out


def note(freq, start, dur, waveform='ks', decay=0.996, gain=0.3):
    n_note = int(dur * SR)
    if waveform == 'ks':
        audio = karplus_strong(freq, dur, decay)
    elif waveform == 'sine':
        tt = np.arange(n_note) / SR
        audio = np.sin(2 * np.pi * freq * tt)
    elif waveform == 'bell':
        tt = np.arange(n_note) / SR
        audio = (np.sin(2*np.pi*freq*tt) +
                 0.5*np.sin(2*np.pi*freq*2*tt) * np.exp(-tt*3) +
                 0.3*np.sin(2*np.pi*freq*3*tt) * np.exp(-tt*5) +
                 0.2*np.sin(2*np.pi*freq*4.2*tt) * np.exp(-tt*7))
        audio /= 4
    elif waveform == 'marimba':
        audio = karplus_strong(freq, dur, decay)
        tt = np.arange(n_note) / SR
        audio *= 1 + 0.003 * np.sin(2 * np.pi * 5 * tt)  # vibrato
    elif waveform == 'pluck':
        tt = np.arange(n_note) / SR
        audio = (np.sin(2*np.pi*freq*tt) +
                 0.4*np.sin(2*np.pi*freq*2*tt) +
                 0.2*np.sin(2*np.pi*freq*3*tt))
        audio *= np.exp(-tt * 4) / 1.6
    audio *= envelope(n_note, attack=0.003, release=0.5) * gain
    out = np.zeros(N)
    start_sample = int(start * SR)
    end_sample = min(start_sample + n_note, N)
    out[start_sample:end_sample] = audio[:end_sample - start_sample]
    return out


def mix(*tracks):
    result = np.zeros(N)
    for tr in tracks:
        result += tr
    return np.tanh(result * 0.8) * 0.7


def to_stereo(mono):
    delay = 15
    left = mono
    right = np.zeros_like(mono)
    right[delay:] = mono[:-delay]
    return np.column_stack([left, right])


def save(name, audio):
    wav_path = OUT / f"{name}.wav"
    audio_stereo = to_stereo(audio) if audio.ndim == 1 else audio
    wavfile_write(wav_path, SR, audio_stereo)
    mp3_path = OUT / f"{name}.mp3"
    subprocess.run([
        "ffmpeg", "-y", "-i", str(wav_path),
        "-codec:a", "libmp3lame", "-b:a", "192k",
        str(mp3_path)
    ], capture_output=True)
    print(f"  ✅ {name}.mp3 ({mp3_path.stat().st_size // 1024} KB)")


def sizzle(start, dur, gain=0.08):
    """Crisp cooking sizzle: filtered noise with random crackles."""
    n_siz = int(dur * SR)
    noise = np.random.uniform(-1, 1, n_siz)
    lp = np.convolve(noise, np.ones(50)/50, mode='same')
    crackles = np.zeros(n_siz)
    for _ in range(int(dur * 15)):
        pos = np.random.randint(0, n_siz)
        crackle_len = np.random.randint(20, 100)
        end = min(pos + crackle_len, n_siz)
        crackles[pos:end] += np.exp(-np.arange(crackle_len)[:end-pos] / 20) * np.random.uniform(0.5, 1)
    audio = (lp * 0.6 + crackles * 0.4) * gain
    fade_in = int(0.1 * n_siz)
    fade_out = int(0.3 * n_siz)
    audio[:fade_in] *= np.linspace(0, 1, fade_in)
    audio[-fade_out:] *= np.linspace(1, 0, fade_out)
    out = np.zeros(N)
    s = int(start * SR)
    e = min(s + n_siz, N)
    out[s:e] = audio[:e - s]
    return out


def soft_clap(start, gain=0.15):
    """Soft hand clap — like children clapping."""
    n_clap = int(0.1 * SR)
    noise = np.random.uniform(-1, 1, n_clap)
    env = np.exp(-np.arange(n_clap) / (0.02 * SR))
    audio = noise * env * gain
    out = np.zeros(N)
    s = int(start * SR)
    e = min(s + n_clap, N)
    out[s:e] = audio[:e - s]
    return out


def wind_chime(start, freq, dur=0.8, gain=0.12):
    """Wind chime / spice jar shake — bell-like with shimmer."""
    n_ch = int(dur * SR)
    tt = np.arange(n_ch) / SR
    audio = (np.sin(2*np.pi*freq*tt) +
             0.6*np.sin(2*np.pi*freq*1.5*tt) * np.exp(-tt*2) +
             0.4*np.sin(2*np.pi*freq*2.1*tt) * np.exp(-tt*3))
    audio *= np.exp(-tt * 1.5) * gain / 2
    out = np.zeros(N)
    s = int(start * SR)
    e = min(s + n_ch, N)
    out[s:e] = audio[:e - s]
    return out


# ═══════════════════════════════════════════════════
# STINGERS WARM/ORGANIC — gammes MAJEURES
# Gamme de Do majeur: C(261.63) D(293.66) E(329.63) F(349.23) G(392.00) A(440.00) B(493.88) C(523.25)
# ═══════════════════════════════════════════════════

# 1. SIZZLE WARM — Marimba chaleureuse + crépitement de cuisson
# Idéal: cuisine, gastronomie, ateliers culinaires
print("Synthèse 1/3: Sizzle Warm...")
C4 = 261.63; E4 = 329.63; G4 = 392.00; C5 = 523.25; E5 = 659.25
save("stinger_sizzle_warm", mix(
    note(C4, 0.0, 0.5, waveform='marimba', decay=0.99, gain=0.22),
    note(E4, 0.08, 0.5, waveform='marimba', decay=0.99, gain=0.22),
    note(G4, 0.16, 0.5, waveform='marimba', decay=0.99, gain=0.22),
    note(C5, 0.24, 0.8, waveform='marimba', decay=0.995, gain=0.25),
    note(E5, 0.4, 1.2, waveform='bell', gain=0.15),
    note(G4, 0.6, 0.8, waveform='marimba', decay=0.99, gain=0.12),
    note(C5, 0.72, 1.0, waveform='bell', gain=0.1),
    sizzle(0.0, 1.8, gain=0.04),
))

# 2. MARKET BELL — Dinner bell + kalimba ascendante + claps
# Idéal: enfants, familles, école, communauté
print("Synthèse 2/3: Market Bell...")
D4 = 293.66; G5 = 783.99
save("stinger_market_bell", mix(
    note(G5, 0.0, 1.5, waveform='bell', gain=0.15),
    note(C5, 0.0, 1.5, waveform='bell', gain=0.12),
    note(C4, 0.2, 0.4, waveform='ks', decay=0.988, gain=0.2),
    note(D4, 0.3, 0.4, waveform='ks', decay=0.988, gain=0.2),
    note(E4, 0.4, 0.4, waveform='ks', decay=0.988, gain=0.2),
    note(G4, 0.5, 0.6, waveform='ks', decay=0.99, gain=0.22),
    note(C5, 0.65, 1.2, waveform='ks', decay=0.996, gain=0.18),
    soft_clap(0.2, gain=0.08),
    soft_clap(0.25, gain=0.06),
))

# 3. SPICE WIND — Carillon éolien + pad chaleureux
# Idéal: onirique, épiceries, épices, produits artisanaux
print("Synthèse 3/3: Spice Wind...")
save("stinger_spice_wind", mix(
    wind_chime(0.0, E5, dur=0.8, gain=0.1),
    wind_chime(0.05, G5, dur=0.7, gain=0.08),
    wind_chime(0.12, C5, dur=0.9, gain=0.12),
    wind_chime(0.2, A4, dur=0.6, gain=0.08),
    wind_chime(0.28, E5, dur=0.7, gain=0.1),
    wind_chime(0.35, G5, dur=0.8, gain=0.08),
    note(C4, 0.0, 2.0, waveform='sine', gain=0.08),
    note(G4, 0.0, 2.0, waveform='sine', gain=0.06),
    note(C5, 0.5, 1.2, waveform='bell', gain=0.15),
    note(E5, 0.65, 1.0, waveform='bell', gain=0.1),
))

print(f"\n🎉 3 stingers warm générés dans {OUT}")
