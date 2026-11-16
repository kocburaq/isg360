"""Merkez edge API istemcisi (/edge/v1)."""

from collections.abc import Sequence
from typing import Any

import httpx
from fcs_contracts import (
    CONTRACT_VERSION,
    CONTRACT_VERSION_HEADER,
    EdgeConfig,
    EventBatch,
    EventBatchResult,
    Heartbeat,
    HeartbeatResult,
    ViolationEvent,
)

from fcs_vision import __version__


class CentralError(Exception):
    """Merkezden dönen hata. `code`, backend hata sözleşmesindeki koddur."""

    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(f"{status} {code}: {message}")
        self.status = status
        self.code = code
        self.message = message


class AuthError(CentralError):
    """Anahtar geçersiz veya node devre dışı: yeniden denemek işe yaramaz."""


class TransientError(Exception):
    """Ağ hatası, zaman aşımı veya 5xx: daha sonra yeniden denenebilir."""


class CentralClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        *,
        timeout_s: float = 10,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("Edge API anahtarı tanımlı değil (EDGE_API_KEY).")
        self._http = httpx.Client(
            base_url=base_url,
            timeout=timeout_s,
            transport=transport,
            headers={
                "Authorization": f"Bearer {api_key}",
                CONTRACT_VERSION_HEADER: CONTRACT_VERSION,
                "User-Agent": f"fcs-vision/{__version__}",
            },
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "CentralClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        try:
            response = self._http.request(method, path, **kwargs)
        except httpx.TransportError as exc:
            raise TransientError(f"Merkeze ulaşılamadı: {exc.__class__.__name__}") from exc

        if response.status_code >= 500:
            raise TransientError(f"Merkez hatası: HTTP {response.status_code}")
        if response.status_code >= 400:
            code, message = "http_error", response.text[:200]
            try:
                err = response.json()["error"]
                code, message = err["code"], err["message"]
            except (ValueError, KeyError, TypeError):
                pass
            error_cls = AuthError if response.status_code in (401, 403) else CentralError
            raise error_cls(response.status_code, code, message)
        return response

    def get_config(self, etag: str | None = None) -> tuple[EdgeConfig | None, str | None]:
        """Yapılandırmayı çeker. Değişmediyse (304) (None, etag) döner."""
        headers = {"If-None-Match": etag} if etag else {}
        response = self._request("GET", "/config", headers=headers)
        new_etag = response.headers.get("etag", etag)
        if response.status_code == 304:
            return None, new_etag
        return EdgeConfig.model_validate_json(response.content), new_etag

    def send_heartbeat(self, heartbeat: Heartbeat) -> HeartbeatResult:
        response = self._request("POST", "/heartbeat", json=heartbeat.model_dump(mode="json"))
        return HeartbeatResult.model_validate_json(response.content)

    def send_events(self, events: Sequence[ViolationEvent]) -> EventBatchResult:
        batch = EventBatch(events=list(events))
        response = self._request("POST", "/events", json=batch.model_dump(mode="json"))
        return EventBatchResult.model_validate_json(response.content)
