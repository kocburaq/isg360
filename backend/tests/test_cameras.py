from fastapi.testclient import TestClient

from tests.conftest import API

NEW_CAMERA = {
    "code": "CAM-07",
    "name": "Boyahane Girişi",
    "zoneId": "zone-production",
    "location": "Boya kabini 1 önü",
}


def assert_error(response, status: int, code: str) -> dict:  # type: ignore[no-untyped-def]
    assert response.status_code == status, response.text
    body = response.json()
    assert set(body) == {"error"}
    assert body["error"]["code"] == code
    assert body["error"]["message"]
    return body["error"]


# --- Listeleme -------------------------------------------------------------


def test_list_cameras_returns_page_with_frontend_shape(client: TestClient) -> None:
    r = client.get(f"{API}/cameras")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 6
    assert body["page"] == 1
    assert [c["code"] for c in body["items"]] == [f"CAM-0{i}" for i in range(1, 7)]

    cam = body["items"][0]
    assert set(cam) >= {
        "id", "code", "name", "zone", "location", "status", "lastSeenAt",
        "stream", "ppeClasses", "isSimulated", "createdAt", "updatedAt",
    }  # fmt: skip
    assert cam["zone"] == {"id": "zone-entrance", "name": "Giriş ve Güvenlik", "area": "A Blok"}
    assert cam["stream"]["protocol"] == "rtsp"
    assert cam["stream"]["configured"] is False
    assert cam["isSimulated"] is True


def test_list_cameras_filters(client: TestClient) -> None:
    offline = client.get(f"{API}/cameras", params={"status": "offline"}).json()
    assert [c["id"] for c in offline["items"]] == ["cam-05"]

    both = client.get(f"{API}/cameras", params=[("status", "offline"), ("status", "online")])
    assert both.json()["total"] == 6

    zone = client.get(f"{API}/cameras", params={"zone_id": "zone-logistics"}).json()
    assert {c["id"] for c in zone["items"]} == {"cam-04", "cam-05"}

    search = client.get(f"{API}/cameras", params={"q": "kaynak"}).json()
    assert [c["id"] for c in search["items"]] == ["cam-03"]


def test_list_cameras_pagination(client: TestClient) -> None:
    body = client.get(f"{API}/cameras", params={"page": 3, "page_size": 2}).json()
    assert body["total"] == 6
    assert body["pageSize"] == 2
    assert [c["code"] for c in body["items"]] == ["CAM-05", "CAM-06"]

    empty = client.get(f"{API}/cameras", params={"page": 10, "page_size": 2}).json()
    assert empty["items"] == []


def test_list_cameras_rejects_invalid_query(client: TestClient) -> None:
    assert_error(client.get(f"{API}/cameras", params={"status": "broken"}), 422, "validation_error")
    assert_error(client.get(f"{API}/cameras", params={"page": 0}), 422, "validation_error")
    assert_error(client.get(f"{API}/cameras", params={"page_size": 10_000}), 422, "validation_error")


def test_get_camera(client: TestClient) -> None:
    r = client.get(f"{API}/cameras/cam-05")
    assert r.status_code == 200
    assert r.json()["status"] == "offline"

    err = assert_error(client.get(f"{API}/cameras/cam-99"), 404, "not_found")
    assert "cam-99" in err["message"]


# --- Ekleme ----------------------------------------------------------------


def test_create_camera(client: TestClient) -> None:
    r = client.post(f"{API}/cameras", json=NEW_CAMERA)
    assert r.status_code == 201, r.text
    cam = r.json()
    assert r.headers["location"] == f"{API}/cameras/{cam['id']}"
    assert cam["code"] == "CAM-07"
    assert cam["zone"]["id"] == "zone-production"
    # Telemetri olmadan durum bilinmez; elle eklenen kayıt simülasyon değildir
    assert cam["status"] == "unknown"
    assert cam["isSimulated"] is False
    assert cam["lastSeenAt"] is None
    assert cam["ppeClasses"] == ["helmet", "vest"]

    assert client.get(f"{API}/cameras/{cam['id']}").status_code == 200
    assert client.get(f"{API}/cameras").json()["total"] == 7


def test_create_camera_rejects_duplicate_code_case_insensitive(client: TestClient) -> None:
    r = client.post(f"{API}/cameras", json={**NEW_CAMERA, "code": "cam-01"})
    assert_error(r, 409, "conflict")


def test_create_camera_rejects_unknown_zone(client: TestClient) -> None:
    r = client.post(f"{API}/cameras", json={**NEW_CAMERA, "zoneId": "zone-mars"})
    err = assert_error(r, 422, "invalid_reference")
    assert err["details"][0]["loc"] == ["body", "zoneId"]


