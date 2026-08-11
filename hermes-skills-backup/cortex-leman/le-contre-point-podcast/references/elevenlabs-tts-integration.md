# ElevenLabs TTS : findings techniques et intégration

Explored 2026-07-20 as alternative to edge-tts HenriNeural for more natural voice (avoid YouTube "IA" label penalty observed on Tech In Check French — 10 likes for 25min).

## Coût réel par épisode (mesuré sur ep03)

Caractères par section (comptage réel, pas estimation):
```
01_cold_open    736 chars
02_rappel       842 chars
03_angle1      1189 chars
04_angle2      1280 chars
05_angle3      1116 chars
06_changement   828 chars
07_verdict     1165 chars
TOTAL          7156 chars  (~1101 mots)
```

| Plan | Prix | Episodes/mois |
|------|------|:---:|
| Free | $0 | 1.4 |
| Starter | $5 | 4.2 |
| Creator | $22 | 14 |
| Pro | $99 | 70 |

**Recommandation**: Starter ($5/mois) suffit pour un rythme de 4 épisodes/mois. Free plan = 1 épisode + tests.

## Permissions de clé — pitfall critique

Toutes les clés ElevenLabs n'ont pas les mêmes permissions. Symptômes observés avec une clé limitée:

- `client.voices.search()` → 401 `missing_permissions` (code: `voices_read`)
- Voix premium (Antoni `21m00Tcm4TlvDq8ikWAM`, Daniel `on2KvcuMNQc0uvP052q7`, Arnold, Michael) → 401 sur TTS
- Voix par défaut (Adam `pNInz6obpgDQGcFmaJgB`, George `JBFqnCBsd6RMkjVDRZzb`) → OK

**Fix**: vérifier les permissions de la clé dans le dashboard ElevenLabs (Settings → API Keys). Une clé "preview" ou restreinte ne donnera pas accès au catalogue complet.

## Voix accessibles et recommandées (podcast finance FR)

| Voix | Voice ID | Timbre | Stability recommandée |
|------|----------|--------|----------------------|
| **George** ✅ Choix validé | `JBFqnCBsd6RMkjVDRZzb` | Journalistique, mid-range — naturel, crédibilité finance | 0.50 (similarity 0.75) |
| Adam | `pNInz6obpgDQGcFmaJgB` | Grave, narratif | 0.75 |

**George est le choix retenu** (validé user après A/B test, juil. 2026). Timbre journalistique = crédibilité financière sans paraître dramatique. Plus rapide naturellement qu'Adam (~137 wpm vs ~120).

## Pacing: pas de `rate` avec ElevenLabs

George parle à ~137 mots/min naturellement. Mesuré contre edge-tts HenriNeural `+10%` (117 mots/min), George est ~17% plus rapide **sans accélération artificielle**. Conséquence: le paramètre `rate` d'edge-tts n'a pas d'équivalent ElevenLabs et n'est plus nécessaire. Les Shorts migrés depuis `rate="+10%"` conservent leur énergie grâce au pacing naturel de George.

## Pattern d'intégration SDK v2.58.0

```python
from elevenlabs import ElevenLabs, VoiceSettings
from pathlib import Path

client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])

audio = client.text_to_speech.convert(
    voice_id="JBFqnCBsd6RMkjVDRZzb",  # George
    model_id="eleven_multilingual_v2",
    text=section_text,
    voice_settings=VoiceSettings(
        stability=0.50,        # George: neutre, moins rigide
        similarity_boost=0.75, # fidélité au timbre
        style=0.0,             # neutre (pas de dramatisation)
        use_speaker_boost=True
    )
)
Path(output_path).write_bytes(b"".join(audio))  # generator → bytes
```

**Important**: `text_to_speech.convert()` retourne un **generator d'bytes**, pas un bytes direct. Il faut `b"".join(audio)` pour assembler.

## Architecture recommandée : fallback edge-tts

Pour éviter qu'un quota dépassé bloque le pipeline, implémenter un fallback:

```python
def gen_tts_section(text, output_path, provider="elevenlabs"):
    if provider == "elevenlabs":
        try:
            client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
            audio = client.text_to_speech.convert(...)
            Path(output_path).write_bytes(b"".join(audio))
            return output_path
        except Exception as e:
            print(f"⚠️ ElevenLabs failed ({e}), fallback to edge-tts")
    # Fallback: edge-tts HenriNeural (gratuit, illimité)
    asyncio.run(edge_tts.Communicate(text, "fr-FR-HenriNeural", rate="+0%").save(output_path))
    return output_path
```

## Setup dans le projet

```bash
# 1. Installer le SDK
pip install elevenlabs

# 2. Clé API dans .env (déjà gitignored)
echo 'ELEVENLABS_API_KEY=sk_...' >> ~/crypto-project/.env

# 3. Vérifier .env est dans .gitignore
grep ".env" ~/crypto-project/.gitignore
```

## Comparaison mesurée (cold_open ep03, 291 chars)

| Provider | Durée | Taille | Notes |
|----------|-------|--------|-------|
| edge-tts HenriNeural | 18.1s | 106KB | Léger, rapide, gratuit |
| ElevenLabs Adam (stab=0.5) | 21.9s | 342KB | Plus lent (latence API), plus riche |
| ElevenLabs George | 19.2s | 300KB | — |
| ElevenLabs Adam (stab=0.75) | 20.9s | 327KB | Recommandé |

Les samples ElevenLabs sont ~3x plus lourds (qualité audio supérieure, 44.1kHz vs edge-tts).
