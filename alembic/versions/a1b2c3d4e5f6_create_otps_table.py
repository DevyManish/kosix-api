"""create_otps_table

Revision ID: a1b2c3d4e5f6
Revises: 8f3d2a1b4c5e
Create Date: 2026-02-14 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '8f3d2a1b4c5e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create otps table for email verification."""
    op.create_table(
        'otps',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('account_id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('otp_code', sa.String(length=6), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=False, default=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['account_id'],
            ['accounts.id'],
            name=op.f('fk_otps_account_id_accounts'),
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_otps'))
    )
    op.create_index(op.f('ix_otps_id'), 'otps', ['id'], unique=False)
    op.create_index(op.f('ix_otps_account_id'), 'otps', ['account_id'], unique=False)
    op.create_index(op.f('ix_otps_email'), 'otps', ['email'], unique=False)


def downgrade() -> None:
    """Drop otps table."""
    op.drop_index(op.f('ix_otps_email'), table_name='otps')
    op.drop_index(op.f('ix_otps_account_id'), table_name='otps')
    op.drop_index(op.f('ix_otps_id'), table_name='otps')
    op.drop_table('otps')
