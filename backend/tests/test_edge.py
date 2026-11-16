"""Edge (saha sunucusu) ↔ merkez API testleri."""

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.cli.edge_nodes import CliError, assign_cameras, create_node, rotate_key
from app.core.security import hash_api_key
from app.models import Camera, EdgeNode, PpeViolation
from app.models.enums import CameraStatus
from app.repositories.edge import mark_stale_cameras_offline
from tests.conftest import API
from tests.test_cameras import assert_error

EDGE = "/edge/v1"


@pytest.fixture
def node_key(session_factory: sessionmaker[Session]) -> tuple[str, str]:
    """fac-default fabrikasında cam-01 ve cam-02'yi okuyan bir edge node."""
    with session_factory() as session:
        node, key = create_node(
            session, factory_id="fac-default", name="Test Edge", camera_ids=["cam-01", "cam-02"]
        )
        return node.id, key


@pytest.fixture
def edge(client: TestClient, node_key: tuple[str, str]) -> Iterator[TestClient]:
    client.headers["Authorization"] = f"Bearer {node_key[1]}"
    yield client
    client.headers.pop("Authorization", None)


def now_iso(delta_s: float = 0) -> str:
    return (datetime.now(UTC) + timedelta(seconds=delta_s)).isoformat()


def heartbeat(**overrides):  # type: ignore[no-untyped-def]
    body = {
        "sentAt": now_iso(),
        "softwareVersion": "0.1.0-test",
        "simulated": True,
        "cameras": [
            {"cameraId": "cam-01", "status": "online", "fps": 5},
            {"cameraId": "cam-02", "status": "offline", "error": "RTSP zaman aşımı"},
        ],
    }
    body.update(overrides)
    return body


def event(**overrides):  # type: ignore[no-untyped-def]
    body = {
        "eventId": str(uuid4()),
        "cameraId": "cam-01",
        "violationType": "missing_ppe",
        "missingPpe": ["helmet"],
        "startedAt": now_iso(-5),
        "confidence": 0.87,
        "severity": "high",
        "source": "simulation",
        "ruleId": "rule-ppe-1",
        "trackId": "trk-42",
    }
    body.update(overrides)
    return body


# --- Kimlik doğrulama ------------------------------------------------------


def test_edge_api_requires_valid_key(client: TestClient, node_key: tuple[str, str]) -> None:
    r = client.get(f"{EDGE}/config")
    err = assert_error(r, 401, "unauthorized")
    assert r.headers["www-authenticate"] == "Bearer"
    assert "anahtar" in err["message"]

    for header in ["Bearer fcs_edge_wrongwrongwrongwrongwrong", "Bearer x", "Basic abc"]:
        assert_error(client.get(f"{EDGE}/config", headers={"Authorization": header}), 401, "unauthorized")

    ok = client.get(f"{EDGE}/config", headers={"Authorization": f"Bearer {node_key[1]}"})
    assert ok.status_code == 200


def test_deactivated_node_is_forbidden(
    edge: TestClient, node_key: tuple[str, str], session_factory: sessionmaker[Session]
) -> None:
    with session_factory() as session:
        session.get(EdgeNode, node_key[0]).is_active = False  # type: ignore[union-attr]
        session.commit()
    assert_error(edge.get(f"{EDGE}/config"), 403, "forbidden")


def test_unsupported_contract_version(edge: TestClient) -> None:
    r = edge.get(f"{EDGE}/config", headers={"X-FCS-Contract-Version": "99"})
    assert_error(r, 400, "unsupported_contract")
    assert edge.get(f"{EDGE}/config", headers={"X-FCS-Contract-Version": "1"}).status_code == 200


def test_api_key_is_stored_only_as_hash(
    node_key: tuple[str, str], session_factory: sessionmaker[Session]
) -> None:
    node_id, key = node_key
    with session_factory() as session:
        node = session.get(EdgeNode, node_id)
        assert node is not None
        assert node.api_key_hash == hash_api_key(key)
        assert key not in (node.api_key_hash, node.api_key_prefix)
        assert key.startswith(node.api_key_prefix)


