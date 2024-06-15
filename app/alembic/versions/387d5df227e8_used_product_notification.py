"""used product notification

Revision ID: 387d5df227e8
Revises: c4252f788219
Create Date: 2024-06-14 09:47:01.463737

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '387d5df227e8'
down_revision = 'c4252f788219'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('used_product', sa.Column('mark_as_sold_notification_sent_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('used_product', 'mark_as_sold_notification_sent_at')
    # ### end Alembic commands ###
