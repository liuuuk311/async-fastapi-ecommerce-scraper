"""hot categories

Revision ID: 2f66042ec8f3
Revises: 61f65d8e36b8
Create Date: 2023-10-10 08:58:03.562281

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = "2f66042ec8f3"
down_revision = "61f65d8e36b8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "category",
        sa.Column(
            "is_hot", sa.Boolean(), server_default=sa.text("FALSE"), nullable=False
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("category", "is_hot")
    # ### end Alembic commands ###
