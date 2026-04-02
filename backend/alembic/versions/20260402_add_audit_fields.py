"""Add audit fields to transactions and users

Revision ID: add_audit_fields
Revises: 4e8bd9f0467a
Create Date: 2026-04-02 09:27:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_audit_fields'
down_revision: Union[str, None] = '4e8bd9f0467a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use batch mode for SQLite compatibility
    with op.batch_alter_table('transactions', recreate='auto') as batch_op:
        # Add audit columns
        batch_op.add_column(sa.Column('created_by', sa.String(length=36), nullable=True))
        batch_op.add_column(sa.Column('updated_by', sa.String(length=36), nullable=True))

    # Create indexes (not supported in batch mode for FK, but we add regular indexes)
    op.create_index('ix_transactions_updated_by', 'transactions', ['updated_by'], unique=False)

    with op.batch_alter_table('users', recreate='auto') as batch_op:
        batch_op.add_column(sa.Column('updated_by', sa.String(length=36), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('users', recreate='auto') as batch_op:
        batch_op.drop_column('updated_by')

    op.drop_index('ix_transactions_updated_by', table_name='transactions')

    with op.batch_alter_table('transactions', recreate='auto') as batch_op:
        batch_op.drop_column('updated_by')
        batch_op.drop_column('created_by')