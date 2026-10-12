"""ALIAS FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from alias_core.config.settings import settings
from alias_core.database.init_db import init_db
from alias_core.experiments.registry import registry
from alias_core.api.middleware import add_middleware
from alias_core.api.routes.health import router as health_router
from alias_core.api.routes.scenarios import router as scenarios_router
from alias_core.api.routes.experiments import router as experiments_router
from alias_core.api.routes.defenses import router as defenses_router
from alias_core.api.routes.reports import router as reports_router
from alias_core.graphql.lab_router import lab_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    registry.discover()
    yield


app = FastAPI(
    title="ALIAS — GraphQL Security Research Platform",
    version=settings.app_version,
    lifespan=lifespan,
)

add_middleware(app)

app.include_router(health_router, prefix="/api")
app.include_router(scenarios_router, prefix="/api")
app.include_router(experiments_router, prefix="/api")
app.include_router(defenses_router, prefix="/api")
app.include_router(reports_router, prefix="/api")
app.include_router(lab_router, prefix="/lab")


def run() -> None:
    import uvicorn
    uvicorn.run(
        "alias_core.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    run()
