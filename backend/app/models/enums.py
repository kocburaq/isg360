"""Alan değer kümeleri. Frontend'deki TypeScript birleşim tipleriyle birebir aynıdır."""

from enum import StrEnum


class CameraStatus(StrEnum):
    ONLINE = "online"
    OFFLINE = "offline"
    # Gerçek telemetri olmadan durumu bilinmeyen kameralar (ör. yeni eklenenler)
    UNKNOWN = "unknown"


class PpeClass(StrEnum):
    HELMET = "helmet"
    VEST = "vest"
    GLOVES = "gloves"
    GOGGLES = "goggles"
    SAFETY_BOOTS = "safety-boots"


class ViolationType(StrEnum):
    # İleride: restricted_area, unsafe_behavior vb.
    MISSING_PPE = "missing_ppe"


class ViolationStatus(StrEnum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class ViolationSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DetectionSource(StrEnum):
    # "simulation": örnek/seed veri — gerçek kamera veya model çıktısı değildir.
    SIMULATION = "simulation"
    MODEL = "model"
