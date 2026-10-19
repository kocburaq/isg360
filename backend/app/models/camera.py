from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UTCDateTime, portable_enum
from app.models.enums import CameraStatus

if TYPE_CHECKING:
    from app.models.factory import FactoryZone
    from app.models.violation import PpeViolation


class Camera(TimestampMixin, Base):
    __tablename__ = "cameras"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    # Sahadaki etiket, ör. "CAM-01"
    code: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    zone_id: Mapped[str] = mapped_column(
        ForeignKey("factory_zones.id", ondelete="RESTRICT"), index=True
    )
    location: Mapped[str] = mapped_column(String(255), default="")
    status: Mapped[CameraStatus] = mapped_column(
        portable_enum(CameraStatus, "camera_status"), default=CameraStatus.UNKNOWN, index=True
    )
    last_seen_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)

    # Akış bilgileri. Gerçek RTSP adresi/kimlik bilgileri burada tutulmaz;
    # ileride ayrı ve şifreli bir yapılandırma alanında saklanacaktır.
    stream_protocol: Mapped[str] = mapped_column(String(16), default="rtsp")
    stream_configured: Mapped[bool] = mapped_column(Boolean, default=False)
    resolution: Mapped[str] = mapped_column(String(32), default="1920×1080")
    fps: Mapped[int] = mapped_column(Integer, default=25)

    # Denetlenen KKD sınıfları, ör. ["helmet", "vest"]
    ppe_classes: Mapped[list[str]] = mapped_column(JSON, default=lambda: ["helmet", "vest"])

    # True: durum ve kayıtlar simülasyon/örnek veridir, gerçek telemetri değildir.
    is_simulated: Mapped[bool] = mapped_column(Boolean, default=False)

    zone: Mapped["FactoryZone"] = relationship(back_populates="cameras", lazy="joined")
    violations: Mapped[list["PpeViolation"]] = relationship(back_populates="camera")
