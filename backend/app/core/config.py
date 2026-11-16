"""Uygulama yapılandırması (ortam değişkenleri / .env)."""

from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal
from zoneinfo import ZoneInfo

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]

APP_VERSION = "0.2.0"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Factory Control System API"
    # Gerçek kimlik doğrulama yok: yalnızca yerel geliştirme ve test ortamları desteklenir.
    app_env: Literal["development", "test"] = "development"
    api_prefix: str = "/api/v1"

    database_url: str = "sqlite:///./data/fcs_dev.db"
    db_echo: bool = False

    cors_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    allowed_hosts: Annotated[list[str], NoDecode] = ["localhost", "127.0.0.1"]

    app_timezone: str = "Europe/Istanbul"

    # --- Edge (saha sunucusu) ---
    # Bu süre boyunca heartbeat gelmeyen, edge'e atanmış kameralar çevrimdışı sayılır
    edge_heartbeat_timeout_s: int = Field(default=60, ge=10, le=3600)
    # Canlılık kontrolünün çalışma aralığı (0: arka plan kontrolü kapalı, ör. testlerde)
    edge_liveness_check_interval_s: int = Field(default=15, ge=0, le=600)
    # Edge saatinin merkezden en fazla bu kadar ileride olmasına izin verilir
    edge_max_clock_skew_s: int = Field(default=300, ge=0, le=3600)

    @field_validator("cors_origins", "allowed_hosts", mode="before")
    @classmethod
    def _split_csv(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("cors_origins")
    @classmethod
    def _no_wildcard_origin(cls, value: list[str]) -> list[str]:
        if "*" in value:
            raise ValueError("CORS_ORIGINS '*' olamaz; izin verilen origin'leri tek tek yazın.")
        return value

    @field_validator("app_timezone")
    @classmethod
    def _valid_timezone(cls, value: str) -> str:
        ZoneInfo(value)  # geçersizse hata fırlatır
        return value

    @property
    def tz(self) -> ZoneInfo:
        return ZoneInfo(self.app_timezone)

    @property
    def resolved_database_url(self) -> str:
        """Göreli SQLite yollarını backend klasörüne göre çözer (çalışma dizininden bağımsız)."""
        prefix = "sqlite:///"
        if self.database_url.startswith(prefix) and not self.database_url.startswith(
            prefix + "/"
        ):
            raw = self.database_url[len(prefix) :]
            if raw != ":memory:" and not Path(raw).is_absolute():
                path = (BACKEND_DIR / raw).resolve()
                path.parent.mkdir(parents=True, exist_ok=True)
                return f"{prefix}{path.as_posix()}"
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
