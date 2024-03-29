"""suggested store

Revision ID: b4e462d67183
Revises: a1769ab8eb7a
Create Date: 2023-06-07 08:53:48.869650

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "b4e462d67183"
down_revision = "a1769ab8eb7a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "suggested_store",
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("current_timestamp"),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("website", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("suggested_store")
    # ### end Alembic commands ###
