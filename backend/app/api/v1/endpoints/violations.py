from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Path, Query

from app.api.deps import DbSession, PageParams
from app.core.errors import AppError
from app.models.enums import PpeClass, ViolationSeverity, ViolationStatus, ViolationType
from app.repositories.violations import ViolationFilter
from app.schemas.common import Page
from app.schemas.violation import ViolationOut, ViolationUpdate
from app.services.violations import ViolationService

router = APIRouter(prefix="/violations", tags=["İhlaller"])

ViolationId = Annotated[str, Path(min_length=1, max_length=64)]


class InvalidQueryError(AppError):
    status_code = 422
    code = "validation_error"


@router.get("", response_model=Page[ViolationOut], summary="KKD ihlallerini listele")
def list_violations(
    db: DbSession,
    paging: PageParams,
    camera_id: Annotated[str | None, Query(max_length=64)] = None,
    factory_id: Annotated[str | None, Query(max_length=64)] = None,
    zone_id: Annotated[str | None, Query(max_length=64)] = None,
    type_: Annotated[
        list[ViolationType] | None,
        Query(alias="type", description="İhlal türüne göre filtre (tekrarlanabilir)"),
    ] = None,
    status_: Annotated[
        list[ViolationStatus] | None,
        Query(alias="status", description="Duruma göre filtre (tekrarlanabilir)"),
    ] = None,
    severity: Annotated[list[ViolationSeverity] | None, Query()] = None,
    ppe: Annotated[
        list[PpeClass] | None, Query(description="Eksik KKD sınıfına göre filtre")
    ] = None,
    detected_from: Annotated[datetime | None, Query(alias="from")] = None,
    detected_to: Annotated[datetime | None, Query(alias="to")] = None,
    order: Annotated[str, Query(pattern="^(asc|desc)$")] = "desc",
) -> Page[ViolationOut]:
    for value in (detected_from, detected_to):
        if value is not None and value.tzinfo is None:
            raise InvalidQueryError(
                "Tarih filtreleri zaman dilimi içermelidir (ör. 2026-10-19T00:00:00+03:00)."
            )
    f = ViolationFilter(
        camera_id=camera_id,
        factory_id=factory_id,
        zone_id=zone_id,
        statuses=status_ or (),
        types=type_ or (),
        severities=severity or (),
        ppe=ppe or (),
        detected_from=detected_from,
        detected_to=detected_to,
        newest_first=order == "desc",
    )
    items, total = ViolationService(db).list(f, page=paging.page, page_size=paging.page_size)
    return Page(
        items=[ViolationOut.from_model(v) for v in items],
        total=total,
        page=paging.page,
        page_size=paging.page_size,
    )


@router.get(
    "/{violation_id}",
    response_model=ViolationOut,
    responses={404: {"description": "İhlal kaydı bulunamadı"}},
    summary="İhlal ayrıntısı",
)
def get_violation(violation_id: ViolationId, db: DbSession) -> ViolationOut:
    return ViolationOut.from_model(ViolationService(db).get(violation_id))


@router.patch(
    "/{violation_id}",
    response_model=ViolationOut,
    responses={404: {"description": "İhlal kaydı bulunamadı"}, 422: {"description": "Geçersiz istek"}},
    summary="İhlal durumunu / açıklamasını güncelle",
)
def update_violation(
    violation_id: ViolationId, body: ViolationUpdate, db: DbSession
) -> ViolationOut:
    return ViolationOut.from_model(ViolationService(db).update(violation_id, body))