# --- Yapılandırma ----------------------------------------------------------


def test_config_lists_only_assigned_cameras_with_etag(
    edge: TestClient, node_key: tuple[str, str], session_factory: sessionmaker[Session]
) -> None:
    r = edge.get(f"{EDGE}/config")
    assert r.status_code == 200
    body = r.json()
    assert body["node"] == {
        "id": node_key[0],
        "name": "Test Edge",
        "factoryId": "fac-default",
        "factoryName": "Merkez Fabrika",
        "timezone": "Europe/Istanbul",
    }
    assert [c["id"] for c in body["cameras"]] == ["cam-01", "cam-02"]
    assert body["cameras"][0]["ppeClasses"] == ["helmet", "vest"]
    etag = r.headers["etag"]
    assert etag == f'"{body["configVersion"]}"'

    not_modified = edge.get(f"{EDGE}/config", headers={"If-None-Match": etag})
    assert not_modified.status_code == 304
    assert not_modified.content == b""

    # Atama değişince sürüm de değişir
    with session_factory() as session:
        node = session.get(EdgeNode, node_key[0])
        assign_cameras(session, node, ["cam-03"])  # type: ignore[arg-type]
        session.commit()
    changed = edge.get(f"{EDGE}/config", headers={"If-None-Match": etag})
    assert changed.status_code == 200
    assert len(changed.json()["cameras"]) == 3


# --- Heartbeat --------------------------------------------------------------


def test_heartbeat_updates_camera_status(
    edge: TestClient, node_key: tuple[str, str], session_factory: sessionmaker[Session]
) -> None:
    before = edge.get(f"{API}/cameras/cam-01").json()
    assert before["edgeNodeId"] == node_key[0]
    assert before["status"] == "unknown"  # atandıktan sonra telemetri gelene kadar

    body = heartbeat(
        cameras=[
            {"cameraId": "cam-01", "status": "online", "fps": 5},
            {"cameraId": "cam-02", "status": "offline", "error": "RTSP zaman aşımı"},
            {"cameraId": "cam-03", "status": "online"},  # bu node'a ait değil
            {"cameraId": "cam-99", "status": "online"},  # yok
        ]
    )
    r = edge.post(f"{EDGE}/heartbeat", json=body)
    assert r.status_code == 200, r.text
    result = r.json()
    assert result["acceptedCameras"] == 2
    assert result["unknownCameras"] == ["cam-03", "cam-99"]
    assert result["configVersion"] == edge.get(f"{EDGE}/config").json()["configVersion"]

    cam1 = edge.get(f"{API}/cameras/cam-01").json()
    cam2 = edge.get(f"{API}/cameras/cam-02").json()
    assert cam1["status"] == "online"
    assert cam1["isSimulated"] is True  # simülatör heartbeat'i
    assert cam2["status"] == "offline"
    # Atanmamış kamera değişmez
    assert edge.get(f"{API}/cameras/cam-03").json()["edgeNodeId"] is None

    with session_factory() as session:
        node = session.get(EdgeNode, node_key[0])
        assert node is not None and node.last_seen_at is not None
        assert node.software_version == "0.1.0-test"
        assert node.reports_simulated is True


def test_real_heartbeat_clears_simulated_flag(edge: TestClient) -> None:
    edge.post(f"{EDGE}/heartbeat", json=heartbeat(simulated=False))
    assert edge.get(f"{API}/cameras/cam-01").json()["isSimulated"] is False


def test_heartbeat_validation(edge: TestClient) -> None:
    assert_error(
        edge.post(f"{EDGE}/heartbeat", json=heartbeat(sentAt="2026-11-15T10:00:00")),
        422,
        "validation_error",
    )
    assert_error(
        edge.post(f"{EDGE}/heartbeat", json=heartbeat(cameras=[{"cameraId": "cam-01", "status": "sleeping"}])),
        422,
        "validation_error",
    )


