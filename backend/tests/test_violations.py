from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from tests.conftest import API
from tests.test_cameras import assert_error


def test_list_violations_newest_first(client: TestClient) -> None:
    body = client.get(f"{API}/violations", params={"page_size": 100}).json()
    assert body["total"] == 24
    items = body["items"]
    assert items[0]["id"] == "vio-0022"
    times = [v["detectedAt"] for v in items]
    assert times == sorted(times, reverse=True)

    v = items[0]
    assert set(v) >= {
        "id", "cameraId", "zoneId", "violationType", "missing", "detectedAt", "confidence",
        "severity", "status", "source", "description", "reviewedAt",
        "factoryId", "endedAt", "eventId", "edgeNodeId", "ruleId", "trackId", "modelRef",
    }  # fmt: skip
    assert v["factoryId"] == "fac-default"
    assert v["eventId"] is None and v["edgeNodeId"] is None
    assert v["violationType"] == "missing_ppe"
    assert v["source"] == "simulation"


def test_list_violations_filters(client: TestClient) -> None:
    def ids(**params) -> set[str]:  # type: ignore[no-untyped-def]
        return {v["id"] for v in client.get(f"{API}/violations", params=params).json()["items"]}

    open_items = client.get(f"{API}/violations", params={"status": "open"}).json()
    assert open_items["total"] == 3
    assert all(v["status"] == "open" for v in open_items["items"])

    pending = client.get(
        f"{API}/violations", params=[("status", "open"), ("status", "acknowledged")]
    ).json()
    assert pending["total"] == 5

    assert all(
        v["cameraId"] == "cam-02"
        for v in client.get(f"{API}/violations", params={"camera_id": "cam-02"}).json()["items"]
    )

    helmet = client.get(f"{API}/violations", params={"ppe": "helmet", "page_size": 100}).json()
    assert helmet["total"] > 0
    assert all("helmet" in v["missing"] for v in helmet["items"])

    high = client.get(f"{API}/violations", params={"severity": "high", "page_size": 100}).json()
    assert all(v["severity"] == "high" for v in high["items"])

    assert ids(zone_id="zone-hazmat") == {"vio-0013", "vio-0006"}
    assert ids(factory_id="fac-gebze") == {"vio-0023", "vio-0024"}
    assert len(ids(factory_id="fac-default", page_size=100)) == 22
    assert len(ids(type="missing_ppe", page_size=100)) == 24
    assert ids(type="restricted_area") == set()


def test_list_violations_date_range_and_order(client: TestClient) -> None:
    since = (datetime.now(UTC) - timedelta(minutes=30)).isoformat()
    recent = client.get(f"{API}/violations", params={"from": since}).json()
    assert recent["total"] == 4  # 3, 6, 11 ve 27 dakika önce

    asc = client.get(f"{API}/violations", params={"order": "asc", "page_size": 1}).json()
    assert asc["items"][0]["id"] == "vio-0001"

    naive = client.get(f"{API}/violations", params={"from": "2026-01-01T00:00:00"})
    assert_error(naive, 422, "validation_error")
    assert_error(client.get(f"{API}/violations", params={"order": "random"}), 422, "validation_error")
    assert_error(client.get(f"{API}/violations", params={"ppe": "cape"}), 422, "validation_error")


def test_list_violations_pagination(client: TestClient) -> None:
    page1 = client.get(f"{API}/violations", params={"page_size": 10}).json()
    page3 = client.get(f"{API}/violations", params={"page": 3, "page_size": 10}).json()
    assert len(page1["items"]) == 10
    assert len(page3["items"]) == 4
    assert page1["items"][0]["id"] != page3["items"][0]["id"]


def test_get_violation(client: TestClient) -> None:
    r = client.get(f"{API}/violations/vio-0020")
    assert r.status_code == 200
    assert r.json()["missing"] == ["helmet", "vest"]
    assert_error(client.get(f"{API}/violations/vio-9999"), 404, "not_found")


def test_acknowledge_violation(client: TestClient) -> None:
    before = client.get(f"{API}/violations/vio-0022").json()
    assert before["status"] == "open"
    assert before["reviewedAt"] is None

    r = client.patch(f"{API}/violations/vio-0022", json={"status": "acknowledged"})
    assert r.status_code == 200, r.text
    after = r.json()
    assert after["status"] == "acknowledged"
    assert after["reviewedAt"] is not None

    # Liste ve özet de güncel durumu yansıtır
    open_ids = {
        v["id"]
        for v in client.get(f"{API}/violations", params={"status": "open"}).json()["items"]
    }
    assert "vio-0022" not in open_ids
    assert client.get(f"{API}/dashboard/summary").json()["violations"]["open"] == 2


def test_resolve_then_reopen_violation(client: TestClient) -> None:
    resolved = client.patch(
        f"{API}/violations/vio-0021",
        json={"status": "resolved", "description": "Personel uyarıldı, baret temin edildi."},
    ).json()
    assert resolved["status"] == "resolved"
    assert resolved["description"] == "Personel uyarıldı, baret temin edildi."
    assert resolved["reviewedAt"] is not None

    reopened = client.patch(f"{API}/violations/vio-0021", json={"status": "open"}).json()
    assert reopened["status"] == "open"
    assert reopened["reviewedAt"] is None
    # Açıklama durumdan bağımsızdır
    assert reopened["description"] == "Personel uyarıldı, baret temin edildi."

    cleared = client.patch(f"{API}/violations/vio-0021", json={"description": None}).json()
    assert cleared["description"] is None


def test_update_violation_errors(client: TestClient) -> None:
    url = f"{API}/violations/vio-0022"
    assert_error(client.patch(url, json={"status": "closed"}), 422, "validation_error")
    assert_error(client.patch(url, json={}), 422, "validation_error")
    assert_error(client.patch(url, json={"status": None}), 422, "validation_error")
    assert_error(client.patch(url, json={"cameraId": "cam-02"}), 422, "validation_error")
    assert_error(client.patch(url, json={"description": "x" * 2001}), 422, "validation_error")
    assert_error(
        client.patch(f"{API}/violations/vio-9999", json={"status": "acknowledged"}),
        404,
        "not_found",
    )
    # Hatalı istekler kaydı değiştirmez
    assert client.get(url).json()["status"] == "open"
