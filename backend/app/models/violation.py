from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import JSON, Float, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UTCDateTime, portable_enum
from app.models.enums import (
    DetectionSource,
    ViolationSeverity,
    ViolationStatus,
    ViolationType,
)

if TYPE_CHECKING:
    from app.models.camera import Camera


class PpeViolation(TimestampMixin, Base):
    __tablename__ = "ppe_violations"
    __table_args__ = (Index("ix_ppe_violations_status_detected", "status", "detected_at"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    # İhlal kaydı İSG geçmişidir: kaydı olan kamera silinemez (RESTRICT).
    camera_id: Mapped[str] = mapped_column(
        ForeignKey("cameras.id", ondelete="RESTRICT"), index=True
    )
    # Tespit anındaki bölge (kamera sonradan taşınsa bile kayıt doğru kalır)
    zone_id: Mapped[str] = mapped_column(ForeignKey("factory_zones.id", ondelete="RESTRICT"))

    violation_type: Mapped[ViolationType] = mapped_column(
        portable_enum(ViolationType, "violation_type"), default=ViolationType.MISSING_PPE
    )
    # Eksik tespit edilen KKD sınıfları, ör. ["helmet"]
    missing_ppe: Mapped[list[str]] = mapped_column(JSON)
    detected_at: Mapped[datetime] = mapped_column(UTCDateTime(), index=True)
    confidence: Mapped[float] = mapped_column(Float)
    severity: Mapped[ViolationSeverity] = mapped_column(
        portable_enum(ViolationSeverity, "violation_severity")
    )
    status: Mapped[ViolationStatus] = mapped_column(
        portable_enum(ViolationStatus, "violation_status"), default=ViolationStatus.OPEN
    )
    source: Mapped[DetectionSource] = mapped_column(
        portable_enum(DetectionSource, "detection_source"), default=DetectionSource.SIMULATION
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # İnceleme/çözüm zamanı (durum "open" dışına çıktığında dolar)
    reviewed_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)

    camera: Mapped["Camera"] = relationship(back_populates="violations")
