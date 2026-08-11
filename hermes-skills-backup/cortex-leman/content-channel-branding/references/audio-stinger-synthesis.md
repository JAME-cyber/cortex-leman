# Audio Stinger Synthesis (No External Samples)

Generate brand signature audio (stingers/intro music) procedurally with Python + numpy.
No API calls, no sample libraries, no licensing concerns. Output is 100% original synthesis.

## When to Use

- Channel needs a signature audio sting (1-3s) for intro/outro
- User asks for culturally-specific instruments (kora, kalimba, balafon, djembe, etc.)
- No scipy available — pure numpy + stdlib `wave` module

## Synthesis Techniques by Instrument Family

### String Instruments (Kora, Kalimba, N'goni) — Karplus-Strong

The Karplus-Strong algorithm produces remarkably convincing plucked-string tones:

```python
def karplus_strong(freq, dur, decay=0.996, sr=44100):
    n = int(dur * sr)
    buf_len = max(int(sr / freq), 2)
    buf = np.random.uniform(-1, 1, buf_len)  # Noise burst excites string
    out = np.zeros(n)
    for i in range(n):
        buf[i % buf_len] = decay * 0.5 * (buf[i % buf_len] + buf[(i+1) % buf_len])
        out[i] = buf[i % buf_len]
    return out
```

| Parameter | Kora | Kalimba | Effect |
|-----------|------|---------|--------|
| decay | 0.997 | 0.990 | Higher = longer sustain (kora resonates) |
| gain | 0.20 | 0.25 | Kalimba louder (shorter = needs more presence) |

### Percussion (Djembe, Talking Drum) — Sine + Noise Burst

```python
def djembe_hit(freq, dur, gain=0.4):
    tt = np.arange(int(dur * sr)) / sr
    tone = np.sin(2*np.pi*freq*tt) * np.exp(-tt * 8)      # Low body resonance
    noise = np.random.uniform(-1, 1, len(tt)) * np.exp(-tt * 30) * 0.3  # Skin slap
    return (tone + noise) * gain
```

| Drum type | freq | dur | Character |
|-----------|------|-----|-----------|
| Bass tone | 70-80 Hz | 0.5s | Deep, resonant |
| Tone/slap | 85-120 Hz | 0.3-0.4s | Sharper, articulate |

### Wooden/Metal Keys (Balafon, Marimba) — Additive Bell Synthesis

```python
def bell_note(freq, dur):
    tt = np.arange(int(dur * sr)) / sr
    audio = (np.sin(2*np.pi*freq*tt) +
             0.5*np.sin(2*np.pi*freq*2*tt) * np.exp(-tt*3) +
             0.3*np.sin(2*np.pi*freq*3*tt) * np.exp(-tt*5))
    return audio / 3  # Normalize
```

The fast-decaying harmonics give the woody/metallic character.

## Scale Choice — Emotional Palette

The scale you choose IS the emotional signature. Match it to the brand personality:

| Scale | Character | Example brands | Good for |
|-------|-----------|---------------|----------|
| **Pentatonic minor** (C, Eb, F, G, Bb) | Mystical, ancient, epic | Sankofa (history) | Heritage, narrative, dramatic |
| **Major (ionian)** (C, D, E, F, G, A, B) | Joyful, warm, inviting | Culture en Saveurs (cooking) | Family, food, community, playful |
| **Pentatonic major** (C, D, E, G, A) | Hopeful, open | Crypto/finance intros | Reveals, optimism, growth |

**Rule:** Don't default to pentatonic minor for every African-themed project. A cooking workshop for children needs major-scale warmth, not mystical tension.

## Melodic Patterns

### Pentatonic (traditional African instruments)

```
C Major Pentatonic: C(261.63), D(293.66), E(329.63), G(392.00), A(440.00), C(523.25)
```

| Pattern | Character | Good for |
|--------|-----------|----------|
| Ascending | Hopeful, revealing | Intro openers, logo reveals |
| Descending + resolve | Warm, concluding | Outros, sign-offs |
| Arpeggio (1-3-5-8) | Majestic | Cinematic stings |
| Echo (note + higher repeat) | Reflective, call-response | Narrative channels |

### Major arpeggio (warm/inviting)

```
C Major: C(261.63), E(329.63), G(392.00), C(523.25) → triad ascending
```

Use for family-friendly, food, community brands. The major third (E) is the "warm" interval.

## Texture Synthesis — Beyond Instruments

Brand signatures can include non-musical textures that evoke the brand's domain. These are layered under or mixed with melodic elements.

### Sizzle (cooking oil crackling)

Filtered white noise + random crackle pops. Evokes cooking, kitchen, food preparation.

