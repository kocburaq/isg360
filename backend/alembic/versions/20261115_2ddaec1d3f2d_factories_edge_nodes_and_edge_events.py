"""factories, edge nodes and edge events

- factories tablosu; mevcut bölgeler "fac-default" fabrikasına bağlanır
- edge_nodes tablosu (API anahtarının yalnızca SHA-256 özeti saklanır)
- cameras.edge_node_id
- ppe_violations: event_id (benzersiz), edge_node_id, ended_at, rule_id, track_id, model_ref
- violation_type CHECK kısıtına restricted_area ve missing_harness eklenir

Revision ID: 2ddaec1d3f2d
Revises: 0ba5cd031ac7
Create Date: 2026-11-15 19:49:27.328835

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2ddaec1d3f2d'
down_revision: Union[str, Sequence[str], None] = '0ba5cd031ac7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DEFAULT_FACTORY_ID = 'fac-default'

OLD_VIOLATION_TYPES = ("missing_ppe",)
NEW_VIOLATION_TYPES = ("missing_ppe", "restricted_area", "missing_harness")


def _in_list(values: tuple[str, ...]) -> str:
    return ", ".join(f"'{v}'" for v in values)


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('factories',
    sa.Column('id', sa.String(length=64), nullable=False),
    sa.Column('code', sa.String(length=16), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('city', sa.String(length=80), nullable=True),
    sa.Column('timezone', sa.String(length=64), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_factories')),
    sa.UniqueConstraint('code', name=op.f('uq_factories_code'))
    )

    # Veri taşıma: bölge varsa hepsi varsayılan fabrikaya bağlanır (seed ile aynı değerler).
    op.execute(
        sa.text(
            "INSERT INTO factories (id, code, name, city, timezone) "
            "SELECT :id, 'F01', 'Merkez Fabrika', 'İstanbul', 'Europe/Istanbul' "
            "WHERE EXISTS (SELECT 1 FROM factory_zones)"
        ).bindparams(id=DEFAULT_FACTORY_ID)
    )

    op.create_table('edge_nodes',
    sa.Column('id', sa.String(length=64), nullable=False),
    sa.Column('factory_id', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('api_key_hash', sa.String(length=64), nullable=False),
    sa.Column('api_key_prefix', sa.String(length=16), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('software_version', sa.String(length=32), nullable=True),
    sa.Column('reports_simulated', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['factory_id'], ['factories.id'], name=op.f('fk_edge_nodes_factory_id_factories'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_edge_nodes')),
    sa.UniqueConstraint('api_key_hash', name=op.f('uq_edge_nodes_api_key_hash'))
    )
    with op.batch_alter_table('edge_nodes', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_edge_nodes_factory_id'), ['factory_id'], unique=False)

    with op.batch_alter_table('cameras', schema=None) as batch_op:
        batch_op.add_column(sa.Column('edge_node_id', sa.String(length=64), nullable=True))
        batch_op.create_index(batch_op.f('ix_cameras_edge_node_id'), ['edge_node_id'], unique=False)
        batch_op.create_foreign_key(batch_op.f('fk_cameras_edge_node_id_edge_nodes'), 'edge_nodes', ['edge_node_id'], ['id'], ondelete='RESTRICT')

    # factory_id önce boş eklenir, mevcut satırlar doldurulur, sonra zorunlu yapılır.
    with op.batch_alter_table('factory_zones', schema=None) as batch_op:
        batch_op.add_column(sa.Column('factory_id', sa.String(length=64), nullable=True))
    op.execute(
        sa.text("UPDATE factory_zones SET factory_id = :id WHERE factory_id IS NULL").bindparams(
            id=DEFAULT_FACTORY_ID
        )
    )
    with op.batch_alter_table('factory_zones', schema=None) as batch_op:
        batch_op.alter_column('factory_id', existing_type=sa.String(length=64), nullable=False)
        batch_op.create_index(batch_op.f('ix_factory_zones_factory_id'), ['factory_id'], unique=False)
        batch_op.create_foreign_key(batch_op.f('fk_factory_zones_factory_id_factories'), 'factories', ['factory_id'], ['id'], ondelete='RESTRICT')

    with op.batch_alter_table('ppe_violations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('event_id', sa.String(length=36), nullable=True))
        batch_op.add_column(sa.Column('edge_node_id', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('rule_id', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('track_id', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('model_ref', sa.String(length=100), nullable=True))
        batch_op.create_index(batch_op.f('ix_ppe_violations_edge_node_id'), ['edge_node_id'], unique=False)
        batch_op.create_unique_constraint(batch_op.f('uq_ppe_violations_event_id'), ['event_id'])
        batch_op.create_foreign_key(batch_op.f('fk_ppe_violations_edge_node_id_edge_nodes'), 'edge_nodes', ['edge_node_id'], ['id'], ondelete='RESTRICT')
        # Enum değer kümesi genişledi (autogenerate CHECK değişikliklerini algılamaz)
        batch_op.drop_constraint(batch_op.f('ck_ppe_violations_violation_type'), type_='check')
        batch_op.create_check_constraint(
            'violation_type', f"violation_type IN ({_in_list(NEW_VIOLATION_TYPES)})"
        )


def downgrade() -> None:
    """Downgrade schema.

    Not: Yeni ihlal türlerinde (restricted_area, missing_harness) kayıt varsa
    CHECK kısıtı geri yüklenemez ve downgrade bilinçli olarak hata verir.
    """
    with op.batch_alter_table('ppe_violations', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('ck_ppe_violations_violation_type'), type_='check')
        batch_op.create_check_constraint(
            'violation_type', f"violation_type IN ({_in_list(OLD_VIOLATION_TYPES)})"
        )
        batch_op.drop_constraint(batch_op.f('fk_ppe_violations_edge_node_id_edge_nodes'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('uq_ppe_violations_event_id'), type_='unique')
        batch_op.drop_index(batch_op.f('ix_ppe_violations_edge_node_id'))
        batch_op.drop_column('model_ref')
        batch_op.drop_column('track_id')
        batch_op.drop_column('rule_id')
        batch_op.drop_column('ended_at')
        batch_op.drop_column('edge_node_id')
        batch_op.drop_column('event_id')

    with op.batch_alter_table('factory_zones', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_factory_zones_factory_id_factories'), type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_factory_zones_factory_id'))
        batch_op.drop_column('factory_id')

    with op.batch_alter_table('cameras', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_cameras_edge_node_id_edge_nodes'), type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_cameras_edge_node_id'))
        batch_op.drop_column('edge_node_id')

    with op.batch_alter_table('edge_nodes', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_edge_nodes_factory_id'))

    op.drop_table('edge_nodes')
    op.drop_table('factories')