def test_create_camera_validates_body(client: TestClient) -> None:
    cases = [
        {k: v for k, v in NEW_CAMERA.items() if k != "name"},  # zorunlu alan eksik
        {**NEW_CAMERA, "code": "CAM 07; DROP TABLE"},  # geçersiz karakter
        {**NEW_CAMERA, "name": "   "},  # boşluk kırpılınca boş
        {**NEW_CAMERA, "status": "exploded"},  # geçersiz enum
        {**NEW_CAMERA, "ppeClasses": []},  # en az bir KKD sınıfı
        {**NEW_CAMERA, "ppeClasses": ["cape"]},  # bilinmeyen KKD
        {**NEW_CAMERA, "stream": {"fps": 0}},  # aralık dışı
        {**NEW_CAMERA, "rtspUrl": "rtsp://x"},  # bilinmeyen alan
    ]
    for body in cases:
        err = assert_error(client.post(f"{API}/cameras", json=body), 422, "validation_error")
        assert err["details"], body


def test_create_camera_rejects_malformed_json(client: TestClient) -> None:
    r = client.post(
        f"{API}/cameras", content=b"{not json", headers={"Content-Type": "application/json"}
    )
    assert_error(r, 422, "validation_error")


# --- Güncelleme ------------------------------------------------------------


def test_update_camera_partial(client: TestClient) -> None:
    before = client.get(f"{API}/cameras/cam-02").json()
    r = client.patch(
        f"{API}/cameras/cam-02",
        json={"name": "Montaj Hattı 1 (Yeni)", "status": "offline", "stream": {"fps": 30}},
    )
    assert r.status_code == 200, r.text
    cam = r.json()
    assert cam["name"] == "Montaj Hattı 1 (Yeni)"
    assert cam["status"] == "offline"
    assert cam["stream"]["fps"] == 30
    # Gönderilmeyen alanlar değişmez
    assert cam["stream"]["resolution"] == before["stream"]["resolution"]
    assert cam["location"] == before["location"]
    assert cam["updatedAt"] >= before["updatedAt"]


def test_update_camera_zone_and_code(client: TestClient) -> None:
    r = client.patch(f"{API}/cameras/cam-03", json={"zoneId": "zone-hazmat", "code": "CAM-03B"})
    assert r.status_code == 200
    assert r.json()["zone"]["name"] == "Tehlikeli Madde Alanı"
    assert r.json()["code"] == "CAM-03B"

    # Kendi koduyla güncelleme çakışma sayılmaz
    assert client.patch(f"{API}/cameras/cam-03", json={"code": "CAM-03B"}).status_code == 200


def test_update_camera_errors(client: TestClient) -> None:
    assert_error(client.patch(f"{API}/cameras/cam-99", json={"name": "X"}), 404, "not_found")
    assert_error(client.patch(f"{API}/cameras/cam-01", json={}), 422, "validation_error")
    assert_error(client.patch(f"{API}/cameras/cam-01", json={"name": None}), 422, "validation_error")
    assert_error(client.patch(f"{API}/cameras/cam-01", json={"id": "x"}), 422, "validation_error")
    assert_error(client.patch(f"{API}/cameras/cam-01", json={"code": "CAM-02"}), 409, "conflict")
    assert_error(
        client.patch(f"{API}/cameras/cam-01", json={"zoneId": "nope"}), 422, "invalid_reference"
    )


# --- Silme -----------------------------------------------------------------


def test_delete_camera(client: TestClient) -> None:
    created = client.post(f"{API}/cameras", json=NEW_CAMERA).json()

    r = client.delete(f"{API}/cameras/{created['id']}")
    assert r.status_code == 204
    assert r.content == b""
    assert_error(client.get(f"{API}/cameras/{created['id']}"), 404, "not_found")
    assert_error(client.delete(f"{API}/cameras/{created['id']}"), 404, "not_found")


def test_delete_camera_with_violations_is_blocked(client: TestClient) -> None:
    err = assert_error(client.delete(f"{API}/cameras/cam-01"), 409, "conflict")
    assert "ihlal" in err["message"]
    assert client.get(f"{API}/cameras/cam-01").status_code == 200


def test_unknown_route_and_method(client: TestClient) -> None:
    assert_error(client.get(f"{API}/nope"), 404, "not_found")
    assert_error(client.put(f"{API}/cameras/cam-01", json={}), 405, "method_not_allowed")
