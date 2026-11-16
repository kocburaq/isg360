"""Veritabanı bağlantısı ve oturum yönetimi."""

from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


def build_engine(url: str, echo: bool = False) -> Engine:
    is_sqlite = url.startswith("sqlite")
    engine = create_engine(
        url,
        echo=echo,
        # SQLite bağlantısı FastAPI iş parçacıkları arasında paylaşılabilsin
        connect_args={"check_same_thread": False} if is_sqlite else {},
        pool_pre_ping=not is_sqlite,
    )
    if is_sqlite:

        @event.listens_for(engine, "connect")
        def _sqlite_pragmas(dbapi_connection, _record):  # type: ignore[no-untyped-def]
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")  # SQLite'ta FK kontrolleri varsayılan kapalı
            cursor.close()

    return engine


def build_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    return build_engine(settings.resolved_database_url, echo=settings.db_echo)


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return build_session_factory(get_engine())


def get_db() -> Iterator[Session]:
    """FastAPI bağımlılığı: istek başına bir oturum."""
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()
