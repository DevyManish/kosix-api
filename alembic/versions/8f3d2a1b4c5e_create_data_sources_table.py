"""create_data_sources_table

Revision ID: 8f3d2a1b4c5e
Revises: 42a4bf055c05
Create Date: 2026-02-14 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '8f3d2a1b4c5e'
down_revision: Union[str, Sequence[str], None] = '42a4bf055c05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create data_sources table."""
    op.create_table(
        'data_sources',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('team_id', sa.UUID(), nullable=True),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['created_by'],
            ['accounts.id'],
            name=op.f('fk_data_sources_created_by_accounts'),
            ondelete='SET NULL'
        ),
        sa.ForeignKeyConstraint(
            ['team_id'],
            ['teams.id'],
            name=op.f('fk_data_sources_team_id_teams'),
            ondelete='SET NULL'
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_data_sources'))
    )
    op.create_index(op.f('ix_data_sources_id'), 'data_sources', ['id'], unique=False)
    op.create_index(op.f('ix_data_sources_title'), 'data_sources', ['title'], unique=True)
    op.create_index(op.f('ix_data_sources_created_by'), 'data_sources', ['created_by'], unique=False)
    op.create_index(op.f('ix_data_sources_team_id'), 'data_sources', ['team_id'], unique=False)


def downgrade() -> None:
    """Drop data_sources table."""
    op.drop_index(op.f('ix_data_sources_team_id'), table_name='data_sources')
    op.drop_index(op.f('ix_data_sources_created_by'), table_name='data_sources')
    op.drop_index(op.f('ix_data_sources_title'), table_name='data_sources')
    op.drop_index(op.f('ix_data_sources_id'), table_name='data_sources')
    op.drop_table('data_sources')
