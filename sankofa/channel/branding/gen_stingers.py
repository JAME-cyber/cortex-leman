#!/usr/bin/env python3
"""Synthétise 4 signatures audio africaines pour Sankofa.
Instruments: Kora, Kalimba, Balafon, Djembe+Voix
Chaque stinger ~2.5s, 44100Hz, stéréo.
"""
import numpy as np
import wave
from pathlib import Path
import subprocess

OUT = Path("/home/tars/african-heroes/CHANNEL/branding/stingers")
OUT.mkdir(parents=True, exist_ok=True)

def wavfile_write(path, sr, data):
    """Write WAV without scipy."""
    audio_int = np.clip(data * 32767, -32768, 32767).astype(np.int16)
    with wave.open(str(path), 'w') as w:
        w.setnchannels(2 if data.ndim > 1 else 1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(audio_int.tobytes())

SR = 44100
DURATION = 2.5
N = int(SR * DURATION)
t = np.arange(N) / SR

def envelope(n, attack=0.01, release=0.3):
    """ADSR-ish envelope for a note."""
    env = np.ones(n)
    a = int(attack * n)
    r = int(release * n)
    if a > 0:
        env[:a] = np.linspace(0, 1, a)
    if r > 0:
        env[-r:] = np.exp(-np.linspace(0, 4, r))
    return env

def karplus_strong(freq, dur, decay=0.996, sr=44100):
    """Karplus-Strong string synthesis — good for kora/kalimba."""
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
    elif waveform == 'tri':
        tt = np.arange(n_note) / SR
        audio = 2 * np.abs(2 * (freq * tt - np.floor(freq * tt + 0.5))) - 1
    elif waveform == 'bell':
        # FM-ish bell: sine + harmonics with fast decay
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

def mix(*tracks):
    """Mix multiple tracks together."""
    result = np.zeros(N)
    for tr in tracks:
        result += tr
    # Soft clip
    result = np.tanh(result * 0.8) * 0.7
    return result

def add_djembe_hit(start, freq=80, dur=0.4, gain=0.5):
    """Synthetic djembe hit: low sine + noise burst."""
    n_hit = int(dur * SR)
    tt = np.arange(n_hit) / SR
    # Low tone
    tone = np.sin(2 * np.pi * freq * tt) * np.exp(-tt * 8)
    # Noise burst (skin slap)
    noise = np.random.uniform(-1, 1, n_hit) * np.exp(-tt * 30) * 0.3
    hit = (tone + noise) * gain
    out = np.zeros(N)
    s = int(start * SR)
    e = min(s + n_hit, N)
    out[s:e] = hit[:e - s]
    return out

def to_stereo(mono):
    """Slight stereo widening."""
    delay = 15  # samples
    left = mono
    right = np.zeros_like(mono)
    right[delay:] = mono[:-delay]
    return np.column_stack([left, right])

def save(name, audio):
    """Save as WAV then convert to MP3."""
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

# ─── Stinger 1: KORA (harpe mandingue) ───
print("Synthèse 1/4: Kora...")
# Pentatonic ascending: C4, D4, E4, G4, A4, C5
# Kora-like: bright, resonant, long decay
kora_notes = [
    (261.63, 0.0, 1.2),   # C4
    (293.66, 0.15, 1.1),  # D4
    (329.63, 0.3, 1.0),   # E4
    (392.00, 0.5, 1.0),   # G4
    (440.00, 0.7, 1.2),   # A4
    (523.25, 1.0, 1.5),   # C5 (sustained)
]
tracks = []
for freq, start, dur in kora_notes:
    tracks.append(note(freq, start, dur, waveform='ks', decay=0.997, gain=0.2))
kora = mix(*tracks)
save("stinger_kora", kora)

# ─── Stinger 2: KALIMBA (piano à pouce) ───
print("Synthèse 2/4: Kalimba...")
# Kalimba: short, warm, woody. Pentatonic descending then resolve.
# Notes: A4, G4, E4, C4, A4 (resolve)
kalimba_notes = [
    (523.25, 0.0, 0.6),   # C5
    (440.00, 0.12, 0.6),  # A4
    (392.00, 0.24, 0.7),  # G4
    (329.63, 0.36, 0.8),  # E4
    (261.63, 0.5, 1.5),   # C4 (resolve, sustained)
    (523.25, 0.7, 1.0),   # C5 (echo)
]
tracks = []
for freq, start, dur in kalimba_notes:
    tracks.append(note(freq, start, dur, waveform='ks', decay=0.99, gain=0.25))
kalimba = mix(*tracks)
save("stinger_kalimba", kalimba)

# ─── Stinger 3: BALAFON (xylophone africain) ───
print("Synthèse 3/4: Balafon...")
# Balafon: woody marimba-like, bell harmonics, resonant.
# Ascending triad pattern: C4-E4-G4-C5 then sustain.
balafon_notes = [
    (261.63, 0.0, 0.5),   # C4
    (329.63, 0.1, 0.5),   # E4
    (392.00, 0.2, 0.5),   # G4
    (523.25, 0.3, 1.8),   # C5 (long sustain)
    (659.25, 0.5, 1.2),   # E5 (harmonic shimmer)
]
tracks = []
for freq, start, dur in balafon_notes:
    tracks.append(note(freq, start, dur, waveform='bell', gain=0.2))
balafon = mix(*tracks)
save("stinger_balafon", balafon)

# ─── Stinger 4: DJEMBE + KORA (tribal) ───
print("Synthèse 4/4: Djembe+Kora...")
# Two djembe hits + kora melody = cinematic tribal feel.
djembe1 = add_djembe_hit(0.0, freq=70, dur=0.5, gain=0.4)
djembe2 = add_djembe_hit(0.3, freq=85, dur=0.4, gain=0.35)
djembe3 = add_djembe_hit(0.6, freq=70, dur=0.6, gain=0.3)
kora_overlay = note(392.00, 0.5, 1.5, waveform='ks', decay=0.996, gain=0.15) + \
               note(523.25, 0.8, 1.2, waveform='ks', decay=0.996, gain=0.15)
tribal = mix(djembe1, djembe2, djembe3, kora_overlay)
save("stinger_djembe_kora", tribal)

print("\n🎉 4 stingers générés dans", OUT)
