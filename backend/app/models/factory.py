"""Fabrika yapısı: fabrika → bölgeler → kameralar."""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.camera import Camera
    from app.models.edge import EdgeNode


class Factory(TimestampMixin, Base):
    __tablename__ = "factories"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    # Kısa kod, ör. "F01"
    code: Mapped[str] = mapped_column(String(16), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    city: Mapped[str | None] = mapped_column(String(80), nullable=True)
    # Fabrikanın yerel saat dilimi ("bugün" hesapları ve raporlar için)
    timezone: Mapped[str] = mapped_column(String(64), default="Europe/Istanbul")

    zones: Mapped[list["FactoryZone"]] = relationship(back_populates="factory")
    edge_nodes: Mapped[list["EdgeNode"]] = relationship(back_populates="factory")


class FactoryZone(TimestampMixin, Base):
    __tablename__ = "factory_zones"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    factory_id: Mapped[str] = mapped_column(
        ForeignKey("factories.id", ondelete="RESTRICT"), index=True
    )
    name: Mapped[str] = mapped_column(String(120))
    # Bina / blok / hol gibi üst konum bilgisi
    area: Mapped[str] = mapped_column(String(120))

    factory: Mapped[Factory] = relationship(back_populates="zones", lazy="joined")
    cameras: Mapped[list["Camera"]] = relationship(back_populates="zone")
