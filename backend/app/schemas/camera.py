from datetime import datetime
from typing import Annotated, ClassVar, Literal

from pydantic import Field, field_validator

from app.models import Camera
from app.models.enums import CameraStatus, PpeClass
from app.schemas.common import ApiModel, PatchModel, RequestModel

CameraCode = Annotated[
    str,
    Field(
        min_length=2,
        max_length=32,
        pattern=r"^[A-Za-z0-9_-]+$",
        description="Saha etiketi, ör. CAM-07",
    ),
]
CameraName = Annotated[str, Field(min_length=1, max_length=120)]
Location = Annotated[str, Field(max_length=255)]
ZoneId = Annotated[str, Field(min_length=1, max_length=64)]
PpeClassList = Annotated[list[PpeClass], Field(min_length=1, max_length=10)]


def _unique(values: list[PpeClass]) -> list[PpeClass]:
    return list(dict.fromkeys(values))


class FactoryOut(ApiModel):
    id: str
    code: str
    name: str
    city: str | None
    timezone: str


class FactoryRef(ApiModel):
    id: str
    code: str
    name: str


class ZoneOut(ApiModel):
    id: str
    factory_id: str
    name: str
    area: str


class StreamInfo(ApiModel):
    protocol: Literal["rtsp"]
    # Gerçek bağlantı yapılandırılmadıysa false (bu aşamada her zaman false)
    configured: bool
    resolution: str
    fps: int


class StreamInput(RequestModel):
    resolution: Annotated[str, Field(min_length=3, max_length=32)] = "1920×1080"
    fps: Annotated[int, Field(ge=1, le=120)] = 25


class CameraOut(ApiModel):
    id: str
    code: str
    name: str
    factory: FactoryRef
    zone: ZoneOut
    location: str
    status: CameraStatus
    last_seen_at: datetime | None
    stream: StreamInfo
    ppe_classes: list[PpeClass]
    is_simulated: bool = Field(
        description="true ise durum ve kayıtlar simülasyondur; gerçek telemetri değildir."
    )
    # Kamerayı okuyan saha sunucusu; atanmışsa durum heartbeat'ten gelir
    edge_node_id: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, camera: Camera) -> "CameraOut":
        return cls(
            id=camera.id,
            code=camera.code,
            name=camera.name,
            factory=FactoryRef.model_validate(camera.zone.factory),
            zone=ZoneOut.model_validate(camera.zone),
            location=camera.location,
            status=camera.status,
            last_seen_at=camera.last_seen_at,
            stream=StreamInfo(
                protocol="rtsp",
                configured=camera.stream_configured,
                resolution=camera.resolution,
                fps=camera.fps,
            ),
            ppe_classes=[PpeClass(p) for p in camera.ppe_classes],
            is_simulated=camera.is_simulated,
            edge_node_id=camera.edge_node_id,
            created_at=camera.created_at,
            updated_at=camera.updated_at,
        )


class CameraCreate(RequestModel):
    code: CameraCode
    name: CameraName
    zone_id: ZoneId
    location: Location = ""
    # Gerçek telemetri olmadığından varsayılan "unknown"
    status: CameraStatus = CameraStatus.UNKNOWN
    stream: StreamInput = Field(default_factory=StreamInput)
    ppe_classes: PpeClassList = Field(
        default_factory=lambda: [PpeClass.HELMET, PpeClass.VEST]
    )

    _dedupe = field_validator("ppe_classes")(_unique)


class CameraUpdate(PatchModel):
    code: CameraCode | None = None
    name: CameraName | None = None
    zone_id: ZoneId | None = None
    location: Location | None = None
    status: CameraStatus | None = None
    stream: StreamInput | None = None
    ppe_classes: PpeClassList | None = None

    _nullable_fields: ClassVar[frozenset[str]] = frozenset()
    _dedupe = field_validator("ppe_classes")(lambda v: _unique(v) if v else v)
