"""Sağlık, panel özeti, güvenlik yapılandırması ve migration testleri."""

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR, Settings
from app.db.session import build_engine
from app.models import PpeViolation
from app.services.system import SystemService
from tests.conftest import API, run_migrations


def test_health(client: TestClient) -> None:
    r = client.get(f"{API}/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["authentication"] == "none"
    assert body["environment"] == "test"
    states = {s["id"]: s["state"] for s in body["services"]}
    assert states["database"] == "operational"
    # Gerçek model/kamera yok: simülasyon olarak raporlanmalı
    assert states["inference"] == "simulated"
    assert states["stream-gateway"] == "simulated"
    assert body["state"] == "simulated"


def test_dashboard_summary(client: TestClient, db: Session, settings: Settings) -> None:
    body = client.get(f"{API}/dashboard/summary").json()
    assert body["cameras"] == {"total": 8, "online": 7, "offline": 1, "unknown": 0}
    v = body["violations"]
    assert (v["total"], v["open"], v["acknowledged"], v["resolved"]) == (24, 3, 2, 19)
    assert body["containsSimulatedData"] is True
    assert body["timezone"] == "Europe/Istanbul"

    start = SystemService(db, settings).start_of_today()
    expected_today = sum(
        1 for x in db.query(PpeViolation).all() if x.detected_at >= start
    )
    assert v["today"] == expected_today


def test_openapi_docs_available(client: TestClient) -> None:
    assert client.get("/docs").status_code == 200
    spec = client.get(f"{API}/openapi.json").json()
    for path in ["/cameras", "/cameras/{camera_id}", "/violations", "/violations/{violation_id}",
                 "/dashboard/summary", "/health"]:  # fmt: skip
        assert f"{API}{path}" in spec["paths"]


def test_cors_allows_only_configured_origins(client: TestClient) -> None:
    preflight = {"Access-Control-Request-Method": "PATCH"}
    ok = client.options(
        f"{API}/violations/vio-0001", headers={**preflight, "Origin": "http://localhost:5173"}
    )
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:5173"

    bad = client.options(
        f"{API}/violations/vio-0001", headers={**preflight, "Origin": "https://evil.example"}
    )
    assert "access-control-allow-origin" not in bad.headers


def test_untrusted_host_is_rejected(client: TestClient) -> None:
    r = client.get(f"{API}/health", headers={"Host": "192.168.1.50:8000"})
    assert r.status_code == 400


def test_settings_reject_unsafe_configuration() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, app_env="production")  # type: ignore[call-arg,arg-type]
    with pytest.raises(ValidationError):
        Settings(_env_file=None, cors_origins="*")  # type: ignore[call-arg,arg-type]
    s = Settings(_env_file=None, cors_origins="http://a.test, http://b.test")  # type: ignore[call-arg,arg-type]
    assert s.cors_origins == ["http://a.test", "http://b.test"]


def test_migrations_upgrade_and_downgrade(db_url: str) -> None:
    run_migrations(db_url)
    engine = build_engine(db_url)
    try:
        tables = set(inspect(engine).get_table_names())
        assert {"factory_zones", "cameras", "ppe_violations"} <= tables

        cfg = Config(str(BACKEND_DIR / "alembic.ini"))
        cfg.set_main_option("sqlalchemy.url", db_url)
        command.downgrade(cfg, "base")
        assert set(inspect(engine).get_table_names()) <= {"alembic_version"}
    finally:
        engine.dispose()


def test_database_rejects_invalid_enum_values(db: Session) -> None:
    """CHECK kısıtları ORM dışındaki hatalı yazımları da engeller."""
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError):
        db.execute(text("UPDATE ppe_violations SET status = 'deleted' WHERE id = 'vio-0001'"))
    db.rollback()
