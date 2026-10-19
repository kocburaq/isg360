"""KKD ihlali iş mantığı."""

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.db.base import utcnow
from app.models import PpeViolation
from app.models.enums import ViolationStatus
from app.repositories.violations import ViolationFilter, ViolationRepository
from app.schemas.violation import ViolationUpdate


class ViolationService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.violations = ViolationRepository(session)

    def list(
        self, f: ViolationFilter, *, page: int, page_size: int
    ) -> tuple[list[PpeViolation], int]:
        return self.violations.list(f, offset=(page - 1) * page_size, limit=page_size)

    def get(self, violation_id: str) -> PpeViolation:
        violation = self.violations.get(violation_id)
        if violation is None:
            raise NotFoundError(f"İhlal kaydı bulunamadı: {violation_id}")
        return violation

    def update(self, violation_id: str, data: ViolationUpdate) -> PpeViolation:
        violation = self.get(violation_id)
        changes = data.changes()

        new_status = changes.get("status")
        if new_status is not None and new_status != violation.status:
            violation.status = new_status
            # İnceleme zamanı: açık durumdan çıkınca işaretlenir, yeniden açılırsa temizlenir.
            if new_status == ViolationStatus.OPEN:
                violation.reviewed_at = None
            elif violation.reviewed_at is None:
                violation.reviewed_at = utcnow()

        if "description" in changes:
            violation.description = changes["description"]

        self.session.commit()
        self.session.refresh(violation)
        return violation
