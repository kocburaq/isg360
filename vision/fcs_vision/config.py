"""Edge servisi ayarları (ortam değişkenleri / .env)."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

VISION_DIR = Path(__file__).resolve().parents[1]


class EdgeSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=VISION_DIR / ".env",
        env_file_encoding="utf-8",
        env_prefix="EDGE_",
        extra="ignore",
    )

    api_url: str = "http://127.0.0.1:8000/edge/v1"
    # SecretStr: anahtar günlüklere veya hata mesajlarına yanlışlıkla yazılmaz
    api_key: SecretStr = SecretStr("")
    outbox_path: Path = Path("./data/outbox.db")
    heartbeat_interval_s: float = Field(default=10, ge=1, le=300)
    http_timeout_s: float = Field(default=10, ge=1, le=120)

    @field_validator("api_url")
    @classmethod
    def _strip_slash(cls, value: str) -> str:
        return value.rstrip("/")

    @property
    def resolved_outbox_path(self) -> Path:
        path = self.outbox_path
        if not path.is_absolute():
            path = (VISION_DIR / path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> EdgeSettings:
    return EdgeSettings()
