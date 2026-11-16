"""Alembic ortamı: bağlantı adresi uygulama ayarlarından (DATABASE_URL) gelir."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import Connection

import app.models  # noqa: F401  — tüm modelleri metadata'ya kaydeder
from app.core.config import get_settings
from app.db.base import Base, UTCDateTime
from app.db.session import build_engine

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def _database_url() -> str:
    # Testler gibi programatik çağrılar `sqlalchemy.url` ile adres geçebilir.
    return config.get_main_option("sqlalchemy.url") or get_settings().resolved_database_url


def _render_item(type_: str, obj: object, autogen_context: object) -> str | bool:
    # Uygulamaya özel UTCDateTime, migration dosyalarında standart tip olarak yazılır;
    # böylece migration'lar uygulama koduna bağımlı olmaz.
    if type_ == "type" and isinstance(obj, UTCDateTime):
        return "sa.DateTime(timezone=True)"
    return False


def _configure(connection: Connection | None = None, url: str | None = None) -> None:
    context.configure(
        connection=connection,
        url=url,
        target_metadata=target_metadata,
        # SQLite ALTER TABLE kısıtları için tabloyu yeniden oluşturarak değiştirir
        render_as_batch=True,
        compare_type=True,
        render_item=_render_item,
        literal_binds=connection is None,
        dialect_opts={"paramstyle": "named"} if connection is None else {},
    )


def run_migrations_offline() -> None:
    _configure(url=_database_url())
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = build_engine(_database_url())
    is_sqlite = engine.dialect.name == "sqlite"
    with engine.connect() as connection:
        if is_sqlite:
            # SQLite "batch" migration'ları tabloyu yeniden oluşturur; FK kontrolü açıkken
            # başvurulan tablo silinemez. Kontrol migration süresince kapatılır
            # (PRAGMA yalnızca işlem dışında etkilidir) ve sonunda bütünlük doğrulanır.
            connection.exec_driver_sql("PRAGMA foreign_keys=OFF")
            connection.commit()
        _configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()
        if is_sqlite:
            broken = connection.exec_driver_sql("PRAGMA foreign_key_check").fetchall()
            connection.exec_driver_sql("PRAGMA foreign_keys=ON")
            if broken:
                raise RuntimeError(f"Migration sonrası yabancı anahtar ihlalleri: {broken[:5]}")
    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