def test_cameras_go_offline_when_heartbeat_stops(
    edge: TestClient, session_factory: sessionmaker[Session]
) -> None:
    edge.post(f"{EDGE}/heartbeat", json=heartbeat())
    assert edge.get(f"{API}/cameras/cam-01").json()["status"] == "online"

    with session_factory() as session:
        # Heartbeat yeni geldi: 60 sn zaman aşımı içinde değişiklik yok
        assert mark_stale_cameras_offline(session, datetime.now(UTC) - timedelta(seconds=60)) == 0
        # "Edge durdu": zaman aşımı geçmiş gibi kontrol et
        changed = mark_stale_cameras_offline(session, datetime.now(UTC) + timedelta(seconds=1))
        assert changed == 1  # yalnızca edge'e atanmış ve çevrimiçi olan cam-01

    assert edge.get(f"{API}/cameras/cam-01").json()["status"] == "offline"
    # Edge'e atanmamış seed kameralarına dokunulmaz
    assert edge.get(f"{API}/cameras/cam-03").json()["status"] == "online"

    # Heartbeat tekrar gelince kamera geri döner
    edge.post(f"{EDGE}/heartbeat", json=heartbeat())
    assert edge.get(f"{API}/cameras/cam-01").json()["status"] == "online"


def test_health_reports_edge_nodes(edge: TestClient) -> None:
    def edge_state() -> str:
        services = edge.get(f"{API}/health").json()["services"]
        return next(s for s in services if s["id"] == "edge")["state"]

    assert edge_state() == "down"  # node kayıtlı ama hiç görülmedi
    edge.post(f"{EDGE}/heartbeat", json=heartbeat())
    assert edge_state() == "operational"


# --- Olaylar ----------------------------------------------------------------


def test_event_creates_violation_visible_in_panel(edge: TestClient, node_key: tuple[str, str]) -> None:
    open_before = edge.get(f"{API}/dashboard/summary").json()["violations"]["open"]
    ev = event()
    r = edge.post(f"{EDGE}/events", json={"events": [ev]})
    assert r.status_code == 200, r.text
    [res] = r.json()["results"]
    assert res["status"] == "created"
    assert res["eventId"] == ev["eventId"]

    v = edge.get(f"{API}/violations/{res['violationId']}").json()
    assert v["eventId"] == ev["eventId"]
    assert v["edgeNodeId"] == node_key[0]
    assert v["cameraId"] == "cam-01"
    assert v["zoneId"] == "zone-entrance"
    assert v["factoryId"] == "fac-default"
    assert v["missing"] == ["helmet"]
    assert v["status"] == "open"
    assert v["source"] == "simulation"
    assert (v["ruleId"], v["trackId"], v["endedAt"]) == ("rule-ppe-1", "trk-42", None)

    assert edge.get(f"{API}/dashboard/summary").json()["violations"]["open"] == open_before + 1


def test_events_are_idempotent(edge: TestClient, session_factory: sessionmaker[Session]) -> None:
    ev = event()
    first = edge.post(f"{EDGE}/events", json={"events": [ev]}).json()["results"][0]

    # Ağ kopması sonrası aynı olay tekrar gönderildi
    again = edge.post(f"{EDGE}/events", json={"events": [ev]}).json()["results"][0]
    assert again["status"] == "duplicate"
    assert again["violationId"] == first["violationId"]

    # İhlal bitti: aynı olay endedAt ile gönderilir → güncellenir
    ended = edge.post(f"{EDGE}/events", json={"events": [{**ev, "endedAt": now_iso()}]}).json()
    assert ended["results"][0]["status"] == "updated"
    assert edge.get(f"{API}/violations/{first['violationId']}").json()["endedAt"] is not None

    # Bitişten sonra tekrar gönderim yine çift kayıt oluşturmaz
    final = edge.post(f"{EDGE}/events", json={"events": [{**ev, "endedAt": now_iso()}]}).json()
    assert final["results"][0]["status"] == "duplicate"

    with session_factory() as session:
        rows = session.query(PpeViolation).filter_by(event_id=ev["eventId"]).all()
        assert len(rows) == 1


