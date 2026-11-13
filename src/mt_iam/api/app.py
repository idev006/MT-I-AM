"""POC-only FastAPI application factory. No OAuth/OIDC/token endpoints."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from mt_iam.core.config import Settings, get_settings

def create_app(settings: Settings | None = None) -> FastAPI:
    cfg = settings if settings is not None else get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        db = None
        if cfg.database_url:
            from mt_iam.adapters.database import Database
            db = Database(cfg.database_url, pool_size=cfg.db_pool_size,
                          max_overflow=cfg.db_max_overflow, pool_timeout=cfg.db_pool_timeout)
        app.state.database = db
        app.state.ready = True
        try:
            yield
        finally:
            app.state.ready = False
            if db is not None:
                db.dispose()

    app = FastAPI(title=cfg.app_name, version="0.0.2", lifespan=lifespan,
                  docs_url=None if cfg.environment == "production" else "/docs")

    @app.get("/health/live", tags=["Operations"])
    async def live() -> dict[str, str]:
        return {"status": "alive"}

    @app.get("/health/ready", tags=["Operations"])
    async def ready() -> dict[str, str]:
        return {"status": "ready" if getattr(app.state, "ready", False) else "not-ready"}

    return app

app = create_app()
