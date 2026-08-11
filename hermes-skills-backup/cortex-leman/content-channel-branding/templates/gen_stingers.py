#!/usr/bin/env python3
"""Synthétise 4 signatures audio pour une chaîne (stingers d'intro/outro).
Instruments: Kora, Kalimba, Balafon, Djembe+Kora
Chaque stinger ~2.5s, 44100Hz, stéréo.

Utilisation:
    python3 gen_stingers.py

Dépendances: numpy uniquement (stdlib wave pour WAV, ffmpeg pour MP3).
Voir references/audio-stinger-synthesis.md pour la théorie complète.

PATTERN MÉLODIQUE: utiliser des gammes pentatoniques.
- Ascendant = intro/révélation (hopeful)
- Descendant+resolve = outro/conclusion (warm)
- Arpège 1-3-5-8 = cinématique
"""
import numpy as np
import wave
from pathlib import Path
import subprocess

OUT = Path("./stingers")  # Ajuster selon le projet
OUT.mkdir(parents=True, exist_ok=True)

SR = 44100
DURATION = 2.5
N = int(SR * DURATION)


def wavfile_write(path, sr, data):
    """Write WAV without scipy — stdlib only."""
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
    """Karplus-Strong string synthesis — kora, kalimba, n'goni."""
    n = int(dur * sr)
    buf_len = max(int(sr / freq), 2)
    buf = np.random.uniform(-1, 1, buf_len)
    out = np.zeros(n)
    for i in range(n):
        buf[i % buf_len] = decay * 0.5 * (buf[i % buf_len] + buf[(i + 1) % buf_len])
        out[i] = buf[i % buf_len]
    return out


def note(freq, start, dur, waveform='ks', decay=0.996, gain=0.3):
    """Place a note at time `start` with frequency `freq`."""
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
                 0.3*np.sin(2*np.pi*freq*3*tt) * np.exp(-tt*5))
        audio /= 3
    audio *= envelope(n_note, attack=0.005, release=0.5) * gain
    out = np.zeros(N)
    start_sample = int(start * SR)
    end_sample = min(start_sample + n_note, N)
    out[start_sample:end_sample] = audio[:end_sample - start_sample]
    return out


def add_djembe_hit(start, freq=80, dur=0.4, gain=0.5):
    """Synthetic djembe hit: low sine + noise burst."""
    n_hit = int(dur * SR)
    tt = np.arange(n_hit) / SR
    tone = np.sin(2 * np.pi * freq * tt) * np.exp(-tt * 8)
    noise = np.random.uniform(-1, 1, n_hit) * np.exp(-tt * 30) * 0.3
    hit = (tone + noise) * gain
    out = np.zeros(N)
    s = int(start * SR)
    e = min(s + n_hit, N)
    out[s:e] = hit[:e - s]
    return out


def mix(*tracks):
    """Mix multiple tracks + soft clip."""
    result = np.zeros(N)
    for tr in tracks:
        result += tr
    return np.tanh(result * 0.8) * 0.7


def to_stereo(mono):
    """Haas stereo widening."""
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


# ═══════════════════════════════════════════════════
# STINGERS — ajuster les notes selon la palette émotionnelle
# Gamme pentatonique de Do: C(261.63) D(293.66) E(329.63) G(392.00) A(440.00) C(523.25)
# ═══════════════════════════════════════════════════

# 1. KORA — ascendant pentatonique (révélation)
print("Synthèse 1/4: Kora...")
kora_notes = [
    (261.63, 0.0, 1.2), (293.66, 0.15, 1.1), (329.63, 0.3, 1.0),
    (392.00, 0.5, 1.0), (440.00, 0.7, 1.2), (523.25, 1.0, 1.5),
]
save("stinger_kora", mix(*[note(f, s, d, 'ks', 0.997, 0.2) for f, s, d in kora_notes]))

# 2. KALIMBA — descendant + résolution (warm)
print("Synthèse 2/4: Kalimba...")
kalimba_notes = [
    (523.25, 0.0, 0.6), (440.00, 0.12, 0.6), (392.00, 0.24, 0.7),
    (329.63, 0.36, 0.8), (261.63, 0.5, 1.5), (523.25, 0.7, 1.0),
]
save("stinger_kalimba", mix(*[note(f, s, d, 'ks', 0.990, 0.25) for f, s, d in kalimba_notes]))

# 3. BALAFON — arpège ascendant cinématique
print("Synthèse 3/4: Balafon...")
balafon_notes = [
    (261.63, 0.0, 0.5), (329.63, 0.1, 0.5), (392.00, 0.2, 0.5),
    (523.25, 0.3, 1.8), (659.25, 0.5, 1.2),
]
save("stinger_balafon", mix(*[note(f, s, d, 'bell', gain=0.2) for f, s, d in balafon_notes]))

# 4. DJEMBE + KORA — tribal cinématique
print("Synthèse 4/4: Djembe+Kora...")
tribal = mix(
    add_djembe_hit(0.0, 70, 0.5, 0.4),
    add_djembe_hit(0.3, 85, 0.4, 0.35),
    add_djembe_hit(0.6, 70, 0.6, 0.3),
    note(392.00, 0.5, 1.5, 'ks', 0.996, 0.15),
    note(523.25, 0.8, 1.2, 'ks', 0.996, 0.15),
)
save("stinger_djembe_kora", tribal)

print(f"\n🎉 4 stingers générés dans {OUT}")
