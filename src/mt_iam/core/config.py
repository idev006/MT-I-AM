"""Typed configuration. Production secrets come from environment/secret provider, never Git."""
from functools import lru_cache
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MT_IAM_", extra="ignore")
    app_name: str = "MT-IAM POC Lab"
    environment: str = Field(default="local", pattern=r"^(local|test|staging|production)$")
    issuer_url: str | None = None
    database_url: str | None = Field(default=None, repr=False)
    db_pool_size: int = Field(default=2, ge=1, le=20)
    db_max_overflow: int = Field(default=0, ge=0, le=20)
    db_pool_timeout: int = Field(default=10, ge=1, le=60)

    @model_validator(mode="after")
    def validate_production(self):
        if self.environment == "production":
            if not self.issuer_url or not self.issuer_url.startswith("https://"):
                raise ValueError("Production requires MT_IAM_ISSUER_URL using HTTPS")
            if self.database_url and not self.database_url.startswith("postgresql+psycopg://"):
                raise ValueError("Production requires PostgreSQL with psycopg")
        return self

@lru_cache
def get_settings() -> Settings:
    return Settings()
