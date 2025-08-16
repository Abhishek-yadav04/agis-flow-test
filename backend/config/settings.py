from __future__ import annotations
from typing import List
import os
from pydantic_settings import BaseSettings
from pydantic import field_validator
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    app_name: str = "AgisFL Enterprise"
    environment: str = os.getenv("ENV", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", "8001"))

    jwt_secret: str = os.getenv("JWT_SECRET", "")

    # Preview model feature flags (enabled by default; can be disabled via env)
    enable_gpt5_preview: bool = os.getenv("ENABLE_GPT5_PREVIEW", "true").lower() == "true"
    enable_gemini_2_5_pro: bool = os.getenv("ENABLE_GEMINI_2_5_PRO", "true").lower() == "true"

    cors_origins: List[str] = [
        "http://127.0.0.1:8001",
        "http://localhost:8001",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ]

    security_headers_enabled: bool = True

    @field_validator("cors_origins", mode="before")
    @classmethod
    def assemble_cors(cls, v):
        if isinstance(v, str):
            # support comma-separated list in env
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = {
        "env_file": os.path.join(os.path.dirname(__file__), "..", "..", ".env"),
        "env_file_encoding": "utf-8"
    }


settings = Settings()

# Enforce presence of JWT secret in non-development environments
if settings.environment.lower() != "development" and not settings.jwt_secret:
    # For college project and development, use a secure default
    if os.getenv("COLLEGE_PROJECT", "false").lower() == "true":
        settings.jwt_secret = "agisfl-college-project-2025-secure-jwt-secret-key"
        logger.warning("Using college project JWT secret - change in production!")
    else:
        raise RuntimeError("JWT_SECRET must be set in non-development environments")