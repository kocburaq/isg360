import json
from collections.abc import Callable
from datetime import UTC, datetime

import httpx
import pytest
from fcs_contracts import EdgeCameraConfig, PpeClass

NOW = datetime(2026, 11, 15, 10, 0, tzinfo=UTC)

CAMERAS = [
    EdgeCameraConfig(
        id="cam-01", code="CAM-01", name="Giriş", zone_id="z1",
        ppe_classes=[PpeClass.HELMET, PpeClass.VEST], stream_configured=False,
    ),
    EdgeCameraConfig(
        id="cam-02", code="CAM-02", name="Montaj", zone_id="z2",
        ppe_classes=[PpeClass.HELMET], stream_configured=False,
    ),
]  # fmt: skip

CONFIG = {
    "node": {
        "id": "edge-test",
        "name": "Test Edge",
        "factoryId": "fac-default",
        "factoryName": "Merkez Fabrika",
        "timezone": "Europe/Istanbul",
    },
    "cameras": [c.model_dump(mode="json") for c in CAMERAS],
    "configVersion": "v1",
    "generatedAt": NOW.isoformat(),
}


class FakeCentral:
    """Merkez edge API'sinin bellek içi taklidi (httpx.MockTransport ile)."""

    def __init__(self) -> None:
        self.requests: list[httpx.Request] = []
        self.received: dict[str, dict] = {}
        self.heartbeats: list[dict] = []
        self.fail_with: int | None = None
        self.reject_cameras: set[str] = set()

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if self.fail_with == -1:
            raise httpx.ConnectError("bağlantı reddedildi", request=request)
        if self.fail_with:
            body = {"error": {"code": "x", "message": "hata"}}
            return httpx.Response(self.fail_with, json=body)
        path = request.url.path
        if path.endswith("/config"):
            if request.headers.get("if-none-match") == '"v1"':
                return httpx.Response(304, headers={"ETag": '"v1"'})
            return httpx.Response(200, json=CONFIG, headers={"ETag": '"v1"'})
        if path.endswith("/heartbeat"):
            self.heartbeats.append(json.loads(request.content))
            return httpx.Response(
                200, json={"acceptedCameras": 2, "unknownCameras": [], "configVersion": "v1"}
            )
        if path.endswith("/events"):
            results = []
            for ev in json.loads(request.content)["events"]:
                eid = ev["eventId"]
                if ev["cameraId"] in self.reject_cameras:
                    results.append({"eventId": eid, "status": "rejected", "reason": "camera_not_assigned"})
                    continue
                status = "duplicate" if eid in self.received else "created"
                if eid in self.received and ev.get("endedAt") and not self.received[eid].get("endedAt"):
                    status = "updated"
                self.received[eid] = ev
                results.append({"eventId": eid, "status": status, "violationId": f"vio-{eid[:6]}"})
            return httpx.Response(200, json={"results": results})
        return httpx.Response(404)


@pytest.fixture
def central() -> FakeCentral:
    return FakeCentral()


@pytest.fixture
def make_client(central: FakeCentral) -> Callable:
    from fcs_vision.sync.client import CentralClient

    def _make() -> CentralClient:
        return CentralClient(
            "http://central.test/edge/v1",
            "fcs_edge_testkey_testkey_testkey",
            transport=httpx.MockTransport(central.handler),
        )

    return _make