```python
def sizzle(start, dur, gain=0.08):
    n_siz = int(dur * sr)
    noise = np.random.uniform(-1, 1, n_siz)
    lp = np.convolve(noise, np.ones(50)/50, mode='same')  # Low-pass
    crackles = np.zeros(n_siz)
    for _ in range(int(dur * 15)):  # ~15 crackles/sec
        pos = np.random.randint(0, n_siz)
        crackle_len = np.random.randint(20, 100)
        crackles[pos:pos+crackle_len] += np.exp(-np.arange(crackle_len) / 20)
    audio = (lp * 0.6 + crackles * 0.4) * gain
    # Fade in/out
    audio[:int(0.1*n_siz)] *= np.linspace(0, 1, int(0.1*n_siz))
    audio[-int(0.3*n_siz):] *= np.linspace(1, 0, int(0.3*n_siz))
    return audio
```

### Soft clap (children clapping)

Short noise burst with fast exponential decay. Playful, human, family-friendly.

```python
def soft_clap(start, gain=0.15):
    n_clap = int(0.1 * sr)
    noise = np.random.uniform(-1, 1, n_clap)
    env = np.exp(-np.arange(n_clap) / (0.02 * sr))
    return noise * env * gain
```

### Wind chime (spice jar shimmer)

Bell-like with inharmonic partials. Evokes sprinkling, lightness, airiness.

```python
def wind_chime(start, freq, dur=0.8, gain=0.12):
    tt = np.arange(int(dur * sr)) / sr
    audio = (np.sin(2*np.pi*freq*tt) +
             0.6*np.sin(2*np.pi*freq*1.5*tt) * np.exp(-tt*2) +  # inharmonic
             0.4*np.sin(2*np.pi*freq*2.1*tt) * np.exp(-tt*3))
    return audio * np.exp(-tt * 1.5) * gain / 2
```

### Marimba (warm woody)

KS with faster decay + slight vibrato for organic feel. Richer than plain KS.

```python
def marimba_note(freq, dur, decay=0.99, sr=44100):
    audio = karplus_strong(freq, dur, decay, sr)
    tt = np.arange(len(audio)) / sr
    audio *= 1 + 0.003 * np.sin(2 * np.pi * 5 * tt)  # subtle vibrato
    return audio
```

## Envelope (ADSR)

Every note needs an envelope to sound natural:

```python
def envelope(n, attack=0.005, release=0.5):
    env = np.ones(n)
    a = int(attack * n)
    r = int(release * n)
    if a > 0: env[:a] = np.linspace(0, 1, a)       # Attack (pluck onset)
    if r > 0: env[-r:] = np.exp(-np.linspace(0, 4, r))  # Exponential decay
    return env
```

## Output Pipeline

1. Mix all notes: `result = np.zeros(N); for track in tracks: result += track`
2. Soft clip to prevent distortion: `result = np.tanh(result * 0.8) * 0.7`
3. Stereo widening (Haas effect, 15-sample delay): `right[delay:] = left[:-delay]`
4. Write WAV via stdlib `wave` (no scipy needed)
5. Convert to MP3: `ffmpeg -i in.wav -codec:a libmp3lame -b:a 192k out.mp3`
6. For Telegram delivery, convert to OGG: `ffmpeg -i in.mp3 -c:a libopus -b:a 64k out.ogg`

## WAV Writing (stdlib only, no scipy)

```python
import wave
def wavfile_write(path, sr, data):
    audio_int = np.clip(data * 32767, -32768, 32767).astype(np.int16)
    with wave.open(str(path), 'w') as w:
        w.setnchannels(2 if data.ndim > 1 else 1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(audio_int.tobytes())
```

## Reference Implementation

See `templates/gen_stingers.py` for the full working script that produced:
- `stinger_kora.mp3` — ascending pentatonic, KS decay 0.997
- `stinger_kalimba.mp3` — descending + resolve, KS decay 0.990
- `stinger_balafon.mp3` — ascending arpeggio, bell synthesis
- `stinger_djembe_kora.mp3` — 3 djembe hits + kora melody overlay

All ~2.5s, 44100Hz stereo, ~60KB each as MP3.

## Base64 Embedding for Logo in Animated Intro

When embedding a PNG logo into an HTML/SVG animated intro captured by Playwright:

| Format | Size (500×500) | Quality | Recommendation |
|--------|----------------|---------|----------------|
| PNG base64 | ~465 KB | Lossless | Too heavy for inline HTML |
| JPEG q85 base64 | ~39 KB | Good (flattened) | ✅ Best for dark backgrounds |
| JPEG q85 base64 (RGB) | ~39 KB | Good | Logo bg must match intro bg |

**Critical:** Flatten the PNG onto the intro's background color (#1A1A1A = rgb(26,26,26)) before JPEG encoding, since JPEG has no alpha channel. If the intro background is also dark, the flatten is invisible.

```python
img = Image.open("logo.png").convert("RGBA").resize((500, 500), Image.LANCZOS)
bg = Image.new("RGB", (500, 500), (26, 26, 26))
bg.paste(img, mask=img.split()[3])  # Composite onto bg color
buffer = BytesIO()
bg.save(buffer, format="JPEG", quality=85)
b64 = "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode()
```
