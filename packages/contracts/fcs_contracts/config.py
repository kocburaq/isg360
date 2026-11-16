"""Edge yapılandırması (merkez → edge).

Edge, kendisine atanmış kameraları ve (3.2 aşamasından itibaren) kuralları buradan çeker.
Kamera akış adresleri ve kimlik bilgileri bu aşamada taşınmaz.
"""

from typing import Annotated, Any

from pydantic import Field

from fcs_contracts.base import AwareDatetime, ContractModel
from fcs_contracts.enums import PpeClass
from fcs_contracts.events import Identifier


class EdgeNodeInfo(ContractModel):
    id: Identifier
    name: str
    factory_id: Identifier
    factory_name: str
    timezone: str


class EdgeCameraConfig(ContractModel):
    id: Identifier
    code: str
    name: str
    zone_id: Identifier
    ppe_classes: list[PpeClass]
    stream_configured: bool
    # Kural tanımları 3.2 aşamasında eklenecek; şimdilik boş liste
    rules: list[dict[str, Any]] = Field(default_factory=list)


class EdgeConfig(ContractModel):
    node: EdgeNodeInfo
    cameras: Annotated[list[EdgeCameraConfig], Field(max_length=500)]
    # İçerik özeti (hash): değişmediyse edge yeniden işlem yapmaz
    config_version: str
    generated_at: AwareDatetime
