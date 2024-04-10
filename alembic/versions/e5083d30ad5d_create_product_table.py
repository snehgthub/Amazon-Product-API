"""create product table

Revision ID: e5083d30ad5d
Revises: 09054dc89446
Create Date: 2024-04-10 14:47:54.899307

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e5083d30ad5d"
down_revision: Union[str, None] = "09054dc89446"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "product",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("asin", sa.String(), nullable=True, index=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("current_price", sa.String(), nullable=False),
        sa.Column("previous_price", sa.String(), nullable=True),
        sa.Column("discount", sa.String(), nullable=True),
        sa.Column("ratings_count", sa.String(), nullable=True),
        sa.Column("star_ratings", sa.String(), nullable=True),
        sa.Column("description", sa.JSON(), nullable=True),
        sa.Column("image_link", sa.String(), nullable=True),
        sa.Column(
            "first_fetch_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("user.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_product_asin"), table_name="product")
    op.drop_table("product")
