"""Veritabanı kalıcılığı: değişiklikler yeni bağlantı/uygulama örneğinde de görünür."""

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.db.seed import seed_demo_data
from app.db.session import build_engine, build_session_factory
from app.models import Camera, PpeViolation
from app.models.enums import ViolationStatus
from tests.conftest import API, make_client


def test_acknowledged_violation_survives_restart(
    settings: Settings, session_factory: sessionmaker[Session], db_url: str
) -> None:
    with make_client(settings, session_factory) as client:
        r = client.patch(f"{API}/violations/vio-0020", json={"status": "acknowledged"})
        assert r.status_code == 200

    # "Sunucu yeniden başlatıldı": aynı dosyaya tamamen yeni engine + uygulama
    fresh_engine = build_engine(db_url)
    try:
        fresh_factory = build_session_factory(fresh_engine)
        with fresh_factory() as session:
            stored = session.get(PpeViolation, "vio-0020")
            assert stored is not None
            assert stored.status == ViolationStatus.ACKNOWLEDGED
            assert stored.reviewed_at is not None
            assert stored.reviewed_at.tzinfo is not None  # UTC olarak geri okunur

        with make_client(settings, fresh_factory) as client:
            assert client.get(f"{API}/violations/vio-0020").json()["status"] == "acknowledged"
    finally:
        fresh_engine.dispose()


def test_created_camera_is_persisted(
    settings: Settings, session_factory: sessionmaker[Session], db_url: str
) -> None:
    with make_client(settings, session_factory) as client:
        created = client.post(
            f"{API}/cameras",
            json={"code": "CAM-10", "name": "Kompresör Odası", "zoneId": "zone-production"},
        ).json()

    fresh_engine = build_engine(db_url)
    try:
        with build_session_factory(fresh_engine)() as session:
            camera = session.scalar(select(Camera).where(Camera.code == "CAM-10"))
            assert camera is not None
            assert camera.id == created["id"]
            assert camera.zone.name == "Üretim Atölyesi"
    finally:
        fresh_engine.dispose()


def test_seed_is_idempotent_and_keeps_user_changes(
    settings: Settings, session_factory: sessionmaker[Session]
) -> None:
    with make_client(settings, session_factory) as client:
        client.patch(f"{API}/violations/vio-0022", json={"status": "resolved"})

    with session_factory() as session:
        result = seed_demo_data(session)
        assert (result.factories, result.zones, result.cameras, result.violations) == (0, 0, 0, 0)
        assert session.get(PpeViolation, "vio-0022").status == ViolationStatus.RESOLVED  # type: ignore[union-attr]
        assert len(session.scalars(select(PpeViolation)).all()) == 24
