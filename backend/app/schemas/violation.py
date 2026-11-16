from datetime import datetime
from typing import Annotated, ClassVar, Literal

from pydantic import Field

from app.models import PpeViolation
from app.models.enums import (
    DetectionSource,
    PpeClass,
    ViolationSeverity,
    ViolationStatus,
    ViolationType,
)
from app.schemas.common import ApiModel, PatchModel


class EntityRef(ApiModel):
    """Başka bir modüldeki kayda referans (ör. düzeltici faaliyet iş kartı)."""

    module: Literal["cameras", "work-orders", "drones"]
    id: str


class ViolationOut(ApiModel):
    id: str
    camera_id: str
    zone_id: str
    factory_id: str
    violation_type: ViolationType
    # Eksik tespit edilen KKD sınıfları (frontend: `missing`)
    missing: list[PpeClass]
    detected_at: datetime
    confidence: float
    severity: ViolationSeverity
    status: ViolationStatus
    source: DetectionSource
    description: str | None
    reviewed_at: datetime | None
    # İhlalin bittiği zaman (süren veya bitişi bilinmeyen ihlallerde null)
    ended_at: datetime | None
    # Edge kaynaklı olay bilgileri (seed/elle girilen kayıtlarda null)
    event_id: str | None
    edge_node_id: str | None
    rule_id: str | None
    track_id: str | None
    model_ref: str | None
    # İş Kartları modülü geldiğinde doldurulacak
    links: list[EntityRef] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, v: PpeViolation) -> "ViolationOut":
        return cls(
            id=v.id,
            camera_id=v.camera_id,
            zone_id=v.zone_id,
            factory_id=v.zone.factory_id,
            violation_type=v.violation_type,
            missing=[PpeClass(p) for p in v.missing_ppe],
            detected_at=v.detected_at,
            confidence=v.confidence,
            severity=v.severity,
            status=v.status,
            source=v.source,
            description=v.description,
            reviewed_at=v.reviewed_at,
            ended_at=v.ended_at,
            event_id=v.event_id,
            edge_node_id=v.edge_node_id,
            rule_id=v.rule_id,
            track_id=v.track_id,
            model_ref=v.model_ref,
            created_at=v.created_at,
            updated_at=v.updated_at,
        )


class ViolationUpdate(PatchModel):
    status: ViolationStatus | None = None
    description: Annotated[str, Field(max_length=2000)] | None = None

    _nullable_fields: ClassVar[frozenset[str]] = frozenset({"description"})
