"""feat: Added a one to one configuration to orm

Revision ID: 8c3f7ef1a5ac
Revises: df7f29a8b982
Create Date: 2024-03-28 12:28:09.009771

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '8c3f7ef1a5ac'
down_revision = 'df7f29a8b982'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_setting',
    sa.Column('id', sa.String(length=50), nullable=False),
    sa.Column('default_user_count', sa.Integer(), nullable=False),
    sa.Column('default_depth_count', sa.Integer(), nullable=False),
    sa.Column('theme', sa.String(length=10), nullable=False),
    sa.Column('user_id', sa.String(length=50), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('user_settings')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_setting_id', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('usage_id', sa.String(length=50), nullable=True))
        batch_op.create_foreign_key(None, 'user_setting', ['user_setting_id'], ['id'])
        batch_op.create_foreign_key(None, 'user_usage', ['usage_id'], ['id'])

    with op.batch_alter_table('user_usage', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.String(length=50), nullable=False))
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_usage', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('user_id')

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('usage_id')
        batch_op.drop_column('user_setting_id')

    op.create_table('user_settings',
    sa.Column('id', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('default_user_count', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('default_depth_count', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('theme', mysql.VARCHAR(length=10), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.drop_table('user_setting')
    # ### end Alembic commands ###
