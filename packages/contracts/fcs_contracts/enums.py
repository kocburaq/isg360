"""Edge ve merkezin ortak kullandığı değer kümeleri.

Frontend TypeScript tipleri (src/features/cameras/types.ts) bu değerlerle birebir aynıdır.
"""

from enum import StrEnum


class PpeClass(StrEnum):
    HELMET = "helmet"
    VEST = "vest"
    GLOVES = "gloves"
    GOGGLES = "goggles"
    SAFETY_BOOTS = "safety-boots"


class ViolationType(StrEnum):
    # Kişide gerekli KKD eksik (baret, yelek…)
    MISSING_PPE = "missing_ppe"
    # Yasaklı / izinsiz bölgeye giriş
    RESTRICTED_AREA = "restricted_area"
    # Yüksekte çalışırken emniyet kemeri yok
    MISSING_HARNESS = "missing_harness"


class ViolationSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DetectionSource(StrEnum):
    # Örnek/simülasyon verisi — gerçek kamera veya model çıktısı değildir
    SIMULATION = "simulation"
    # Gerçek model çıktısı
    MODEL = "model"


class EdgeCameraStatus(StrEnum):
    """Edge'in bir kamera için bildirdiği bağlantı durumu."""

    ONLINE = "online"
    OFFLINE = "offline"
