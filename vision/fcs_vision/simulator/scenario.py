"""Tekrarlanabilir (seed'li) sahte olay ve kamera durumu üreteci."""

import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import UUID

from fcs_contracts import (
    CameraHeartbeat,
    DetectionSource,
    EdgeCameraConfig,
    EdgeCameraStatus,
    PpeClass,
    ViolationEvent,
    ViolationSeverity,
    ViolationType,
)

# İhlal türlerinin görülme ağırlıkları (KKD eksikliği en sık)
TYPE_WEIGHTS = {
    ViolationType.MISSING_PPE: 0.7,
    ViolationType.RESTRICTED_AREA: 0.2,
    ViolationType.MISSING_HARNESS: 0.1,
}

DESCRIPTIONS = {
    ViolationType.MISSING_PPE: "Saha simülatörü: KKD eksikliği (simüle)",
    ViolationType.RESTRICTED_AREA: "Saha simülatörü: yasaklı bölgeye giriş (simüle)",
    ViolationType.MISSING_HARNESS: "Saha simülatörü: yüksekte emniyet kemeri yok (simüle)",
}


@dataclass
class OngoingViolation:
    event: ViolationEvent
    ends_at: datetime


@dataclass
class Scenario:
    """Her `tick` çağrısında yeni olaylar ve biten ihlaller için güncellemeler üretir.

    - `event_probability`: her çevrimiçi kamera için bir tick'te yeni ihlal olasılığı
    - `offline_cameras`: sürekli çevrimdışı bildirilecek kameralar (test/gösterim için)
    """

    seed: int | None = None
    event_probability: float = 0.05
    min_duration_s: int = 5
    max_duration_s: int = 60
    offline_cameras: frozenset[str] = frozenset()
    rng: random.Random = field(init=False)
    ongoing: list[OngoingViolation] = field(default_factory=list, init=False)
    _track_counter: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        if not 0 <= self.event_probability <= 1:
            raise ValueError("event_probability 0 ile 1 arasında olmalıdır.")
        self.rng = random.Random(self.seed)

    def camera_heartbeats(
        self, cameras: list[EdgeCameraConfig], now: datetime
    ) -> list[CameraHeartbeat]:
        beats = []
        for cam in cameras:
            if cam.id in self.offline_cameras:
                beats.append(
                    CameraHeartbeat(
                        camera_id=cam.id,
                        status=EdgeCameraStatus.OFFLINE,
                        error="Simüle edilmiş bağlantı kesintisi",
                    )
                )
            else:
                beats.append(
                    CameraHeartbeat(
                        camera_id=cam.id,
                        status=EdgeCameraStatus.ONLINE,
                        last_frame_at=now,
                        fps=round(self.rng.uniform(4.5, 5.5), 1),
                    )
                )
        return beats

    def tick(self, cameras: list[EdgeCameraConfig], now: datetime) -> list[ViolationEvent]:
        """Biten ihlallerin güncellemelerini ve yeni ihlalleri döner."""
        events: list[ViolationEvent] = []

        still_ongoing = []
        for item in self.ongoing:
            if item.ends_at <= now:
                events.append(item.event.model_copy(update={"ended_at": item.ends_at}))
            else:
                still_ongoing.append(item)
        self.ongoing = still_ongoing

        for cam in cameras:
            if cam.id in self.offline_cameras or self.rng.random() >= self.event_probability:
                continue
            event = self._new_event(cam, now)
            duration = timedelta(seconds=self.rng.randint(self.min_duration_s, self.max_duration_s))
            self.ongoing.append(OngoingViolation(event, now + duration))
            events.append(event)
        return events

    def _new_event(self, cam: EdgeCameraConfig, now: datetime) -> ViolationEvent:
        vtype = self.rng.choices(list(TYPE_WEIGHTS), weights=list(TYPE_WEIGHTS.values()))[0]
        missing: list[PpeClass] = []
        if vtype == ViolationType.MISSING_PPE:
            classes = list(cam.ppe_classes) or [PpeClass.HELMET]
            missing = self.rng.sample(classes, k=self.rng.randint(1, len(classes)))

        if vtype == ViolationType.MISSING_PPE:
            severity = (
                ViolationSeverity.HIGH
                if PpeClass.HELMET in missing or len(missing) > 1
                else ViolationSeverity.MEDIUM
            )
        else:
            severity = ViolationSeverity.HIGH

        self._track_counter += 1
        return ViolationEvent(
            event_id=UUID(int=self.rng.getrandbits(128), version=4),
            camera_id=cam.id,
            violation_type=vtype,
            missing_ppe=missing,
            started_at=now,
            confidence=round(self.rng.uniform(0.6, 0.98), 2),
            severity=severity,
            source=DetectionSource.SIMULATION,
            rule_id=f"sim-{vtype.value}",
            track_id=f"sim-trk-{self._track_counter}",
            description=DESCRIPTIONS[vtype],
        )
