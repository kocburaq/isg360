"""Test altyapısı.

Her test kendi geçici SQLite dosyasını kullanır. Şema Alembic migration'larıyla
oluşturulur (böylece migration'lar da her test çalıştırmasında doğrulanır),
ardından örnek veri yüklenir.
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import BACKEND_DIR, Settings, get_settings
from app.db.seed import seed_demo_data
from app.db.session import build_engine, build_session_factory, get_db
from app.main import create_app


def run_migrations(url: str, revision: str = "head") -> None:
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", url)
    command.upgrade(cfg, revision)


@pytest.fixture
def db_url(tmp_path: Path) -> str:
    return f"sqlite:///{(tmp_path / 'test.db').as_posix()}"


@pytest.fixture
def settings(db_url: str) -> Settings:
    return Settings(  # type: ignore[call-arg]
        _env_file=None,
        app_env="test",
        database_url=db_url,
        # Arka plan canlılık döngüsü testlerde kapalı; mantık doğrudan test edilir
        edge_liveness_check_interval_s=0,
    )


@pytest.fixture
def engine(db_url: str) -> Iterator[Engine]:
    run_migrations(db_url)
    engine = build_engine(db_url)
    yield engine
    engine.dispose()


@pytest.fixture
def session_factory(engine: Engine) -> sessionmaker[Session]:
    factory = build_session_factory(engine)
    with factory() as session:
        seed_demo_data(session)
    return factory


@pytest.fixture
def db(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    with session_factory() as session:
        yield session


def make_client(settings: Settings, session_factory: sessionmaker[Session]) -> TestClient:
    app = create_app(settings)

    def _get_db() -> Iterator[Session]:
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = _get_db
    app.dependency_overrides[get_settings] = lambda: settings
    return TestClient(app)


@pytest.fixture
def client(settings: Settings, session_factory: sessionmaker[Session]) -> Iterator[TestClient]:
    with make_client(settings, session_factory) as c:
        yield c


API = "/api/v1"
