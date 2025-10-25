"""add analysis tables

Revision ID: 8f3c2b9d5e14
Revises: 07d7be8aee36
Create Date: 2025-10-26 16:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8f3c2b9d5e14"
down_revision: str | Sequence[str] | None = "07d7be8aee36"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ReviewAnalysis table
    op.create_table(
        "review_analysis",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("review_id", sa.Integer(), nullable=False),
        sa.Column("sentiment", sa.String(length=50), nullable=False),
        sa.Column("keywords", sa.ARRAY(sa.String()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["review_id"],
            ["reviews.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("review_id"),
    )
    op.create_index(
        op.f("ix_review_analysis_review_id"),
        "review_analysis",
        ["review_id"],
        unique=True,
    )

    # Insights table
    op.create_table(
        "insights",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("app_id", sa.String(length=255), nullable=False),
        sa.Column("review_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["review_id"],
            ["reviews.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_insights_app_id"), "insights", ["app_id"], unique=False)
    op.create_index(op.f("ix_insights_review_id"), "insights", ["review_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_insights_review_id"), table_name="insights")
    op.drop_index(op.f("ix_insights_app_id"), table_name="insights")
    op.drop_table("insights")
    op.drop_index(op.f("ix_review_analysis_review_id"), table_name="review_analysis")
    op.drop_table("review_analysis")

