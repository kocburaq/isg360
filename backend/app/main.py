"""Factory Control System API — uygulama girişi.

UYARI: Panel API'sinde (/api/v1) henüz kullanıcı kimlik doğrulaması YOKTUR.
Yalnızca yerel geliştirme içindir: 127.0.0.1 üzerinde çalıştırın, ağa veya internete açmayın.
Edge API'si (/edge/v1) edge node başına API anahtarı ister.
"""

import asyncio
import contextlib
import logging
from collections.abc import AsyncIterator
from datetime import timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.edge.router import router as edge_router
from app.api.v1.router import api_router
from app.core.config import APP_VERSION, Settings, get_settings
from app.core.errors import register_exception_handlers
from app.db.base import utcnow
from app.db.session import get_session_factory
from app.repositories.edge import mark_stale_cameras_offline

logger = logging.getLogger(__name__)

EDGE_PREFIX = "/edge/v1"

DESCRIPTION = """
Factory Control System için yerel geliştirme API'si.

- **Panel API (`/api/v1`)**: kullanıcı kimlik doğrulaması yoktur. Yalnızca yerel geliştirme içindir;
  ağa veya internete açmayın.
- **Edge API (`/edge/v1`)**: saha sunucuları içindir; `Authorization: Bearer <edge API anahtarı>` gerekir.
  Anahtarlar `python -m app.cli.edge_nodes` komutuyla oluşturulur.

Seed kayıtları örnek (simülasyon) verilerdir; gerçek kamera veya YOLO modeli bağlı değildir.

Hata yanıtları her zaman şu biçimdedir:
`{"error": {"code": "...", "message": "...", "details": ...}}`
"""


async def _liveness_loop(settings: Settings) -> None:
    """Heartbeat'i kesilen edge kameralarını periyodik olarak çevrimdışına çeker."""
    interval = settings.edge_liveness_check_interval_s
    timeout = timedelta(seconds=settings.edge_heartbeat_timeout_s)
    while True:
        await asyncio.sleep(interval)
        try:

            def _sweep() -> int:
                with get_session_factory()() as session:
                    return mark_stale_cameras_offline(session, utcnow() - timeout)

            changed = await asyncio.to_thread(_sweep)
            if changed:
                logger.info("Heartbeat zaman aşımı: %d kamera çevrimdışı yapıldı", changed)
        except Exception:  # noqa: BLE001 — kontrol döngüsü hiçbir hatada durmamalı
            logger.exception("Canlılık kontrolü başarısız")


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    logging.basicConfig(level=logging.INFO)

    @contextlib.asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        task = None
        if settings.edge_liveness_check_interval_s > 0:
            task = asyncio.create_task(_liveness_loop(settings))
        yield
        if task:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

    app = FastAPI(
        title=settings.app_name,
        version=APP_VERSION,
        description=DESCRIPTION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.api_prefix}/openapi.json",
        lifespan=lifespan,
    )

    # Yalnızca yerel host adlarından gelen isteklere yanıt ver (ör. LAN IP'si üzerinden erişimi engeller)
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=[*settings.allowed_hosts, "testserver"]
    )
    # CORS yalnızca panel içindir; edge istekleri tarayıcıdan gelmez.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Accept"],
    )

    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_prefix)
    app.include_router(edge_router, prefix=EDGE_PREFIX)
    return app


app = create_app()
