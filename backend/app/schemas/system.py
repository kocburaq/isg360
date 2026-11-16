from datetime import datetime
from typing import Literal

from app.schemas.common import ApiModel

ServiceState = Literal["operational", "degraded", "down", "simulated"]


class ServiceHealth(ApiModel):
    id: str
    label: str
    state: ServiceState
    detail: str


class HealthOut(ApiModel):
    """Sağlık kontrolü. `state`, `checkedAt` ve `services` frontend SystemStatus ile aynıdır."""

    status: Literal["ok", "error"]
    state: ServiceState
    version: str
    environment: str
    # Bu aşamada API'de kimlik doğrulama YOKTUR.
    authentication: Literal["none"] = "none"
    checked_at: datetime
    services: list[ServiceHealth]


class CameraCounts(ApiModel):
    total: int
    online: int
    offline: int
    unknown: int


class ViolationCounts(ApiModel):
    total: int
    today: int
    open: int
    acknowledged: int
    resolved: int


class DashboardSummary(ApiModel):
    cameras: CameraCounts
    violations: ViolationCounts
    generated_at: datetime
    timezone: str
    # Kayıtların simülasyon içerip içermediği (arayüz uyarısı için)
    contains_simulated_data: bool
