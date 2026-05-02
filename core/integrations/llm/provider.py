"""
Cortex Leman v5 — LLM Provider Unifié

Supporte 2 modes:
- openrouter: API externe (mode Standard, startups, RH)
- ollama: LLM local (mode Haute Protection, avocats, banques, santé)

Le mode est déterminé par APP_MODE et LLM_PROVIDER dans .env.
"""
import logging
from typing import Optional
from abc import ABC, abstractmethod

import httpx

from core.config import settings
from core.journal.append_only_journal import journal
from core.journal.models import JournalEventType

logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):
    """Interface commune pour les providers LLM"""

    @abstractmethod
    async def generate(
        self,
        messages: list[dict],
        max_tokens: int = 4096,
        temperature: float = 0.7,
        vertical: str = "unknown",
        client_id: str = "unknown",
        intention_id: str = "unknown",
    ) -> dict:
        """Générer une réponse"""
        pass

    @abstractmethod
    async def health_check(self) -> dict:
        """Vérifier la disponibilité"""
        pass


class OpenRouterProvider(BaseLLMProvider):
    """
    Provider OpenRouter — Mode Standard
    Utilise des modèles externes (Mistral, Claude, GPT-4, etc.)
    Prompts peuvent être journalisés (pas de données sensibles).
    """

    def __init__(self):
        self._base_url = settings.llm_base_url
        self._api_key = settings.llm_api_key
        self._model = settings.llm_model
        self._timeout = settings.llm_timeout

    async def generate(
        self,
        messages: list[dict],
        max_tokens: int = 4096,
        temperature: float = 0.7,
        vertical: str = "unknown",
        client_id: str = "unknown",
        intention_id: str = "unknown",
    ) -> dict:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://cortex-leman.com",
            "X-Title": "Cortex Leman v5",
        }

        payload = {
            "model": self._model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )

                if response.status_code == 200:
                    data = response.json()
                    text = data["choices"][0]["message"]["content"]

                    # Journaliser l'appel LLM (métadonnées uniquement, pas le contenu)
                    journal.append(
                        event_type=JournalEventType.AGENT_RESULT,
                        client_id=client_id,
                        vertical=vertical,
                        agent_source="llm-openrouter",
                        intention_id=intention_id,
                        payload={
                            "model": self._model,
                            "tokens_used": data.get("usage", {}).get("total_tokens", 0),
                            "response_length": len(text),
                        },
                    )

                    return {
                        "text": text,
                        "model": self._model,
                        "provider": "openrouter",
                        "tokens": data.get("usage", {}).get("total_tokens", 0),
                    }
                else:
                    logger.error(f"OpenRouter error: {response.status_code}")
                    return {"text": "", "error": f"HTTP {response.status_code}"}

        except httpx.TimeoutException:
            logger.error("OpenRouter timeout")
            return {"text": "", "error": "timeout"}
        except Exception as e:
            logger.error(f"OpenRouter error: {e}")
            return {"text": "", "error": str(e)}

    async def health_check(self) -> dict:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self._base_url}/models", headers={
                    "Authorization": f"Bearer {self._api_key}",
                })
                return {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "provider": "openrouter",
                    "model": self._model,
                }
        except Exception as e:
            return {"status": "unhealthy", "provider": "openrouter", "error": str(e)}


class OllamaProvider(BaseLLMProvider):
    """
    Provider Ollama — Mode Haute Protection
    LLM local, aucune donnée ne sort de l'infrastructure.
    Requis pour avocats (Art. 321 CP), banques (Art. 47 LB), santé (LPM).
    """

    def __init__(self):
        self._base_url = settings.llm_base_url
        self._model = settings.llm_model
        self._timeout = settings.llm_timeout

    async def generate(
        self,
        messages: list[dict],
        max_tokens: int = 4096,
        temperature: float = 0.7,
        vertical: str = "unknown",
        client_id: str = "unknown",
        intention_id: str = "unknown",
    ) -> dict:
        # Ollama utilise le format chat/comistoire ou generate
        payload = {
            "model": self._model,
            "messages": messages,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/api/chat",
                    json=payload,
                )

                if response.status_code == 200:
                    data = response.json()
                    text = data.get("message", {}).get("content", "")

                    # Journaliser localement (mode Haute Protection)
                    journal.append(
                        event_type=JournalEventType.AGENT_RESULT,
                        client_id=client_id,
                        vertical=vertical,
                        agent_source="llm-ollama",
                        intention_id=intention_id,
                        payload={
                            "model": self._model,
                            "response_length": len(text),
                            "local": True,
                        },
                    )

                    return {
                        "text": text,
                        "model": self._model,
                        "provider": "ollama",
                        "local": True,
                    }
                else:
                    return {"text": "", "error": f"HTTP {response.status_code}"}

        except httpx.ConnectError:
            logger.error("Ollama non disponible — vérifier que le service tourne")
            return {"text": "", "error": "ollama_not_running"}
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return {"text": "", "error": str(e)}

    async def health_check(self) -> dict:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self._base_url}/api/tags")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    model_names = [m.get("name", "") for m in models]
                    return {
                        "status": "healthy",
                        "provider": "ollama",
                        "model": self._model,
                        "available_models": model_names,
                        "model_loaded": any(self._model in n for n in model_names),
                    }
                return {"status": "unhealthy", "provider": "ollama"}
        except Exception as e:
            return {"status": "unhealthy", "provider": "ollama", "error": str(e)}


