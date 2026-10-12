from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# settings.py is at backend/alias_core/config/settings.py → parents[3] = repo root
_REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ALIAS_", env_file=".env", extra="ignore")

    app_version: str = "0.1.0"
    debug: bool = False

    host: str = "127.0.0.1"
    port: int = 8000

    db_path: str = str(_REPO_ROOT / "alias.db")

    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    max_query_depth: int = 10
    max_complexity: int = 1000
    max_batch_operations: int = 10
    max_response_size: int = 1_048_576
    max_concurrent_experiments: int = 3
    experiment_timeout_seconds: int = 30

    log_level: str = "INFO"


settings = Settings()
