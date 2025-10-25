"""update_insights_add_review_id

Revision ID: b4ece80b4ab4
Revises: 8f3c2b9d5e14
Create Date: 2025-10-26 15:36:05.265727

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4ece80b4ab4'
down_revision: Union[str, Sequence[str], None] = '8f3c2b9d5e14'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_table("insights")
    op.create_table(
        "insights",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("app_id", sa.String(length=255), nullable=False),
        sa.Column("review_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["review_id"], ["reviews.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_insights_app_id"), "insights", ["app_id"], unique=False)
    op.create_index(op.f("ix_insights_review_id"), "insights", ["review_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_insights_review_id"), table_name="insights")
    op.drop_index(op.f("ix_insights_app_id"), table_name="insights")
    op.drop_table("insights")
    op.create_table(
        "insights",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("app_id", sa.String(length=255), nullable=False),
        sa.Column("insight_type", sa.String(length=50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_insights_app_id"), "insights", ["app_id"], unique=False)
