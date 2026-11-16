from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import AppSettings, DbSession
from app.schemas.system import DashboardSummary, HealthOut
from app.services.system import SystemService

router = APIRouter()


@router.get("/health", response_model=HealthOut, tags=["Sistem"], summary="Sağlık kontrolü")
def health(db: DbSession, settings: AppSettings) -> HealthOut:
    return SystemService(db, settings).health()


@router.get(
    "/dashboard/summary",
    response_model=DashboardSummary,
    tags=["Panel"],
    summary="Kamera ve ihlal özet sayıları",
)
def dashboard_summary(
    db: DbSession,
    settings: AppSettings,
    factory_id: Annotated[
        str | None, Query(max_length=64, description="Fabrikaya göre filtre")
    ] = None,
) -> DashboardSummary:
    return SystemService(db, settings).dashboard_summary(factory_id)
