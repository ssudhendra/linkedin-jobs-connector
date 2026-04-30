from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    host: str = os.getenv("LINKEDIN_CONNECTOR_HOST", "127.0.0.1")
    port: int = int(os.getenv("LINKEDIN_CONNECTOR_PORT", "8765"))
    default_limit: int = int(os.getenv("LINKEDIN_CONNECTOR_DEFAULT_LIMIT", "50"))
    max_limit: int = int(os.getenv("LINKEDIN_CONNECTOR_MAX_LIMIT", "100"))
    cache_ttl_seconds: int = int(os.getenv("LINKEDIN_CONNECTOR_CACHE_TTL_SECONDS", "300"))
    provider_timeout_seconds: float = float(os.getenv("LINKEDIN_CONNECTOR_PROVIDER_TIMEOUT_SECONDS", "5"))
    provider_retries: int = int(os.getenv("LINKEDIN_CONNECTOR_PROVIDER_RETRIES", "2"))
    linkedin_client_id: str = os.getenv("LINKEDIN_CLIENT_ID", "")
    linkedin_client_secret: str = os.getenv("LINKEDIN_CLIENT_SECRET", "")
    linkedin_redirect_uri: str = os.getenv("LINKEDIN_REDIRECT_URI", "http://127.0.0.1:8787/callback")
    linkedin_scopes: str = os.getenv("LINKEDIN_SCOPES", "openid profile email")


SETTINGS = Settings()
