"""
Cortex Leman v5 — Voice Service (STT + TTS)

Speech-to-Text: faster-whisper (local, gratuit)
Text-to-Speech: edge-tts (gratuit) / elevenlabs (premium)

Modes:
- Local: faster-whisper + edge-tts → 100% gratuit, zéro API externe
- Premium: faster-whisper + elevenlabs → meilleure qualité vocale
- Haute Protection: tout local, zéro appel externe
"""
import io
import logging
import tempfile
from pathlib import Path
from typing import Optional

from core.config import settings

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# Speech-to-Text (STT)
# ═══════════════════════════════════════════════════════════════

class STTService:
    """Transcription vocale via faster-whisper (local)."""

    def __init__(self):
        self._model = None
        self._model_size = "base"  # tiny, base, small, medium, large

    def _load_model(self):
        """Lazy load du modèle whisper."""
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
                self._model = WhisperModel(self._model_size, device="cpu", compute_type="int8")
                logger.info(f"STT: faster-whisper modèle '{self._model_size}' chargé")
            except ImportError:
                logger.warning("STT: faster-whisper non installé — STT indisponible")
                raise
            except Exception as e:
                logger.error(f"STT: erreur chargement modèle: {e}")
                raise

    async def transcribe(
        self,
        audio_data: bytes,
        language: str = "fr",
        task: str = "transcribe",
    ) -> dict:
        """
        Transcrire un audio en texte.

        Args:
            audio_data: Bytes du fichier audio (wav, mp3, webm, ogg)
            language: Langue (fr, de, en, it)
            task: "transcribe" ou "translate" (translate → anglais)

        Returns:
            {"text": "...", "language": "fr", "segments": [...], "duration": 5.2}
        """
        self._load_model()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_data)
            tmp_path = tmp.name

        try:
            segments, info = self._model.transcribe(
                tmp_path,
                language=language,
                task=task,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500),
            )

            text_parts = []
            segment_list = []
            for seg in segments:
                text_parts.append(seg.text.strip())
                segment_list.append({
                    "start": round(seg.start, 2),
                    "end": round(seg.end, 2),
                    "text": seg.text.strip(),
                    "confidence": round(seg.avg_logprob, 2) if seg.avg_logprob else None,
                })

            full_text = " ".join(text_parts)

            return {
                "text": full_text,
                "language": info.language if hasattr(info, "language") else language,
                "language_probability": round(info.language_probability, 2) if hasattr(info, "language_probability") else 1.0,
                "duration": round(info.duration, 1) if hasattr(info, "duration") else 0.0,
                "segments": segment_list[:20],
                "words_count": len(full_text.split()),
            }
        finally:
            Path(tmp_path).unlink(missing_ok=True)


# ═══════════════════════════════════════════════════════════════
# Text-to-Speech (TTS)
# ═══════════════════════════════════════════════════════════════

