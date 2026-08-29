import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    api_secret_key: str | None
    ollama_host: str
    ollama_model: str
    ollama_api_key: str
    allowed_models: frozenset[str]


@lru_cache
def get_settings() -> Settings:
    default_model = os.getenv("OLLAMA_MODEL", "llama3").strip()
    configured_models = {
        model.strip()
        for model in os.getenv("OLLAMA_ALLOWED_MODELS", "").split(",")
        if model.strip()
    }
    if not configured_models:
        configured_models = {default_model}

    return Settings(
        api_secret_key=os.getenv("API_SECRET_KEY"),
        ollama_host=os.getenv(
            "OLLAMA_HOST", "http://host.docker.internal:11434"
        ).rstrip("/"),
        ollama_model=default_model,
        ollama_api_key=os.getenv("OLLAMA_API_KEY", "ollama"),
        allowed_models=frozenset(configured_models),
    )
