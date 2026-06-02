from functools import lru_cache
import os
from pathlib import Path


def _load_dotenv() -> dict[str, str]:
    env_path = Path(".env")
    if not env_path.exists():
        return {}

    values: dict[str, str] = {}
    for line in env_path.read_text().splitlines():
        if not line or line.strip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


class Settings:
    def __init__(self) -> None:
        dotenv = _load_dotenv()

        self.database_url = os.getenv(
            "DATABASE_URL",
            dotenv.get(
                "DATABASE_URL",
                "postgresql+psycopg://jobs:jobs@localhost:5432/job_intelligence",
            ),
        )
        self.openrouter_api_key = (
            os.getenv("OPENROUTER_API_KEY", dotenv.get("OPENROUTER_API_KEY")) or None
        )
        self.openrouter_model = os.getenv(
            "OPENROUTER_MODEL",
            dotenv.get("OPENROUTER_MODEL", "deepseek/deepseek-chat"),
        )
        self.allowed_origins_raw = os.getenv(
            "ALLOWED_ORIGINS",
            dotenv.get("ALLOWED_ORIGINS", "http://localhost:3000"),
        )
        self.remoteok_user_agent = os.getenv(
            "REMOTEOK_USER_AGENT",
            dotenv.get("REMOTEOK_USER_AGENT", "CareerLens/1.0"),
        )
        self.onlinejobs_user_agent = os.getenv(
            "ONLINEJOBS_USER_AGENT",
            dotenv.get(
                "ONLINEJOBS_USER_AGENT",
                (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
            ),
        )

    @property
    def allowed_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins_raw.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
