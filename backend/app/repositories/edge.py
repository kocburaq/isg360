"""Edge node ve fabrika veri erişimi."""

from datetime import datetime

from sqlalchemy import and_, func, select, update
from sqlalchemy.orm import Session

from app.models import Camera, EdgeNode, Factory, PpeViolation
from app.models.enums import CameraStatus


class FactoryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, factory_id: str) -> Factory | None:
        return self.session.get(Factory, factory_id)

    def list(self) -> list[Factory]:
        return list(self.session.scalars(select(Factory).order_by(Factory.code)))


class EdgeNodeRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, node_id: str) -> EdgeNode | None:
        return self.session.get(EdgeNode, node_id)

    def get_by_key_hash(self, key_hash: str) -> EdgeNode | None:
        return self.session.scalar(select(EdgeNode).where(EdgeNode.api_key_hash == key_hash))

    def list(self) -> list[EdgeNode]:
        return list(self.session.scalars(select(EdgeNode).order_by(EdgeNode.name)))

    def add(self, node: EdgeNode) -> EdgeNode:
        self.session.add(node)
        return node

    def cameras_of(self, node_id: str) -> list[Camera]:
        stmt = select(Camera).where(Camera.edge_node_id == node_id).order_by(Camera.code)
        return list(self.session.scalars(stmt).unique())

    def count_online(self, cutoff: datetime) -> tuple[int, int]:
        """(etkin node sayısı, cutoff'tan sonra görülen etkin node sayısı)"""
        active = self.session.scalar(
            select(func.count()).where(EdgeNode.is_active)
        ) or 0
        online = self.session.scalar(
            select(func.count()).where(EdgeNode.is_active, EdgeNode.last_seen_at >= cutoff)
        ) or 0
        return active, online


def get_violation_by_event_id(session: Session, event_id: str) -> PpeViolation | None:
    return session.scalar(select(PpeViolation).where(PpeViolation.event_id == event_id))


def mark_stale_cameras_offline(session: Session, cutoff: datetime) -> int:
    """Edge'e atanmış ve `cutoff`'tan beri sinyal alınmamış çevrimiçi kameraları çevrimdışı yapar.

    Heartbeat her çevrimiçi kamera için `last_seen_at` alanını yeniler; edge durursa
    bu alan eskir ve kamera burada çevrimdışına çekilir.
    """
    stmt = (
        update(Camera)
        .where(
            and_(
                Camera.edge_node_id.is_not(None),
                Camera.status == CameraStatus.ONLINE,
                (Camera.last_seen_at.is_(None)) | (Camera.last_seen_at < cutoff),
            )
        )
        .values(status=CameraStatus.OFFLINE)
        .execution_options(synchronize_session=False)
    )
    result = session.execute(stmt)
    session.commit()
    return result.rowcount or 0
