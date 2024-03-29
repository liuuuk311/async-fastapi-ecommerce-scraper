"""price history

Revision ID: 393a17639193
Revises: b6ef8486e950
Create Date: 2023-10-06 18:22:11.261433

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = '393a17639193'
down_revision = 'b6ef8486e950'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'price_history',
        sa.Column(
            'created_at',
            sa.DateTime(),
            server_default=sa.text('current_timestamp'),
            nullable=False,
        ),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('price', sa.Numeric(precision=7, scale=2), nullable=False),
        sa.ForeignKeyConstraint(
            ['product_id'],
            ['product.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_price_history_product_id'),
        'price_history',
        ['product_id'],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_price_history_product_id'), table_name='price_history')
    op.drop_table('price_history')
    # ### end Alembic commands ###
