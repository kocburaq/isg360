"""Alan değer kümeleri. Frontend'deki TypeScript birleşim tipleriyle birebir aynıdır.

Edge ile paylaşılan değerler (KKD sınıfı, ihlal türü, önem, kaynak) ortak sözleşme
paketinden (packages/contracts) gelir; böylece iki taraf asla ayrışmaz.
"""

from enum import StrEnum

from fcs_contracts.enums import (
    DetectionSource,
    PpeClass,
    ViolationSeverity,
    ViolationType,
)

__all__ = [
    "CameraStatus",
    "DetectionSource",
    "PpeClass",
    "ViolationSeverity",
    "ViolationStatus",
    "ViolationType",
]


class CameraStatus(StrEnum):
    ONLINE = "online"
    OFFLINE = "offline"
    # Gerçek telemetri olmadan durumu bilinmeyen kameralar (ör. yeni eklenenler)
    UNKNOWN = "unknown"


class ViolationStatus(StrEnum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