def test_mixed_batch_reports_per_event_results(edge: TestClient) -> None:
    batch = [
        event(),
        event(cameraId="cam-03"),  # bu node'a atanmamış
        event(cameraId="cam-99"),  # yok
        event(startedAt=now_iso(3600)),  # 1 saat ileride
        event(violationType="restricted_area", missingPpe=[], severity="medium"),
        event(violationType="missing_harness", missingPpe=[], cameraId="cam-02"),
    ]
    r = edge.post(f"{EDGE}/events", json={"events": batch})
    assert r.status_code == 200
    results = r.json()["results"]
    assert [x["status"] for x in results] == [
        "created", "rejected", "rejected", "rejected", "created", "created",
    ]  # fmt: skip
    assert [x["reason"] for x in results[1:4]] == [
        "camera_not_assigned", "camera_not_assigned", "future_timestamp",
    ]  # fmt: skip

    restricted = edge.get(f"{API}/violations", params={"type": "restricted_area"}).json()
    assert restricted["total"] == 1
    assert restricted["items"][0]["missing"] == []
    harness = edge.get(f"{API}/violations", params={"type": "missing_harness"}).json()
    assert harness["items"][0]["cameraId"] == "cam-02"


def test_event_id_cannot_be_reused_by_another_node(
    edge: TestClient, session_factory: sessionmaker[Session]
) -> None:
    ev = event()
    edge.post(f"{EDGE}/events", json={"events": [ev]})

    with session_factory() as session:
        _, other_key = create_node(
            session, factory_id="fac-default", name="Diğer Edge", camera_ids=["cam-03"]
        )
    r = edge.post(
        f"{EDGE}/events",
        json={"events": [{**ev, "cameraId": "cam-03"}]},
        headers={"Authorization": f"Bearer {other_key}"},
    )
    res = r.json()["results"][0]
    assert (res["status"], res["reason"]) == ("rejected", "event_id_conflict")


def test_event_batch_validation(edge: TestClient) -> None:
    cases = [
        {"events": []},
        {"events": [event(missingPpe=[])]},  # missing_ppe türü KKD listesi ister
        {"events": [event(violationType="restricted_area")]},  # KKD listesi almaz
        {"events": [event(confidence=2)]},
        {"events": [event(source="model")]},  # model bilgisi gerekli
        {"events": [event(startedAt="2026-11-15T10:00:00")]},  # zaman dilimi yok
    ]
    for body in cases:
        assert_error(edge.post(f"{EDGE}/events", json=body), 422, "validation_error")


# --- CLI ---------------------------------------------------------------------


def test_cli_rejects_cross_factory_assignment_and_rotates_keys(
    client: TestClient, session_factory: sessionmaker[Session]
) -> None:
    with session_factory() as session:
        with pytest.raises(CliError):
            create_node(session, factory_id="fac-mars", name="X")
        session.rollback()
        with pytest.raises(CliError, match="fabrikasında"):
            create_node(session, factory_id="fac-default", name="X", camera_ids=["cam-07"])
        session.rollback()

        node, old_key = create_node(session, factory_id="fac-gebze", name="Gebze Edge",
                                    camera_ids=["cam-07"])  # fmt: skip
        assert session.get(Camera, "cam-07").status == CameraStatus.UNKNOWN  # type: ignore[union-attr]
        new_key = rotate_key(session, node)

    auth = lambda k: {"Authorization": f"Bearer {k}"}  # noqa: E731
    assert_error(client.get(f"{EDGE}/config", headers=auth(old_key)), 401, "unauthorized")
    cfg = client.get(f"{EDGE}/config", headers=auth(new_key)).json()
    assert [c["id"] for c in cfg["cameras"]] == ["cam-07"]
    assert cfg["node"]["factoryName"] == "Gebze Fabrikası"
