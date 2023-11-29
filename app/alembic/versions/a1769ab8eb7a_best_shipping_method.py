"""best shipping method

Revision ID: a1769ab8eb7a
Revises: da22ce9e9901
Create Date: 2023-06-04 18:30:54.466461

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "a1769ab8eb7a"
down_revision = "da22ce9e9901"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "product", sa.Column("best_shipping_method_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        "product_shipping_method",
        "product",
        "shipping_method",
        ["best_shipping_method_id"],
        ["id"],
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("product_shipping_method", "product", type_="foreignkey")
    op.drop_column("product", "best_shipping_method_id")
    # ### end Alembic commands ###
