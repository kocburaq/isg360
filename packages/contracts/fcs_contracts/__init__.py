"""Factory Control System — edge ↔ merkez sözleşmeleri.

Backend (backend/) ve saha görüntü işleme servisi (vision/) bu paketi birlikte kullanır;
böylece iki taraf aynı şemayı paylaşır ve uyumsuzluk testlerde yakalanır.

Sürümleme: Uyumsuz (geriye dönük bozan) değişikliklerde CONTRACT_VERSION artırılır.
"""

from fcs_contracts.config import EdgeCameraConfig, EdgeConfig, EdgeNodeInfo
from fcs_contracts.enums import (
    DetectionSource,
    EdgeCameraStatus,
    PpeClass,
    ViolationSeverity,
    ViolationType,
)
from fcs_contracts.events import (
    EventBatch,
    EventBatchResult,
    EventResult,
    EventResultStatus,
    ModelRef,
    ViolationEvent,
)
from fcs_contracts.heartbeat import CameraHeartbeat, Heartbeat, HeartbeatResult

CONTRACT_VERSION = "1"
# İstemcinin hangi sözleşme sürümünü kullandığını bildirdiği HTTP başlığı
CONTRACT_VERSION_HEADER = "X-FCS-Contract-Version"

__all__ = [
    "CONTRACT_VERSION",
    "CONTRACT_VERSION_HEADER",
    "CameraHeartbeat",
    "DetectionSource",
    "EdgeCameraConfig",
    "EdgeCameraStatus",
    "EdgeConfig",
    "EdgeNodeInfo",
    "EventBatch",
    "EventBatchResult",
    "EventResult",
    "EventResultStatus",
    "Heartbeat",
    "HeartbeatResult",
    "ModelRef",
    "PpeClass",
    "ViolationEvent",
    "ViolationSeverity",
    "ViolationType",
]
