"""Password reset tokens

Revision ID: c439c5c8e996
Revises: 99db70c7ff3d
Create Date: 2023-10-02 08:36:08.372461

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = "c439c5c8e996"
down_revision = "99db70c7ff3d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "password_reset_token",
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("current_timestamp"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("expiration_date", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("user_id", "token"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("password_reset_token")
    # ### end Alembic commands ###
