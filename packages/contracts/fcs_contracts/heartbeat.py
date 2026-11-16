"""Heartbeat: edge'in kendisinin ve kameralarının canlılık bildirimi (edge → merkez).

Merkez, belirli bir süre heartbeat almadığı kameraları çevrimdışı sayar.
"""

from typing import Annotated

from pydantic import Field

from fcs_contracts.base import AwareDatetime, ContractModel
from fcs_contracts.enums import EdgeCameraStatus
from fcs_contracts.events import Identifier


class CameraHeartbeat(ContractModel):
    camera_id: Identifier
    status: EdgeCameraStatus
    last_frame_at: AwareDatetime | None = None
    fps: Annotated[float, Field(ge=0, le=240)] | None = None
    error: Annotated[str, Field(max_length=300)] | None = None


class Heartbeat(ContractModel):
    sent_at: AwareDatetime
    software_version: Annotated[str, Field(min_length=1, max_length=32)]
    # true: edge gerçek kamera okumuyor (simülatör). Merkez bu bilgiyi kayıtlarda saklar
    # ve arayüz simülasyon verisini gerçek telemetri gibi göstermez.
    simulated: bool
    cameras: Annotated[list[CameraHeartbeat], Field(max_length=500)] = Field(default_factory=list)


class HeartbeatResult(ContractModel):
    accepted_cameras: int
    # Bu edge'e atanmamış veya bilinmeyen kameralar (yok sayıldı)
    unknown_cameras: list[str]
    # Edge, bu değer değiştiğinde yapılandırmayı yeniden çekmelidir
    config_version: str
