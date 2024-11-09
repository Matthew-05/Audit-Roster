"""Added user log

Revision ID: 73337e24d545
Revises: 3da89adb5de0
Create Date: 2024-10-18 14:12:40.524475

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '73337e24d545'
down_revision = '3da89adb5de0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('action', sa.String(length=10), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_log')
    # ### end Alembic commands ###
