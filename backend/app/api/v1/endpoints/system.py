from fastapi import APIRouter

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
def dashboard_summary(db: DbSession, settings: AppSettings) -> DashboardSummary:
    return SystemService(db, settings).dashboard_summary()
