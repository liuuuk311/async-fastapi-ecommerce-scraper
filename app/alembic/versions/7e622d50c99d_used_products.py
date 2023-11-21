"""used products

Revision ID: 7e622d50c99d
Revises: 322dd904d079
Create Date: 2023-11-16 09:19:04.521515

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "7e622d50c99d"
down_revision = "322dd904d079"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "used_product",
        sa.Column(
            "currency",
            postgresql.ENUM(
                "EUR", "USD", "AUD", "CAD", "GBP", name="currency", create_type=False
            ),
            nullable=True,
        ),
        sa.Column(
            "condition",
            postgresql.ENUM(
                "never_opened",
                "like_new",
                "excellent",
                "good",
                "poor",
                "to_fix",
                "broken",
                name="usedproductcondition",
            ),
            nullable=True,
        ),
        sa.Column(
            "shipping_method",
            postgresql.ENUM(
                "hand_delivery",
                "included",
                "excluded",
                name="usedproductshippingmethod",
            ),
            nullable=True,
        ),
        sa.Column(
            "public_id",
            sqlmodel.sql.sqltypes.GUID(),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("current_timestamp"),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("price", sa.Numeric(precision=7, scale=2), nullable=False),
        sa.Column("image", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("is_available", sa.Boolean(), nullable=False),
        sa.Column("nearest_city", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("seller_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["seller_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_used_product_public_id"), "used_product", ["public_id"], unique=False
    )
    op.create_table(
        "used_product_picture",
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("current_timestamp"),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("image", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["used_product.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_used_product_picture_id"), "used_product_picture", ["id"], unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_used_product_picture_id"), table_name="used_product_picture")
    op.drop_table("used_product_picture")
    op.drop_index(op.f("ix_used_product_public_id"), table_name="used_product")
    op.drop_table("used_product")
    # ### end Alembic commands ###
