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
            violation_type=v.violation_type,
            missing=[PpeClass(p) for p in v.missing_ppe],
            detected_at=v.detected_at,
            confidence=v.confidence,
            severity=v.severity,
            status=v.status,
            source=v.source,
            description=v.description,
            reviewed_at=v.reviewed_at,
            created_at=v.created_at,
            updated_at=v.updated_at,
        )


class ViolationUpdate(PatchModel):
    status: ViolationStatus | None = None
    description: Annotated[str, Field(max_length=2000)] | None = None

    _nullable_fields: ClassVar[frozenset[str]] = frozenset({"description"})
