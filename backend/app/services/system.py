"""Sağlık kontrolü ve panel özeti."""

import logging
from datetime import datetime, time

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import APP_VERSION, Settings
from app.db.base import utcnow
from app.models.enums import CameraStatus, ViolationStatus
from app.repositories.cameras import CameraRepository
from app.repositories.violations import ViolationRepository
from app.schemas.system import (
    CameraCounts,
    DashboardSummary,
    HealthOut,
    ServiceHealth,
    ViolationCounts,
)

logger = logging.getLogger(__name__)


def _overall(services: list[ServiceHealth]) -> str:
    states = {s.state for s in services}
    for state in ("down", "degraded", "simulated"):
        if state in states:
            return state
    return "operational"


class SystemService:
    def __init__(self, session: Session, settings: Settings) -> None:
        self.session = session
        self.settings = settings

    def _database_ok(self) -> bool:
        try:
            self.session.execute(text("SELECT 1"))
            return True
        except Exception:  # noqa: BLE001 — sağlık kontrolü hiçbir durumda çökmemeli
            logger.exception("Veritabanı sağlık kontrolü başarısız")
            return False

    def health(self) -> HealthOut:
        db_ok = self._database_ok()
        dialect = self.session.get_bind().dialect.name
        services = [
            ServiceHealth(
                id="api",
                label="Backend API (FastAPI)",
                state="operational",
                detail=f"Sürüm {APP_VERSION} · yerel geliştirme · kimlik doğrulama yok",
            ),
            ServiceHealth(
                id="database",
                label=f"Veritabanı ({dialect})",
                state="operational" if db_ok else "down",
                detail="Bağlantı başarılı." if db_ok else "Veritabanına erişilemiyor.",
            ),
            # Aşağıdakiler bu aşamada yoktur; dürüstçe "simülasyon" olarak raporlanır.
            ServiceHealth(
                id="inference",
                label="Görüntü işleme (YOLO)",
                state="simulated",
                detail="Model bağlı değil; ihlal kayıtları örnek veridir.",
            ),
            ServiceHealth(
                id="stream-gateway",
                label="Kamera akış ağ geçidi (RTSP)",
                state="simulated",
                detail="Gerçek kamera bağlantısı yapılandırılmadı.",
            ),
        ]
        return HealthOut(
            status="ok" if db_ok else "error",
            state=_overall(services),  # type: ignore[arg-type]
            version=APP_VERSION,
            environment=self.settings.app_env,
            checked_at=utcnow(),
            services=services,
        )

    def start_of_today(self) -> datetime:
        local_now = utcnow().astimezone(self.settings.tz)
        return datetime.combine(local_now.date(), time.min, tzinfo=self.settings.tz)

    def dashboard_summary(self) -> DashboardSummary:
        cameras = CameraRepository(self.session)
        violations = ViolationRepository(self.session)
        cam_counts = cameras.count_by_status()
        vio_counts = violations.count_by_status()

        return DashboardSummary(
            cameras=CameraCounts(
                total=sum(cam_counts.values()),
                online=cam_counts.get(CameraStatus.ONLINE, 0),
                offline=cam_counts.get(CameraStatus.OFFLINE, 0),
                unknown=cam_counts.get(CameraStatus.UNKNOWN, 0),
            ),
            violations=ViolationCounts(
                total=sum(vio_counts.values()),
                today=violations.count_since(self.start_of_today()),
                open=vio_counts.get(ViolationStatus.OPEN, 0),
                acknowledged=vio_counts.get(ViolationStatus.ACKNOWLEDGED, 0),
                resolved=vio_counts.get(ViolationStatus.RESOLVED, 0),
            ),
            generated_at=utcnow(),
            timezone=self.settings.app_timezone,
            contains_simulated_data=cameras.any_simulated() or violations.any_simulated(),
        )
