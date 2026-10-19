"""Modüller arası paylaşılan fabrika yapısı (Kamera, Drone, İş Kartları aynı bölgeleri kullanır)."""

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.camera import Camera


class FactoryZone(TimestampMixin, Base):
    __tablename__ = "factory_zones"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    # Bina / blok / hol gibi üst konum bilgisi
    area: Mapped[str] = mapped_column(String(120))

    cameras: Mapped[list["Camera"]] = relationship(back_populates="zone")
