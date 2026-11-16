"""Saha sunucuları (edge node): her fabrikada kameraları okuyup analiz eden servis."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UTCDateTime

if TYPE_CHECKING:
    from app.models.camera import Camera
    from app.models.factory import Factory


class EdgeNode(TimestampMixin, Base):
    __tablename__ = "edge_nodes"

    id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=lambda: f"edge-{uuid4().hex[:12]}"
    )
    factory_id: Mapped[str] = mapped_column(
        ForeignKey("factories.id", ondelete="RESTRICT"), index=True
    )
    name: Mapped[str] = mapped_column(String(120))

    # API anahtarının kendisi SAKLANMAZ; yalnızca SHA-256 özeti tutulur.
    # Anahtar yüksek entropili rastgele bir değer olduğundan yavaş hash gerekmez.
    api_key_hash: Mapped[str] = mapped_column(String(64), unique=True)
    # Anahtarı tanımak için ilk birkaç karakter (ör. günlüklerde, CLI çıktısında)
    api_key_prefix: Mapped[str] = mapped_column(String(16))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    last_seen_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)
    software_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    # Son heartbeat'te edge'in simülatör olduğunu bildirip bildirmediği
    reports_simulated: Mapped[bool] = mapped_column(Boolean, default=False)

    factory: Mapped["Factory"] = relationship(back_populates="edge_nodes", lazy="joined")
    cameras: Mapped[list["Camera"]] = relationship(back_populates="edge_node")
