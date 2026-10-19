"""Kamera ve bölge veri erişimi. Tüm sorgular parametreli SQLAlchemy ifadeleridir."""

from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import Camera, FactoryZone
from app.models.enums import CameraStatus


@dataclass(frozen=True)
class CameraFilter:
    statuses: Sequence[CameraStatus] = ()
    zone_id: str | None = None
    search: str | None = None


class ZoneRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, zone_id: str) -> FactoryZone | None:
        return self.session.get(FactoryZone, zone_id)

    def list(self) -> list[FactoryZone]:
        return list(self.session.scalars(select(FactoryZone).order_by(FactoryZone.name)))


class CameraRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def _filtered(self, f: CameraFilter):  # type: ignore[no-untyped-def]
        stmt = select(Camera)
        if f.statuses:
            stmt = stmt.where(Camera.status.in_(f.statuses))
        if f.zone_id:
            stmt = stmt.where(Camera.zone_id == f.zone_id)
        if f.search:
            pattern = f"%{f.search.lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(Camera.code).like(pattern),
                    func.lower(Camera.name).like(pattern),
                    func.lower(Camera.location).like(pattern),
                )
            )
        return stmt

    def list(self, f: CameraFilter, *, offset: int, limit: int) -> tuple[list[Camera], int]:
        stmt = self._filtered(f)
        total = self.session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = self.session.scalars(stmt.order_by(Camera.code).offset(offset).limit(limit))
        return list(items.unique()), total

    def get(self, camera_id: str) -> Camera | None:
        return self.session.get(Camera, camera_id)

    def get_by_code(self, code: str) -> Camera | None:
        return self.session.scalar(select(Camera).where(func.lower(Camera.code) == code.lower()))

    def add(self, camera: Camera) -> Camera:
        self.session.add(camera)
        return camera

    def delete(self, camera: Camera) -> None:
        self.session.delete(camera)

    def count_by_status(self) -> dict[CameraStatus, int]:
        rows = self.session.execute(select(Camera.status, func.count()).group_by(Camera.status))
        return {status: count for status, count in rows}

    def any_simulated(self) -> bool:
        return bool(self.session.scalar(select(func.count()).where(Camera.is_simulated)))
