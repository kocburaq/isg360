"""v1 API yönlendiricisi.

Yeni bir modül (ör. drones, work_orders) eklemek için:
models → repositories → services → schemas → api/v1/endpoints dosyalarını oluşturup
router'ı buraya kaydetmek yeterlidir.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import cameras, system, violations

api_router = APIRouter()
api_router.include_router(system.router)
api_router.include_router(cameras.router)
api_router.include_router(violations.router)
