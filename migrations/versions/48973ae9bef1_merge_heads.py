"""merge heads

Revision ID: 48973ae9bef1
Revises: 5c6a333de7dc, b526391632f3, ef67e8691671
Create Date: 2024-06-27 10:03:46.205044

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '48973ae9bef1'
down_revision = ('5c6a333de7dc', 'b526391632f3', 'ef67e8691671')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
