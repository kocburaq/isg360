from typing import Annotated

from fastapi import APIRouter, Path, Query, Response, status

from app.api.deps import DbSession, PageParams
from app.core.errors import error_body
from app.models.enums import CameraStatus
from app.repositories.cameras import CameraFilter, ZoneRepository
from app.schemas.camera import CameraCreate, CameraOut, CameraUpdate, ZoneOut
from app.schemas.common import Page
from app.services.cameras import CameraService

router = APIRouter(tags=["Kameralar"])

CameraId = Annotated[str, Path(min_length=1, max_length=64)]

_ERRORS = {
    404: {"description": "Kamera bulunamadı", "content": {"application/json": {"example": error_body("not_found", "Kamera bulunamadı: cam-99")}}},
    409: {"description": "Çakışma (ör. kod kullanımda)"},
    422: {"description": "Geçersiz istek"},
}  # fmt: skip


@router.get("/zones", response_model=list[ZoneOut], summary="Fabrika bölgelerini listele")
def list_zones(db: DbSession) -> list[ZoneOut]:
    return [ZoneOut.model_validate(z) for z in ZoneRepository(db).list()]


@router.get("/cameras", response_model=Page[CameraOut], summary="Kameraları listele")
def list_cameras(
    db: DbSession,
    paging: PageParams,
    status_: Annotated[
        list[CameraStatus] | None,
        Query(alias="status", description="Duruma göre filtre (tekrarlanabilir)"),
    ] = None,
    zone_id: Annotated[str | None, Query(max_length=64)] = None,
    q: Annotated[
        str | None, Query(max_length=100, description="Kod, ad veya konumda arama")
    ] = None,
) -> Page[CameraOut]:
    f = CameraFilter(statuses=status_ or (), zone_id=zone_id, search=q or None)
    items, total = CameraService(db).list(f, page=paging.page, page_size=paging.page_size)
    return Page(
        items=[CameraOut.from_model(c) for c in items],
        total=total,
        page=paging.page,
        page_size=paging.page_size,
    )


@router.get(
    "/cameras/{camera_id}",
    response_model=CameraOut,
    responses={404: _ERRORS[404]},
    summary="Kamera ayrıntısı",
)
def get_camera(camera_id: CameraId, db: DbSession) -> CameraOut:
    return CameraOut.from_model(CameraService(db).get(camera_id))


@router.post(
    "/cameras",
    response_model=CameraOut,
    status_code=status.HTTP_201_CREATED,
    responses={409: _ERRORS[409], 422: _ERRORS[422]},
    summary="Kamera ekle",
)
def create_camera(body: CameraCreate, db: DbSession, response: Response) -> CameraOut:
    camera = CameraService(db).create(body)
    response.headers["Location"] = f"/api/v1/cameras/{camera.id}"
    return CameraOut.from_model(camera)


@router.patch(
    "/cameras/{camera_id}",
    response_model=CameraOut,
    responses=_ERRORS,
    summary="Kamera güncelle (kısmi)",
)
def update_camera(camera_id: CameraId, body: CameraUpdate, db: DbSession) -> CameraOut:
    return CameraOut.from_model(CameraService(db).update(camera_id, body))


@router.delete(
    "/cameras/{camera_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: _ERRORS[404],
        409: {"description": "Kameraya ait ihlal kayıtları olduğu için silinemez"},
    },
    summary="Kamera sil",
)
def delete_camera(camera_id: CameraId, db: DbSession) -> Response:
    CameraService(db).delete(camera_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
