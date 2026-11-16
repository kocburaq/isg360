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
    from app.models.factory import FactoryZone


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
    # Eksik tespit edilen KKD sınıfları, ör. ["helmet"]; diğer türlerde boş liste
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

    # --- Edge kaynaklı olay bilgileri (seed/elle girilen kayıtlarda boş) ---
    # Edge'in ürettiği benzersiz olay kimliği: tekrar gönderimde çift kayıt oluşmaz
    event_id: Mapped[str | None] = mapped_column(String(36), unique=True, nullable=True)
    edge_node_id: Mapped[str | None] = mapped_column(
        ForeignKey("edge_nodes.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    # İhlalin sona erdiği zaman (süren ihlallerde boş)
    ended_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)
    # Kural motoru (3.2) kural kimliği ve edge'deki kişi takip kimliği
    rule_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    track_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    # Olayı üreten model, ör. "ppe-detector@1.0.0"
    model_ref: Mapped[str | None] = mapped_column(String(100), nullable=True)

    camera: Mapped["Camera"] = relationship(back_populates="violations")
    zone: Mapped["FactoryZone"] = relationship(lazy="joined")