class TTSService:
    """Synthèse vocale — edge-tts (gratuit) ou elevenlabs (premium)."""

    # Voix françaises edge-tts
    EDGE_VOICES = {
        "fr-CH": "fr-CH-ArianeNeural",        # Suisse française
        "fr-FR": "fr-FR-DeniseNeural",         # France
        "fr-CA": "fr-CA-SylvieNeural",         # Canada
        "de-CH": "de-CH-LeniNeural",           # Suisse allemande
        "en-US": "en-US-AriaNeural",           # Anglais
        "it-CH": "it-CH-DiegoNeural",          # Suisse italienne
    }

    # Voix par persona
    PERSONA_VOICES = {
        "le_leman": "fr-CH-ArianeNeural",
        "comptable": "fr-FR-DeniseNeural",
        "avocat": "fr-FR-HenriNeural",
        "sante": "fr-CA-SylvieNeural",
        "banque": "fr-FR-DeniseNeural",
        "startup": "fr-FR-DeniseNeural",
        "rh": "fr-FR-DeniseNeural",
    }

    def __init__(self):
        self._elevenlabs_client = None
        self._mode = "edge"  # edge (gratuit) ou elevenlabs (premium)

    def _get_edge_voice(self, persona: str = "le_leman", locale: str = None) -> str:
        """Sélectionner la voix edge-tts."""
        if locale and locale in self.EDGE_VOICES:
            return self.EDGE_VOICES[locale]
        return self.PERSONA_VOICES.get(persona, "fr-CH-ArianeNeural")

    async def synthesize(
        self,
        text: str,
        persona: str = "le_leman",
        locale: str = None,
        rate: str = "+0%",
        pitch: str = "+0Hz",
    ) -> dict:
        """
        Synthétiser du texte en audio.

        Args:
            text: Texte à synthétiser
            persona: Persona pour le choix de voix
            locale: Locale (fr-CH, fr-FR, etc.)
            rate: Vitesse ("+0%", "+20%", "-10%")
            pitch: Tonalité ("+0Hz", "+5Hz")

        Returns:
            {"audio_data": bytes, "content_type": "audio/mp3", "duration_ms": int, "voice": "..."}
        """
        if self._mode == "elevenlabs":
            return await self._synthesize_elevenlabs(text, persona)
        else:
            return await self._synthesize_edge(text, persona, locale, rate, pitch)

    async def _synthesize_edge(
        self,
        text: str,
        persona: str,
        locale: str = None,
        rate: str = "+0%",
        pitch: str = "+0Hz",
    ) -> dict:
        """Synthèse via edge-tts (100% gratuit)."""
        import edge_tts
        import asyncio

        voice = self._get_edge_voice(persona, locale)
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)

        audio_buffer = io.BytesIO()
        await communicate.save(audio_buffer)
        audio_data = audio_buffer.getvalue()

        # Estimation durée (edge-tts ne la fournit pas directement)
        # ~150 mots/minute en français
        word_count = len(text.split())
        duration_ms = int((word_count / 150) * 60 * 1000)

        return {
            "audio_data": audio_data,
            "content_type": "audio/mpeg",
            "duration_ms": duration_ms,
            "voice": voice,
            "provider": "edge-tts",
            "size_bytes": len(audio_data),
        }

    async def _synthesize_elevenlabs(self, text: str, persona: str) -> dict:
        """Synthèse via ElevenLabs (premium)."""
        try:
            from elevenlabs import generate, set_api_key
            api_key = getattr(settings, "elevenlabs_api_key", None) or ""
            if not api_key:
                logger.warning("TTS: pas de clé ElevenLabs — fallback edge-tts")
                return await self._synthesize_edge(text, persona)

            set_api_key(api_key)

            # Voix française par défaut
            voice_id = "pNInz6obpgDQGcFmaJgB"  # Bella (FR)
            audio = generate(text=text, voice=voice_id, model="eleven_multilingual_v2")

            audio_data = b"".join(chunk for chunk in audio if isinstance(chunk, bytes))

            return {
                "audio_data": audio_data,
                "content_type": "audio/mpeg",
                "duration_ms": int(len(text.split()) / 150 * 60000),
                "voice": "elevenlabs-bella",
                "provider": "elevenlabs",
                "size_bytes": len(audio_data),
            }
        except Exception as e:
            logger.warning(f"TTS: ElevenLabs échoué ({e}) — fallback edge-tts")
            return await self._synthesize_edge(text, persona)

    async def stream_synthesize(self, text: str, persona: str = "le_leman"):
        """Stream audio chunks (pour lecture en streaming)."""
        import edge_tts

        voice = self._get_edge_voice(persona)
        communicate = edge_tts.Communicate(text, voice)

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]


# ═══════════════════════════════════════════════════════════════
# Singletons
# ═══════════════════════════════════════════════════════════════

stt_service = STTService()
tts_service = TTSService()
