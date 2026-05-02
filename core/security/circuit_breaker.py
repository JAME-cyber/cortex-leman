"""
Cortex Leman v5 — Circuit Breaker

Protection contre les agents défaillants.
Si un agent produit des réponses incohérentes, il est isolé.
"""
import time
import logging
from enum import Enum
from typing import Callable, Optional
from datetime import datetime

from core.config import settings

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    CLOSED = "closed"      # Normal
    OPEN = "open"          # Bloqué (trop d'échecs)
    HALF_OPEN = "half_open"  # Test de récupération


class CircuitBreaker:
    """
    Circuit Breaker par agent.
    
    CLOSED → (seuil atteint) → OPEN → (timeout) → HALF_OPEN → 
        (succès) → CLOSED / (échec) → OPEN
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = None,
        recovery_timeout: int = None,
        half_open_max: int = None,
    ):
        self.name = name
        self.failure_threshold = failure_threshold or settings.cb_failure_threshold
        self.recovery_timeout = recovery_timeout or settings.cb_recovery_timeout
        self.half_open_max = half_open_max or settings.cb_half_open_max

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._half_open_calls = 0
        self._last_failure_time: Optional[float] = None
        self._last_state_change = datetime.now()

    @property
    def state(self) -> CircuitState:
        """Vérifier l'état actuel (avec transition auto HALF_OPEN)"""
        if (
            self._state == CircuitState.OPEN
            and self._last_failure_time
            and time.time() - self._last_failure_time >= self.recovery_timeout
        ):
            self._transition_to(CircuitState.HALF_OPEN)
        return self._state

    def record_success(self) -> None:
        """Enregistrer un succès"""
        if self._state == CircuitState.HALF_OPEN:
            self._half_open_calls += 1
            if self._half_open_calls >= self.half_open_max:
                self._transition_to(CircuitState.CLOSED)
        self._success_count += 1
        self._failure_count = 0

    def record_failure(self) -> None:
        """Enregistrer un échec"""
        self._failure_count += 1
        self._success_count = 0
        self._last_failure_time = time.time()

        if self._state == CircuitState.HALF_OPEN:
            self._transition_to(CircuitState.OPEN)
            logger.warning(f"Circuit [{self.name}]: HALF_OPEN → OPEN (échec test)")
        elif self._failure_count >= self.failure_threshold:
            self._transition_to(CircuitState.OPEN)
            logger.warning(
                f"Circuit [{self.name}]: CLOSED → OPEN "
                f"({self._failure_count} échecs)"
            )

    def allow_request(self) -> bool:
        """Vérifier si une requête est autorisée"""
        state = self.state
        if state == CircuitState.CLOSED:
            return True
        if state == CircuitState.HALF_OPEN:
            return self._half_open_calls < self.half_open_max
        return False  # OPEN

    def _transition_to(self, new_state: CircuitState) -> None:
        old = self._state
        self._state = new_state
        self._last_state_change = datetime.now()

        if new_state == CircuitState.CLOSED:
            self._failure_count = 0
            self._half_open_calls = 0
        elif new_state == CircuitState.HALF_OPEN:
            self._half_open_calls = 0

        logger.info(f"Circuit [{self.name}]: {old.value} → {new_state.value}")

    def get_status(self) -> dict:
        return {
            "name": self.name,
            "state": self.state.value,
            "failures": self._failure_count,
            "successes": self._success_count,
            "threshold": self.failure_threshold,
            "last_change": self._last_state_change.isoformat(),
        }


class CircuitBreakerRegistry:
    """Registry des circuit breakers par agent"""

    def __init__(self):
        self._breakers: dict[str, CircuitBreaker] = {}

    def get(self, agent_name: str) -> CircuitBreaker:
        if agent_name not in self._breakers:
            self._breakers[agent_name] = CircuitBreaker(name=agent_name)
        return self._breakers[agent_name]

    def get_all_status(self) -> dict[str, dict]:
        return {name: cb.get_status() for name, cb in self._breakers.items()}


# Singleton
circuit_registry = CircuitBreakerRegistry()