class LLMService:
    """
    Service LLM unifié Cortex Leman.
    
    Pipeline: Guardrails in → LLM → Guardrails out → Journal
    
    Mode standard → OpenRouter (externe)
    Mode haute_protection → Ollama (local, aucune fuite de données)
    """

    def __init__(self):
        self._provider: Optional[BaseLLMProvider] = None
        self._setup_provider()
        self._total_calls = 0
        self._total_tokens = 0
        self._guardrail: Optional[object] = None  # lazy init

    def _get_guardrail(self):
        """Lazy-init du pipeline guardrails (singleton)."""
        if self._guardrail is None:
            try:
                from core.security.guardrails import GuardrailPipeline
                self._guardrail = GuardrailPipeline()
            except Exception:
                pass
        return self._guardrail

    def _setup_provider(self) -> None:
        """Initialiser le bon provider"""
        if settings.llm_provider == "ollama":
            self._provider = OllamaProvider()
            logger.info(f"LLM: Ollama local ({settings.llm_model}) — Mode Haute Protection")
        else:
            self._provider = OpenRouterProvider()
            logger.info(f"LLM: OpenRouter ({settings.llm_model}) — Mode Standard")

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        vertical: str = "unknown",
        client_id: str = "unknown",
        intention_id: str = "unknown",
    ) -> dict:
        """Générer une réponse LLM avec guardrails"""
        # Guardrails IN: vérifier le prompt utilisateur
        guardrail = self._get_guardrail()
        if guardrail:
            guard_result = guardrail.check_input(user_prompt, vertical)
            if guard_result.blocked:
                logger.warning(f"Guardrail IN bloqué: {guard_result.violations}")
                return {
                    "text": "",
                    "error": "guardrail_blocked",
                    "flags": guard_result.violations,
                }
            # Utiliser le texte nettoyé si PII détectée
            if guard_result.cleaned_content:
                user_prompt = guard_result.cleaned_content

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        result = await self._provider.generate(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            vertical=vertical,
            client_id=client_id,
            intention_id=intention_id,
        )

        # Stats
        self._total_calls += 1
        self._total_tokens += result.get("tokens", 0)

        # Guardrails OUT: vérifier la réponse
        if result.get("text") and guardrail:
            output_result = guardrail.check_output(result["text"])
            if output_result.blocked:
                logger.warning(f"Guardrail OUT bloqué: {output_result.violations}")
                result["text"] = "[Réponse filtrée par garde-fou de sécurité]"
                result["guardrail_flags"] = output_result.violations

        return result

    async def generate_for_agent(
        self,
        agent_name: str,
        task: str,
        context: dict,
        vertical: str = "unknown",
        client_id: str = "unknown",
        intention_id: str = "unknown",
        use_rag: bool = True,
    ) -> dict:
        """
        Générer une réponse pour un agent spécifique.
        Pipeline: Skill prompt + RAG context + Guardrails + LLM.
        """
        # 1. Charger le skill (system prompt) de l'agent
        from core.agents.prompts import build_system_prompt
        system_prompt = build_system_prompt(agent_name, vertical, context)

        # 2. Injecter le contexte RAG si disponible
        if use_rag:
            try:
                from core.integrations.rag import get_rag
                rag = get_rag()
                rag_context = rag.build_context_for_agent(
                    query=task,
                    agent_name=agent_name,
                    vertical=vertical,
                    client_id=client_id,
                )
                if rag_context and "Aucun contexte" not in rag_context:
                    system_prompt += f"\n\n{rag_context}"
            except Exception as e:
                logger.debug(f"RAG non disponible: {e}")

        # 3. Appel LLM avec guardrails
        return await self.generate(
            system_prompt=system_prompt,
            user_prompt=task,
            vertical=vertical,
            client_id=client_id,
            intention_id=intention_id,
        )

    async def health_check(self) -> dict:
        base = await self._provider.health_check()
        base["total_calls"] = self._total_calls
        base["total_tokens"] = self._total_tokens
        return base

    @property
    def provider_name(self) -> str:
        return settings.llm_provider

    @property
    def is_local(self) -> bool:
        return settings.llm_provider == "ollama"


# Singleton
llm_service = LLMService()
