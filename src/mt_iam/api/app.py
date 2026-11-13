"""POC ASGI application: safe health checks, NOT an OIDC server."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from mt_iam.core.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create isolated ASGI application for tests and future dependency injection."""

    resolved_settings = settings if settings is not None else get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.ready = True
        try:
            yield
        finally:
            app.state.ready = False

    app = FastAPI(
        title=resolved_settings.app_name,
        version="0.0.1",
        lifespan=lifespan,
        docs_url=None if resolved_settings.environment == "production" else "/docs",
    )

    @app.get("/health/live", tags=["Operations"])
    async def live() -> dict[str, str]:
        return {"status": "alive"}

    @app.get("/health/ready", tags=["Operations"])
    async def ready() -> dict[str, str]:
        return {"status": "ready" if app.state.ready else "not-ready"}

    return app


app = create_app()
