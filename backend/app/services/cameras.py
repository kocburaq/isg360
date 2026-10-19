"""Kamera iş mantığı. HTTP'den bağımsızdır; hata durumlarında AppError fırlatır."""

from sqlalchemy.orm import Session

from app.core.errors import ConflictError, InvalidReferenceError, NotFoundError
from app.models import Camera
from app.repositories.cameras import CameraFilter, CameraRepository, ZoneRepository
from app.repositories.violations import ViolationRepository
from app.schemas.camera import CameraCreate, CameraUpdate


class CameraService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.cameras = CameraRepository(session)
        self.zones = ZoneRepository(session)
        self.violations = ViolationRepository(session)

    def list(self, f: CameraFilter, *, page: int, page_size: int) -> tuple[list[Camera], int]:
        return self.cameras.list(f, offset=(page - 1) * page_size, limit=page_size)

    def get(self, camera_id: str) -> Camera:
        camera = self.cameras.get(camera_id)
        if camera is None:
            raise NotFoundError(f"Kamera bulunamadı: {camera_id}")
        return camera

    def _ensure_zone(self, zone_id: str) -> None:
        if self.zones.get(zone_id) is None:
            raise InvalidReferenceError(
                f"Bölge bulunamadı: {zone_id}",
                details=[{"loc": ["body", "zoneId"], "message": "Geçersiz bölge"}],
            )

    def _ensure_code_free(self, code: str, *, exclude_id: str | None = None) -> None:
        existing = self.cameras.get_by_code(code)
        if existing is not None and existing.id != exclude_id:
            raise ConflictError(f"Bu kamera kodu zaten kullanılıyor: {code}")

    def create(self, data: CameraCreate) -> Camera:
        self._ensure_zone(data.zone_id)
        self._ensure_code_free(data.code)
        camera = Camera(
            code=data.code,
            name=data.name,
            zone_id=data.zone_id,
            location=data.location,
            status=data.status,
            stream_protocol="rtsp",
            stream_configured=False,
            resolution=data.stream.resolution,
            fps=data.stream.fps,
            ppe_classes=[p.value for p in data.ppe_classes],
            # API ile eklenen kayıt elle girilmiş envanterdir; telemetri yoktur.
            is_simulated=False,
        )
        self.cameras.add(camera)
        self.session.commit()
        self.session.refresh(camera)
        return camera

    def update(self, camera_id: str, data: CameraUpdate) -> Camera:
        camera = self.get(camera_id)
        changes = data.changes()

        if "zone_id" in changes:
            self._ensure_zone(changes["zone_id"])
        if "code" in changes:
            self._ensure_code_free(changes["code"], exclude_id=camera.id)
        if "stream" in changes:
            stream = changes.pop("stream")
            camera.resolution = stream.get("resolution", camera.resolution)
            camera.fps = stream.get("fps", camera.fps)
        if "ppe_classes" in changes:
            changes["ppe_classes"] = [p.value for p in changes["ppe_classes"]]

        for field, value in changes.items():
            setattr(camera, field, value)

        self.session.commit()
        self.session.refresh(camera)
        return camera

    def delete(self, camera_id: str) -> None:
        camera = self.get(camera_id)
        if self.violations.exists_for_camera(camera.id):
            raise ConflictError(
                "Bu kameraya ait ihlal kayıtları var; İSG geçmişini korumak için kamera silinemez."
            )
        self.cameras.delete(camera)
        self.session.commit()
