"""Factory Control System API — uygulama girişi.

UYARI: Bu API'de henüz kimlik doğrulama/yetkilendirme YOKTUR.
Yalnızca yerel geliştirme içindir: 127.0.0.1 üzerinde çalıştırın, ağa veya internete açmayın.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1.router import api_router
from app.core.config import APP_VERSION, Settings, get_settings
from app.core.errors import register_exception_handlers

DESCRIPTION = """
Factory Control System için yerel geliştirme API'si.

**Kimlik doğrulama yoktur.** Bu sürüm yalnızca yerel geliştirme içindir; ağa veya internete açmayın.
Kamera ve ihlal kayıtları örnek (simülasyon) verileridir; gerçek kamera veya YOLO modeli bağlı değildir.

Hata yanıtları her zaman şu biçimdedir:
`{"error": {"code": "...", "message": "...", "details": ...}}`
"""


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    logging.basicConfig(level=logging.INFO)

    app = FastAPI(
        title=settings.app_name,
        version=APP_VERSION,
        description=DESCRIPTION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.api_prefix}/openapi.json",
    )

    # Yalnızca yerel host adlarından gelen isteklere yanıt ver (ör. LAN IP'si üzerinden erişimi engeller)
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=[*settings.allowed_hosts, "testserver"]
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Accept"],
    )

    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
