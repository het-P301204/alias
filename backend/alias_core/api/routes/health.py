from datetime import datetime, timezone
from fastapi import APIRouter
from alias_core.experiments.registry import registry
from alias_core.config.settings import settings
from alias_core.database.init_db import get_db

router = APIRouter()


@router.get("/health")
async def health():
    db_ok = False
    try:
        async with get_db() as db:
            await db.execute("SELECT 1")
            db_ok = True
    except Exception:
        pass

    return {
        "data": {
            "status": "ok",
            "version": settings.app_version,
            "scenarios_loaded": len(registry.all()),
            "db_ok": db_ok,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        "error": None,
        "meta": {},
    }
