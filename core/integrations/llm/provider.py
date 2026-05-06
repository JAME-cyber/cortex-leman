"""
Cortex Leman v5 — LLM Provider Unifié (LiteLLM)

Architecture model-agnostic: 18+ providers via LiteLLM.
Routing intelligent par verticale — le bon modèle pour chaque métier.

Providers supportés:
- openrouter: Route vers 200+ modèles (Mistral, Claude, GPT-4, Gemini, etc.)
- anthropic: Claude direct
- openai: GPT-4 direct
- ollama: LLM local (mode Haute Protection)
- deepseek, groq, mistral, xai, bedrock, azure, google, sambanova, etc.

Modes:
- Mode Standard: Cloud, routing par verticale
- Mode Haute Protection: Ollama local, zero appel externe
"""
import json
import logging
import os
from datetime import datetime, timezone
from typing import Optional

import litellm

from core.config import settings
from core.journal.append_only_journal import journal
from core.journal.models import JournalEventType

logger = logging.getLogger(__name__)

# Configurer LiteLLM
litellm.suppress_debug_info = True
litellm.set_verbose = False


# ============================================================
# Model Router — Sélectionne le modèle optimal par contexte
# ============================================================

class ModelRouter:
    """
    Route le bon modèle LLM en fonction de:
    - La verticale métier
    - Le mode de déploiement (Standard vs Haute Protection)
    - L'agent qui appelle
    """

    def __init__(self):
        self._routing = settings.llm_vertical_routing or {}
        self._default_model = settings.llm_model
        self._high_protection_model = settings.llm_high_protection_model
        self._is_high_protection = settings.app_mode == "haute_protection"

    def resolve_model(
        self,
        vertical: str = "unknown",
        agent_name: str = "unknown",
        force_local: bool = False,
    ) -> tuple[str, str]:
        """
        Résoudre le modèle à utiliser.
        
        Returns:
            (model_id, provider_label)
            model_id: identifiant LiteLLM (ex: "openrouter/anthropic/claude-sonnet-4-20250514")
            provider_label: label humain (ex: "openrouter/claude-sonnet-4")
        """
        # Mode Haute Protection: toujours local
        if self._is_high_protection or force_local:
            model = self._high_protection_model
            provider = "ollama"
            return f"ollama/{model}", f"ollama/{model}"

        # Routing par verticale
        model = self._routing.get(vertical)

        if model:
            # Le modèle peut être "provider/model" ou juste "model"
            if "/" not in model:
                # Pas de provider prefix → utiliser le provider par défaut
                provider_prefix = settings.llm_provider
                full_model = f"{provider_prefix}/{model}"
            else:
                full_model = f"openrouter/{model}"
                provider_prefix = model.split("/")[0]

            return full_model, model

        # Fallback: modèle par défaut
        if "/" in self._default_model:
            full_model = f"openrouter/{self._default_model}"
        else:
            full_model = f"{settings.llm_provider}/{self._default_model}"

        return full_model, self._default_model

    def get_routing_table(self) -> dict:
        """Retourner la table de routing complète"""
        table = {}
        for vertical, model in self._routing.items():
            full_model, label = self.resolve_model(vertical)
            table[vertical] = {
                "model": label,
                "full_id": full_model,
                "local": self._is_high_protection,
            }
        return table


# ============================================================
# LLM Service — Pipeline complet avec LiteLLM
# ============================================================

