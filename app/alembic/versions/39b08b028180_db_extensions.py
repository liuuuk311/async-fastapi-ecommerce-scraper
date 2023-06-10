"""db_extensions

Revision ID: 39b08b028180
Revises: 
Create Date: 2023-05-22 13:28:03.650581

"""
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '39b08b028180'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
    op.execute(text('CREATE EXTENSION IF NOT EXISTS pg_trgm;'))


def downgrade() -> None:
    op.execute(text('DROP EXTENSION IF EXISTS "uuid-ossp";'))
    op.execute(text('DROP EXTENSION IF EXISTS pg_trgm;'))
