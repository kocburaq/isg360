"""İhlal olayları: edge → merkez.

Her olay edge tarafında üretilen benzersiz `eventId` taşır. Merkez bu kimliği
idempotency anahtarı olarak kullanır: ağ kopup aynı olay tekrar gönderilse bile
tek kayıt oluşur. Süren bir ihlal bittiğinde aynı `eventId` `endedAt` ile tekrar
gönderilir; merkez mevcut kaydı günceller.
"""

from enum import StrEnum
from typing import Annotated, Self
from uuid import UUID

from pydantic import Field, model_validator

from fcs_contracts.base import AwareDatetime, ContractModel
from fcs_contracts.enums import DetectionSource, PpeClass, ViolationSeverity, ViolationType

MAX_EVENTS_PER_BATCH = 100

Identifier = Annotated[str, Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9._:-]+$")]


class ModelRef(ContractModel):
    """Olayı üreten modelin kimliği ve sürümü (model kaydı ile eşleşir)."""

    id: Identifier
    version: Annotated[str, Field(min_length=1, max_length=32)]


class ViolationEvent(ContractModel):
    event_id: UUID
    camera_id: Identifier
    violation_type: ViolationType
    # Yalnızca missing_ppe türünde dolu olmalıdır
    missing_ppe: Annotated[list[PpeClass], Field(max_length=10)] = Field(default_factory=list)
    started_at: AwareDatetime
    ended_at: AwareDatetime | None = None
    confidence: Annotated[float, Field(ge=0, le=1)]
    severity: ViolationSeverity
    source: DetectionSource
    rule_id: Identifier | None = None
    # Edge'deki kişi takip kimliği (aynı kişinin olaylarını ilişkilendirmek için)
    track_id: Identifier | None = None
    model: ModelRef | None = None
    description: Annotated[str, Field(max_length=500)] | None = None

    @model_validator(mode="after")
    def _check_consistency(self) -> Self:
        if self.violation_type == ViolationType.MISSING_PPE and not self.missing_ppe:
            raise ValueError("missing_ppe türündeki olaylarda en az bir KKD sınıfı gerekir.")
        if self.violation_type != ViolationType.MISSING_PPE and self.missing_ppe:
            raise ValueError("missingPpe yalnızca missing_ppe türündeki olaylarda kullanılır.")
        if len(set(self.missing_ppe)) != len(self.missing_ppe):
            raise ValueError("missingPpe tekrar eden değer içeremez.")
        if self.ended_at is not None and self.ended_at < self.started_at:
            raise ValueError("endedAt, startedAt'tan önce olamaz.")
        if self.source == DetectionSource.MODEL and self.model is None:
            raise ValueError("Model kaynaklı olaylar model bilgisi (model) içermelidir.")
        return self


class EventBatch(ContractModel):
    events: Annotated[list[ViolationEvent], Field(min_length=1, max_length=MAX_EVENTS_PER_BATCH)]

    @model_validator(mode="after")
    def _unique_ids(self) -> Self:
        ids = [e.event_id for e in self.events]
        if len(ids) != len(set(ids)):
            raise ValueError("Aynı istekte eventId tekrar edemez.")
        return self


class EventResultStatus(StrEnum):
    CREATED = "created"
    # Daha önce alınmış olay (tekrar gönderim) — yeniden denemeye gerek yok
    DUPLICATE = "duplicate"
    # Daha önce alınmış olay, bitiş zamanı güncellendi
    UPDATED = "updated"
    # Kalıcı olarak reddedildi (ör. kamera bu edge'e ait değil) — yeniden denenmemeli
    REJECTED = "rejected"


class EventResult(ContractModel):
    event_id: UUID
    status: EventResultStatus
    violation_id: str | None = None
    reason: str | None = None


class EventBatchResult(ContractModel):
    results: list[EventResult]

    def count(self, status: EventResultStatus) -> int:
        return sum(1 for r in self.results if r.status == status)
