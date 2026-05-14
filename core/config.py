"""
Cortex Leman v5 — Configuration Pydantic Settings
"""
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from typing import Optional


default_db_url = "sqlite:///./data/cortex-leman.db"


class Settings(BaseSettings):
    """Application settings loaded from .env"""

    app_name: str = "cortex-leman-v5"
    app_version: str = "5.0.0"
    app_env: str = "development"
    app_mode: str = "standard"  # standard | haute_protection

    # NATS
    nats_url: str = "nats://localhost:4222"
    nats_cluster: str = "cortex-leman-cluster"
    nats_client_id: str = "cortex-orchestrator"
    nats_stream_name: str = "CLEMAN_INTENTIONS"
    nats_stream_subjects: str = "cleman.>"
    nats_max_age_days: int = 365
    nats_max_msg_size: int = 1048576
    nats_replicas: int = 1

    # Journal
    journal_path: str = "./data/journal"
    journal_hash_algo: str = "sha256"
    journal_signing_key: str = "change_this_in_production"  # noqa: S105 — override via .env
    journal_worm: bool = True

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_lock_timeout: int = 30

    # LLM — Provider principal (LiteLLM, 18+ providers)
    llm_provider: str = "openrouter"  # openrouter | ollama | anthropic | openai | deepseek | groq | etc.
    llm_model: str = "mistralai/mistral-small-3.1-24b-instruct"
    llm_base_url: str = "https://openrouter.ai/api/v1"
    llm_api_key: Optional[str] = None
    llm_timeout: int = 60
    llm_max_tokens: int = 4096

    # LLM — Routing par verticale (model-agnostic)
    # Chaque verticale peut utiliser un modèle différent optimisé pour son domaine.
    # Format: {"verticale": "provider/model"}
    # Si une verticale n'est pas listée, le modèle par défaut (llm_model) est utilisé.
    llm_vertical_routing: dict = {
        # Mode Standard (cloud) — modèles validés sur OpenRouter
        # GLM 5.1 = top agentic model (HuggingFace AI Engineer Summit 2026, Merve Noyan)
        # DeepSeek V4 Flash = fallback rapide et économique
        "comptable": "thudm/glm-5.1",                      # Précision fiscale, rédaction structurée
        "avocat": "thudm/glm-5.1",                         # Raisonnement juridique, secret professionnel
        "sante": "thudm/glm-5.1",                          # Données médicales, haute protection
        "banque": "thudm/glm-5.1",                         # KYC/AML, conformité FINMA
        "startup": "deepseek/deepseek-v4-flash",           # Rapide, économique
        "rh": "thudm/glm-5.1",                             # Anti-discrimination, RGPD art. 22
        "agent-ia": "thudm/glm-5.1",                       # Conformité agents IA
    }
    # Fallback chain si GLM 5.1 indisponible
    llm_fallback_models: list = [
        "deepseek/deepseek-v4-flash",
        "google/gemini-2.0-flash-001",
        "mistralai/mistral-small-3.1-24b-instruct",
    ]
    # Override pour Mode Haute Protection (local uniquement)
    llm_high_protection_model: str = "llama3.1:8b"  # Modèle Ollama par défaut

    # Reflection Node (pattern JP Morgan "Ask David")
    reflection_enabled: bool = True  # Auto-critique LLM avant livraison
    reflection_max_confidence_delta: float = 0.3  # Seuil de confirmation

    # Mediator
    mediator_rules_dir: str = "./core/mediator/rules"
    mediator_conflict_threshold: float = 0.7
    mediator_freeze_enabled: bool = True
    # P1: Seuil de gel par défaut (utilisé si pas de seuil spécifique par verticale)
    mediator_default_freeze_threshold: float = 10000.0

    # Circuit Breaker
    cb_failure_threshold: int = 5
    cb_recovery_timeout: int = 60
    cb_half_open_max: int = 3

    # Saga
    saga_max_retries: int = 3
    saga_compensation_timeout: int = 300

    # Arbitration
    arbitration_signature_enabled: bool = False
    arbitration_timestamp_server: str = "http://timestamp.digicert.com"
    arbitration_timestamp_provider: str = "auto"  # auto | local_hmac | swisssign | certigna | digicert
    arbitration_precedent_file: str = "./data/precedents.json"
    # P0: Escalade arbitrage — chaîne d'escalade (nom ou ID)
    arbitration_escalation_chain: list[str] = ["expert", "expert_suppleant", "associe"]
    # P0: Timeout par niveau d'escalade (en heures)
    arbitration_escalation_timeout_hours: list[float] = [2.0, 4.0, 8.0]

    # Compliance
    compliance_data_residency: str = "EU"
    compliance_encryption: str = "AES-256"
    compliance_audit_interval: str = "daily"
    compliance_report_dir: str = "./data/reports"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    api_cors_origins: str = "http://localhost:3000,http://localhost:5173,http://localhost:3001,http://localhost:3002"

    # Database
    database_url: str = default_db_url

    # Security
    secret_key: str = "change_this_in_production"  # noqa: S105 — override via .env
    seed_admin_password: Optional[str] = None  # Mot de passe admin initial (prod)
    mtls_enabled: bool = False

    # JWT
    jwt_algorithm: str = "HS256"
    jwt_access_expire_minutes: int = 30
    jwt_refresh_expire_days: int = 7

    # Encryption
    encryption_enabled: bool = True

    # Vertical
    active_vertical: str = "comptable"

    # Stripe Billing
    stripe_secret_key: Optional[str] = None  # sk_test_... or sk_live_...
    stripe_webhook_secret: Optional[str] = None  # whsec_...
    stripe_price_sentinelle: Optional[str] = None  # price_... CHF 500/mois
    stripe_price_garde: Optional[str] = None  # price_... CHF 900/mois
    stripe_price_forteresse: Optional[str] = None  # price_... CHF 1500/mois

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
