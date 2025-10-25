"""add_is_analyzed_flag_to_reviews

Revision ID: ff9349e35b20
Revises: b4ece80b4ab4
Create Date: 2025-10-26 17:49:20.424252

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff9349e35b20'
down_revision: Union[str, Sequence[str], None] = '8f3c2b9d5e14'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('reviews', sa.Column('is_analyzed', sa.Boolean(), nullable=False, server_default='false'))
    op.create_index(op.f('ix_reviews_is_analyzed'), 'reviews', ['is_analyzed'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_reviews_is_analyzed'), table_name='reviews')
    op.drop_column('reviews', 'is_analyzed')
