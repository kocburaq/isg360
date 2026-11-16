"""Edge (saha sunucusu) API'si — /edge/v1.

Panel API'sinden (/api/v1) ayrıdır: yalnızca edge node'lar kullanır ve her istek
`Authorization: Bearer <edge API anahtarı>` başlığı gerektirir.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fcs_contracts import (
    CONTRACT_VERSION,
    CONTRACT_VERSION_HEADER,
    EdgeConfig,
    EventBatch,
    EventBatchResult,
    Heartbeat,
    HeartbeatResult,
)

from app.api.deps import AppSettings, DbSession
from app.core.errors import AppError
from app.models import EdgeNode
from app.services.edge import EdgeService, authenticate_edge_node

_bearer = HTTPBearer(auto_error=False, description="Edge node API anahtarı")


class UnsupportedContractError(AppError):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "unsupported_contract"


def current_edge_node(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    contract_version: Annotated[str | None, Header(alias=CONTRACT_VERSION_HEADER)] = None,
) -> EdgeNode:
    if contract_version is not None and contract_version != CONTRACT_VERSION:
        raise UnsupportedContractError(
            f"Desteklenmeyen sözleşme sürümü: {contract_version} (beklenen {CONTRACT_VERSION})."
        )
    return authenticate_edge_node(db, credentials.credentials if credentials else None)


EdgeNodeDep = Annotated[EdgeNode, Depends(current_edge_node)]

_AUTH_ERRORS = {
    401: {"description": "API anahtarı eksik veya geçersiz"},
    403: {"description": "Edge node devre dışı"},
}

router = APIRouter(tags=["Edge (saha sunucusu)"], responses=_AUTH_ERRORS)


@router.get(
    "/config",
    response_model=EdgeConfig,
    summary="Edge yapılandırması",
    responses={304: {"description": "Yapılandırma değişmedi (If-None-Match)"}},
)
def get_config(
    request: Request, node: EdgeNodeDep, db: DbSession, settings: AppSettings
) -> EdgeConfig | Response:
    config = EdgeService(db, node, settings).build_config()
    etag = f'"{config.config_version}"'
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=status.HTTP_304_NOT_MODIFIED, headers={"ETag": etag})
    return Response(
        content=config.model_dump_json(),
        media_type="application/json",
        headers={"ETag": etag},
    )


@router.post("/heartbeat", response_model=HeartbeatResult, summary="Edge ve kamera canlılığı")
def post_heartbeat(
    body: Heartbeat, node: EdgeNodeDep, db: DbSession, settings: AppSettings
) -> HeartbeatResult:
    return EdgeService(db, node, settings).heartbeat(body)


@router.post(
    "/events",
    response_model=EventBatchResult,
    summary="İhlal olaylarını gönder (toplu, idempotent)",
    description=(
        "Her olay `eventId` ile tanımlanır. Aynı olay tekrar gönderilirse `duplicate`, "
        "bitiş zamanı eklenmişse `updated` döner. `rejected` olaylar yeniden denenmemelidir."
    ),
)
def post_events(
    body: EventBatch, node: EdgeNodeDep, db: DbSession, settings: AppSettings
) -> EventBatchResult:
    return EdgeService(db, node, settings).ingest_events(body)
