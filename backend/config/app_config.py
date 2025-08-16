"""Application configuration using Pydantic BaseSettings.

Centralizes environment-driven configuration replacing the previous
inline dataclass-based AppConfig in `main.py`.
"""
from __future__ import annotations

try:
    from pydantic import BaseSettings
except Exception:  # pragma: no cover
    class BaseSettings:  # type: ignore
        def __init__(self, **data):
            for k, v in data.items():
                setattr(self, k, v)


class AppConfig(BaseSettings):
    log_level: str = "INFO"
    pretty_logs: bool = False
    jwt_secret: str = ""
    environment: str = "development"
    enable_metrics: bool = True
    rate_limit_max: int = 60

    class Config:
        case_sensitive = False
        env_prefix = ""  # keep variable names as-is
        fields = {
            "enable_metrics": {"env": "ENABLE_PROM_METRICS"},
            "pretty_logs": {"env": "PRETTY_LOGS"},
            "jwt_secret": {"env": "JWT_SECRET"},
            "rate_limit_max": {"env": "RATE_LIMIT_MAX"},
        }


app_config = AppConfig()
config = app_config  # backward alias
