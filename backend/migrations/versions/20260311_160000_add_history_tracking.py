"""add_history_tracking

Revision ID: add_history_tracking
Revises: 85723c387107
Create Date: 2026-03-11 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_history_tracking'
down_revision: Union[str, None] = '85723c387107'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add 'latest' column with default True
    op.add_column(
        'claim_insurances',
        sa.Column('latest', sa.Boolean(), nullable=False, server_default='true')
    )
    
    # Create index on 'latest' column for efficient filtering
    op.create_index('ix_claim_insurances_latest', 'claim_insurances', ['latest'])
    
    # Create index on 'claim_number' for efficient grouping of history
    op.create_index('ix_claim_insurances_claim_number', 'claim_insurances', ['claim_number'])
    
    # Remove unique constraint on claim_number (to allow multiple versions)
    op.drop_constraint('claim_insurances_claim_number_key', 'claim_insurances', type_='unique')


def downgrade() -> None:
    # Re-add unique constraint on claim_number
    # Note: This may fail if there are duplicate claim_numbers
    op.create_unique_constraint('claim_insurances_claim_number_key', 'claim_insurances', ['claim_number'])
    
    # Drop indexes
    op.drop_index('ix_claim_insurances_claim_number', table_name='claim_insurances')
    op.drop_index('ix_claim_insurances_latest', table_name='claim_insurances')
    
    # Remove 'latest' column
    op.drop_column('claim_insurances', 'latest')
