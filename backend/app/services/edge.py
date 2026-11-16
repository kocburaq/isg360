"""Edge (saha sunucusu) iş mantığı: kimlik doğrulama, olay alma, heartbeat, yapılandırma."""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from uuid import uuid4

from fcs_contracts import (
    EdgeCameraConfig,
    EdgeConfig,
    EdgeNodeInfo,
    EventBatch,
    EventBatchResult,
    EventResult,
    EventResultStatus,
    Heartbeat,
    HeartbeatResult,
    ViolationEvent,
)
from fcs_contracts.enums import EdgeCameraStatus
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.errors import ForbiddenError, UnauthorizedError
from app.core.security import hash_api_key, looks_like_api_key
from app.db.base import utcnow
from app.models import Camera, EdgeNode, PpeViolation
from app.models.enums import CameraStatus, ViolationStatus
from app.repositories.edge import EdgeNodeRepository, get_violation_by_event_id

logger = logging.getLogger(__name__)


def authenticate_edge_node(session: Session, api_key: str | None) -> EdgeNode:
    """Bearer anahtarından edge node'u bulur. Hatalı/eksik anahtar → 401, pasif node → 403."""
    if not api_key or not looks_like_api_key(api_key):
        raise UnauthorizedError("Geçerli bir edge API anahtarı gerekli.")
    node = EdgeNodeRepository(session).get_by_key_hash(hash_api_key(api_key))
    if node is None:
        raise UnauthorizedError("Geçerli bir edge API anahtarı gerekli.")
    if not node.is_active:
        raise ForbiddenError("Bu edge node devre dışı bırakılmış.")
    return node


class EdgeService:
    def __init__(self, session: Session, node: EdgeNode, settings: Settings) -> None:
        self.session = session
        self.node = node
        self.settings = settings
        self.nodes = EdgeNodeRepository(session)

    # --- Yapılandırma ---------------------------------------------------

    def build_config(self, now: datetime | None = None) -> EdgeConfig:
        cameras = [
            EdgeCameraConfig(
                id=c.id,
                code=c.code,
                name=c.name,
                zone_id=c.zone_id,
                ppe_classes=c.ppe_classes,  # type: ignore[arg-type]
                stream_configured=c.stream_configured,
            )
            for c in self.nodes.cameras_of(self.node.id)
        ]
        factory = self.node.factory
        node_info = EdgeNodeInfo(
            id=self.node.id,
            name=self.node.name,
            factory_id=factory.id,
            factory_name=factory.name,
            timezone=factory.timezone,
        )
        return EdgeConfig(
            node=node_info,
            cameras=cameras,
            config_version=self._version(node_info, cameras),
            generated_at=now or utcnow(),
        )

    def config_version(self) -> str:
        return self.build_config().config_version

    @staticmethod
    def _version(node: EdgeNodeInfo, cameras: list[EdgeCameraConfig]) -> str:
        payload = {
            "node": node.model_dump(mode="json"),
            "cameras": [c.model_dump(mode="json") for c in cameras],
        }
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()[:16]

    # --- Heartbeat ------------------------------------------------------

    def heartbeat(self, hb: Heartbeat, now: datetime | None = None) -> HeartbeatResult:
        now = now or utcnow()
        own = {c.id: c for c in self.nodes.cameras_of(self.node.id)}
        accepted, unknown = 0, []

        for cam_hb in hb.cameras:
            camera = own.get(cam_hb.camera_id)
            if camera is None:
                unknown.append(cam_hb.camera_id)
                continue
            accepted += 1
            camera.is_simulated = hb.simulated
            if cam_hb.status == EdgeCameraStatus.ONLINE:
                camera.status = CameraStatus.ONLINE
                # Son kare zamanı bildirildiyse o, yoksa heartbeat zamanı esas alınır
                camera.last_seen_at = min(cam_hb.last_frame_at or now, now)
            else:
                camera.status = CameraStatus.OFFLINE
                if cam_hb.last_frame_at is not None:
                    camera.last_seen_at = min(cam_hb.last_frame_at, now)

        self.node.last_seen_at = now
        self.node.software_version = hb.software_version
        self.node.reports_simulated = hb.simulated
        self.session.commit()

        if unknown:
            logger.warning("Edge %s bilinmeyen/atanmamış kamera bildirdi: %s", self.node.id, unknown)
        return HeartbeatResult(
            accepted_cameras=accepted,
            unknown_cameras=unknown,
            config_version=self.config_version(),
        )

    # --- Olaylar --------------------------------------------------------

    def ingest_events(self, batch: EventBatch, now: datetime | None = None) -> EventBatchResult:
        now = now or utcnow()
        own = {c.id: c for c in self.nodes.cameras_of(self.node.id)}
        results = [self._ingest_one(event, own, now) for event in batch.events]
        self.node.last_seen_at = now
        self.session.commit()
        return EventBatchResult(results=results)

    def _ingest_one(
        self, event: ViolationEvent, own: dict[str, Camera], now: datetime
    ) -> EventResult:
        event_id = str(event.event_id)

        def result(status: EventResultStatus, violation_id: str | None = None,
                   reason: str | None = None) -> EventResult:  # fmt: skip
            return EventResult(
                event_id=event.event_id, status=status, violation_id=violation_id, reason=reason
            )

        existing = get_violation_by_event_id(self.session, event_id)
        if existing is not None:
            return self._handle_resend(existing, event, result)

        camera = own.get(event.camera_id)
        if camera is None:
            return result(EventResultStatus.REJECTED, reason="camera_not_assigned")
        skew = timedelta(seconds=self.settings.edge_max_clock_skew_s)
        if event.started_at > now + skew or (event.ended_at and event.ended_at > now + skew):
            return result(EventResultStatus.REJECTED, reason="future_timestamp")

        violation = PpeViolation(
            id=f"vio-{uuid4().hex[:12]}",
            event_id=event_id,
            edge_node_id=self.node.id,
            camera_id=camera.id,
            zone_id=camera.zone_id,
            violation_type=event.violation_type,
            missing_ppe=[p.value for p in event.missing_ppe],
            detected_at=event.started_at,
            ended_at=event.ended_at,
            confidence=event.confidence,
            severity=event.severity,
            status=ViolationStatus.OPEN,
            source=event.source,
            description=event.description,
            rule_id=event.rule_id,
            track_id=event.track_id,
            model_ref=f"{event.model.id}@{event.model.version}" if event.model else None,
        )
        try:
            # Savepoint: eşzamanlı aynı olay gönderiminde yalnızca bu olay geri alınır
            with self.session.begin_nested():
                self.session.add(violation)
        except IntegrityError:
            existing = get_violation_by_event_id(self.session, event_id)
            if existing is None:
                raise
            return self._handle_resend(existing, event, result)
        return result(EventResultStatus.CREATED, violation_id=violation.id)

    def _handle_resend(self, existing: PpeViolation, event: ViolationEvent, result) -> EventResult:  # type: ignore[no-untyped-def]
        # Başka bir edge'in olay kimliğini kullanmak (çakışma veya kötüye kullanım) reddedilir
        if existing.edge_node_id != self.node.id:
            return result(EventResultStatus.REJECTED, reason="event_id_conflict")
        if event.ended_at is not None and existing.ended_at is None:
            existing.ended_at = max(event.ended_at, existing.detected_at)
            return result(EventResultStatus.UPDATED, violation_id=existing.id)
        return result(EventResultStatus.DUPLICATE, violation_id=existing.id)
