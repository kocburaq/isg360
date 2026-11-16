"""KKD ihlali veri erişimi."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.orm import Session

from app.models import PpeViolation
from app.models.enums import (
    DetectionSource,
    PpeClass,
    ViolationSeverity,
    ViolationStatus,
    ViolationType,
)
from app.repositories.cameras import zone_ids_of


@dataclass(frozen=True)
class ViolationFilter:
    camera_id: str | None = None
    factory_id: str | None = None
    zone_id: str | None = None
    statuses: Sequence[ViolationStatus] = ()
    types: Sequence[ViolationType] = ()
    severities: Sequence[ViolationSeverity] = ()
    ppe: Sequence[PpeClass] = ()
    detected_from: datetime | None = None
    detected_to: datetime | None = None
    newest_first: bool = True


class ViolationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def _filtered(self, f: ViolationFilter):  # type: ignore[no-untyped-def]
        stmt = select(PpeViolation)
        if f.camera_id:
            stmt = stmt.where(PpeViolation.camera_id == f.camera_id)
        if f.factory_id:
            stmt = stmt.where(PpeViolation.zone_id.in_(zone_ids_of(f.factory_id)))
        if f.zone_id:
            stmt = stmt.where(PpeViolation.zone_id == f.zone_id)
        if f.statuses:
            stmt = stmt.where(PpeViolation.status.in_(f.statuses))
        if f.types:
            stmt = stmt.where(PpeViolation.violation_type.in_(f.types))
        if f.severities:
            stmt = stmt.where(PpeViolation.severity.in_(f.severities))
        if f.ppe:
            # JSON dizisinde arama; SQLite ve PostgreSQL'de aynı çalışan taşınabilir yöntem.
            # Değerler enum ile doğrulandığı ve parametre olarak bağlandığı için güvenlidir.
            missing_text = cast(PpeViolation.missing_ppe, String)
            stmt = stmt.where(or_(*(missing_text.like(f'%"{p.value}"%') for p in f.ppe)))
        if f.detected_from:
            stmt = stmt.where(PpeViolation.detected_at >= f.detected_from)
        if f.detected_to:
            stmt = stmt.where(PpeViolation.detected_at <= f.detected_to)
        return stmt

    def list(
        self, f: ViolationFilter, *, offset: int, limit: int
    ) -> tuple[list[PpeViolation], int]:
        stmt = self._filtered(f)
        total = self.session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        order = PpeViolation.detected_at.desc() if f.newest_first else PpeViolation.detected_at
        items = self.session.scalars(
            stmt.order_by(order, PpeViolation.id).offset(offset).limit(limit)
        )
        return list(items), total

    def get(self, violation_id: str) -> PpeViolation | None:
        return self.session.get(PpeViolation, violation_id)

    def exists_for_camera(self, camera_id: str) -> bool:
        stmt = select(func.count()).where(PpeViolation.camera_id == camera_id)
        return bool(self.session.scalar(stmt))

    @staticmethod
    def _in_factory(stmt, factory_id: str | None):  # type: ignore[no-untyped-def]
        if factory_id:
            return stmt.where(PpeViolation.zone_id.in_(zone_ids_of(factory_id)))
        return stmt

    def count_by_status(self, factory_id: str | None = None) -> dict[ViolationStatus, int]:
        stmt = select(PpeViolation.status, func.count()).group_by(PpeViolation.status)
        rows = self.session.execute(self._in_factory(stmt, factory_id))
        return {status: count for status, count in rows}

    def count_since(self, since: datetime, factory_id: str | None = None) -> int:
        stmt = select(func.count()).where(PpeViolation.detected_at >= since)
        return self.session.scalar(self._in_factory(stmt, factory_id)) or 0

    def any_simulated(self, factory_id: str | None = None) -> bool:
        stmt = select(func.count()).where(PpeViolation.source == DetectionSource.SIMULATION)
        return bool(self.session.scalar(self._in_factory(stmt, factory_id)))
