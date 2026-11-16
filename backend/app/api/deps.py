"""Ortak FastAPI bağımlılıkları."""

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db

DbSession = Annotated[Session, Depends(get_db)]
AppSettings = Annotated[Settings, Depends(get_settings)]

MAX_PAGE_SIZE = 500


@dataclass(frozen=True)
class Pagination:
    page: int
    page_size: int


def pagination(
    page: Annotated[int, Query(ge=1, description="1'den başlayan sayfa numarası")] = 1,
    page_size: Annotated[
        int, Query(ge=1, le=MAX_PAGE_SIZE, description="Sayfa başına kayıt")
    ] = 50,
) -> Pagination:
    return Pagination(page=page, page_size=page_size)


PageParams = Annotated[Pagination, Depends(pagination)]
