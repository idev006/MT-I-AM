"""Typed configuration: never put database passwords or signing keys in the repo."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MT_IAM_", extra="ignore")

    app_name: str = "MT-IAM POC Lab"
    environment: str = Field(default="local", pattern="^(local|test|staging|production)$")
    # A production issuer must be HTTPS and controlled by the organization.
    issuer_url: str | None = None


@lru_cache
def get_settings() -> Settings:
    """Return process settings; tests may inject a different Settings instance."""
    return Settings()
