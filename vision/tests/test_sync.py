from datetime import timedelta
from pathlib import Path

import pytest

from fcs_vision.simulator.__main__ import run_tick
from fcs_vision.simulator.scenario import Scenario
from fcs_vision.sync.client import AuthError, CentralClient, CentralError, TransientError
from fcs_vision.sync.outbox import Outbox
from tests.conftest import CAMERAS, NOW, FakeCentral


def events(n: int = 3):  # type: ignore[no-untyped-def]
    return Scenario(seed=11, event_probability=1.0).tick(CAMERAS * n, NOW)[:n]


# --- İstemci -------------------------------------------------------------------


def test_client_sends_auth_and_contract_headers(make_client, central: FakeCentral) -> None:  # type: ignore[no-untyped-def]
    with make_client() as client:
        config, etag = client.get_config()
    assert config is not None and config.node.id == "edge-test"
    assert etag == '"v1"'
    req = central.requests[0]
    assert req.headers["authorization"].startswith("Bearer fcs_edge_")
    assert req.headers["x-fcs-contract-version"] == "1"


def test_client_handles_not_modified(make_client) -> None:  # type: ignore[no-untyped-def]
    with make_client() as client:
        config, etag = client.get_config('"v1"')
    assert config is None and etag == '"v1"'


@pytest.mark.parametrize(
    ("status", "error"),
    [(401, AuthError), (403, AuthError), (422, CentralError), (503, TransientError), (-1, TransientError)],
)
def test_client_error_mapping(make_client, central: FakeCentral, status: int, error: type) -> None:  # type: ignore[no-untyped-def]
    central.fail_with = status
    with make_client() as client, pytest.raises(error):
        client.get_config()


def test_client_requires_key() -> None:
    with pytest.raises(ValueError):
        CentralClient("http://x", "")


# --- Outbox --------------------------------------------------------------------


def test_outbox_survives_restart_and_flushes(tmp_path: Path, make_client, central: FakeCentral) -> None:  # type: ignore[no-untyped-def]
    db = tmp_path / "outbox.db"
    batch = events(3)
    with Outbox(db) as outbox:
        for e in batch:
            outbox.enqueue(e)

    # "Edge yeniden başladı"
    with Outbox(db) as outbox, make_client() as client:
        assert len(outbox.pending()) == 3
        assert outbox.flush(client) == (3, 0)
        assert outbox.pending() == []
        assert outbox.counts() == {"sent": 3}
    assert set(central.received) == {str(e.event_id) for e in batch}


def test_outbox_keeps_events_on_network_error(tmp_path: Path, make_client, central: FakeCentral) -> None:  # type: ignore[no-untyped-def]
    with Outbox(tmp_path / "o.db") as outbox, make_client() as client:
        for e in events(2):
            outbox.enqueue(e)
        central.fail_with = -1
        with pytest.raises(TransientError):
            outbox.flush(client)
        assert len(outbox.pending()) == 2  # kaybolmadı

        central.fail_with = None
        assert outbox.flush(client) == (2, 0)


def test_outbox_does_not_retry_rejected(tmp_path: Path, make_client, central: FakeCentral) -> None:  # type: ignore[no-untyped-def]
    central.reject_cameras = {"cam-02"}
    with Outbox(tmp_path / "o.db") as outbox, make_client() as client:
        for e in events(4):
            outbox.enqueue(e)
        sent, rejected = outbox.flush(client)
        assert rejected > 0 and sent + rejected == 4
        assert outbox.pending() == []
        assert outbox.counts()["rejected"] == rejected


def test_outbox_requeues_event_when_it_ends(tmp_path: Path, make_client, central: FakeCentral) -> None:  # type: ignore[no-untyped-def]
    [event] = events(1)
    with Outbox(tmp_path / "o.db") as outbox, make_client() as client:
        outbox.enqueue(event)
        outbox.flush(client)
        outbox.enqueue(event.model_copy(update={"ended_at": NOW + timedelta(seconds=30)}))
        assert len(outbox.pending()) == 1
        outbox.flush(client)
    assert central.received[str(event.event_id)]["endedAt"] is not None


# --- Simülatör turu --------------------------------------------------------------


def test_simulator_tick_end_to_end(tmp_path: Path, make_client, central: FakeCentral) -> None:  # type: ignore[no-untyped-def]
    scenario = Scenario(seed=5, event_probability=1.0, offline_cameras=frozenset({"cam-02"}))
    with Outbox(tmp_path / "o.db") as outbox, make_client() as client:
        config, etag = run_tick(client, outbox, scenario, None, None)
        assert config is not None and etag == '"v1"'
        # İkinci tur: yapılandırma değişmedi (304), mevcut yapılandırma korunur
        config2, _ = run_tick(client, outbox, scenario, config, etag)
        assert config2 is config

    hb = central.heartbeats[0]
    assert hb["simulated"] is True
    assert {c["cameraId"]: c["status"] for c in hb["cameras"]} == {
        "cam-01": "online",
        "cam-02": "offline",
    }
    assert central.received  # olaylar merkeze ulaştı
    assert all(e["cameraId"] == "cam-01" for e in central.received.values())