class LLMService:
    """
    Service LLM unifié Cortex Leman v5.
    
    Pipeline: Guardrails IN → Model Router → LiteLLM → Guardrails OUT → Journal
    
    Model-agnostic: 18+ providers via LiteLLM.
    Routing par verticale: le bon modèle pour chaque métier.
    """

    def __init__(self):
        self._router = ModelRouter()
        self._total_calls = 0
        self._total_tokens = 0
        self._call_log: list[dict] = []  # Last 100 calls
        self._guardrail = None  # lazy init
        self._setup_api_keys()

    def _setup_api_keys(self) -> None:
        """Configurer les clés API pour LiteLLM"""
        # OpenRouter
        if settings.llm_api_key:
            os.environ.setdefault("OPENROUTER_API_KEY", settings.llm_api_key)

        # Les autres clés sont lues depuis l'environnement par LiteLLM:
        # ANTHROPIC_API_KEY, OPENAI_API_KEY, DEEPSEEK_API_KEY, etc.

    def _get_guardrail(self):
        """Lazy-init du pipeline guardrails (singleton)."""
        if self._guardrail is None:
            try:
                from core.security.guardrails import GuardrailPipeline
                self._guardrail = GuardrailPipeline()
            except Exception:
                pass
        return self._guardrail

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        vertical: str = "unknown",
        client_id: str = "unknown",
        intention_id: str = "unknown",
        model_override: str = None,
    ) -> dict:
        """
        Générer une réponse LLM avec pipeline complet.
        
        Pipeline:
        1. Guardrails IN (PII, injection)
        2. Model Router (sélection modèle par verticale)
        3. LiteLLM call (provider-agnostic)
        4. Guardrails OUT (safety, compliance)
        5. Journal (métadonnées)
        """
        # === Phase 1: Guardrails IN ===
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
            if guard_result.cleaned_content:
                user_prompt = guard_result.cleaned_content

        # === Phase 2: Model Router ===
        if model_override:
            # Override explicite (ex: forcer ollama pour un appel spécifique)
            if "/" not in model_override:
                model_id = f"{settings.llm_provider}/{model_override}"
            else:
                model_id = model_override
            model_label = model_override
        else:
            model_id, model_label = self._router.resolve_model(vertical)

        # === Phase 3: LiteLLM Call ===
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            # Construction des kwargs LiteLLM
            kwargs = {
                "model": model_id,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "timeout": settings.llm_timeout,
            }

            # Ajouter api_base si Ollama
            if model_id.startswith("ollama/"):
                kwargs["api_base"] = settings.llm_base_url

            # Appel LiteLLM (supporte 18+ providers)
            response = await litellm.acompletion(**kwargs)

            # Extraction de la réponse
            text = response.choices[0].message.content or ""
            tokens = response.usage.total_tokens if response.usage else 0
            actual_model = response.model or model_label

            # === Phase 4: Journal ===
            provider_label = model_id.split("/")[0] if "/" in model_id else settings.llm_provider
            journal.append(
                event_type=JournalEventType.AGENT_RESULT,
                client_id=client_id,
                vertical=vertical,
                agent_source=f"llm-{provider_label}",
                intention_id=intention_id,
                payload={
                    "model": actual_model,
                    "tokens_used": tokens,
                    "response_length": len(text),
                    "local": provider_label == "ollama",
                },
            )

            # === Phase 5: Guardrails OUT ===
            guardrail_flags = []
            if text and guardrail:
                output_result = guardrail.check_output(text)
                if output_result.blocked:
                    logger.warning(f"Guardrail OUT bloqué: {output_result.violations}")
                    text = "[Réponse filtrée par garde-fou de sécurité]"
                    guardrail_flags = output_result.violations

            # Stats
            self._total_calls += 1
            self._total_tokens += tokens
            self._log_call(model_label, provider_label, vertical, tokens, len(text))

            return {
                "text": text,
                "model": actual_model,
                "provider": provider_label,
                "tokens": tokens,
                "guardrail_flags": guardrail_flags,
            }

        except litellm.AuthenticationError as e:
            logger.error(f"LLM Auth error ({model_id}): {e}")
            return {"text": "", "error": f"auth_error: {str(e)[:100]}"}
        except litellm.RateLimitError as e:
            logger.error(f"LLM Rate limit ({model_id}): {e}")
            return {"text": "", "error": f"rate_limit: {str(e)[:100]}"}
        except litellm.Timeout as e:
            logger.error(f"LLM Timeout ({model_id}): {e}")
            return {"text": "", "error": "timeout"}
        except litellm.NotFoundError as e:
            logger.error(f"LLM Model not found ({model_id}): {e}")
            # Fallback vers modèle par défaut
            return await self._fallback_generate(
                messages, max_tokens, temperature,
                vertical, client_id, intention_id,
            )
        except Exception as e:
            logger.error(f"LLM Error ({model_id}): {e}")
            return {"text": "", "error": str(e)[:200]}

    async def _fallback_generate(
        self,
        messages: list[dict],
        max_tokens: int,
        temperature: float,
        vertical: str,
        client_id: str,
        intention_id: str,
    ) -> dict:
        """Fallback vers le modèle par défaut si le modèle routé échoue"""
        fallback_model = f"{settings.llm_provider}/{settings.llm_model}"
        logger.warning(f"Fallback vers modèle par défaut: {fallback_model}")

        try:
            kwargs = {
                "model": fallback_model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "timeout": settings.llm_timeout,
            }
            if fallback_model.startswith("ollama/"):
                kwargs["api_base"] = settings.llm_base_url

            response = await litellm.acompletion(**kwargs)
            text = response.choices[0].message.content or ""
            tokens = response.usage.total_tokens if response.usage else 0

            return {
                "text": text,
                "model": settings.llm_model,
                "provider": settings.llm_provider,
                "tokens": tokens,
                "fallback": True,
            }
        except Exception as e:
            logger.error(f"Fallback LLM also failed: {e}")
            return {"text": "", "error": f"fallback_failed: {str(e)[:100]}"}

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
        Pipeline: Skill prompt + RAG context + Model Router + Guardrails + LLM.
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

        # 3. Appel LLM avec pipeline complet
        return await self.generate(
            system_prompt=system_prompt,
            user_prompt=task,
            vertical=vertical,
            client_id=client_id,
            intention_id=intention_id,
        )

    async def health_check(self) -> dict:
        """Vérifier la disponibilité du provider LLM actif"""
        model_id, model_label = self._router.resolve_model()
        provider = model_id.split("/")[0] if "/" in model_id else settings.llm_provider

        try:
            if provider == "ollama":
                # Health check Ollama: vérifier que le serveur répond
                import httpx
                async with httpx.AsyncClient(timeout=5) as client:
                    resp = await client.get(f"{settings.llm_base_url}/api/tags")
                    if resp.status_code == 200:
                        models = [m.get("name", "") for m in resp.json().get("models", [])]
                        return {
                            "status": "healthy",
                            "provider": "ollama",
                            "model": settings.llm_high_protection_model,
                            "available_models": models,
                            "model_loaded": any(settings.llm_high_protection_model in m for m in models),
                            "total_calls": self._total_calls,
                            "total_tokens": self._total_tokens,
                        }
            else:
                # Health check cloud: essayer un appel minimal
                return {
                    "status": "healthy" if settings.llm_api_key else "no_api_key",
                    "provider": provider,
                    "model": model_label,
                    "total_calls": self._total_calls,
                    "total_tokens": self._total_tokens,
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": provider,
                "error": str(e)[:200],
                "total_calls": self._total_calls,
                "total_tokens": self._total_tokens,
            }

    def _log_call(
        self, model: str, provider: str, vertical: str, tokens: int, response_len: int
    ) -> None:
        """Logger le dernier appel (circulaire, max 100)"""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": model,
            "provider": provider,
            "vertical": vertical,
            "tokens": tokens,
            "response_length": response_len,
        }
        self._call_log.append(entry)
        if len(self._call_log) > 100:
            self._call_log = self._call_log[-100:]

    def get_routing_table(self) -> dict:
        """Table de routing complète (pour l'API)"""
        return {
            "mode": settings.app_mode,
            "default_model": settings.llm_model,
            "default_provider": settings.llm_provider,
            "high_protection_model": settings.llm_high_protection_model,
            "vertical_routing": self._router.get_routing_table(),
        }

    def get_stats(self) -> dict:
        """Statistiques d'utilisation"""
        return {
            "total_calls": self._total_calls,
            "total_tokens": self._total_tokens,
            "recent_calls": len(self._call_log),
        }

    @property
    def provider_name(self) -> str:
        return settings.llm_provider

    @property
    def is_local(self) -> bool:
        return settings.app_mode == "haute_protection"


# Singleton
llm_service = LLMService()
