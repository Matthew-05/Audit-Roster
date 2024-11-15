"""Added toggle visibility field to observations

Revision ID: 5f07ce0654b9
Revises: 73337e24d545
Create Date: 2024-10-25 14:54:18.245890

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5f07ce0654b9'
down_revision = '73337e24d545'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('observation', schema=None) as batch_op:
        batch_op.add_column(sa.Column('hidden', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('observation', schema=None) as batch_op:
        batch_op.drop_column('hidden')

    # ### end Alembic commands ###
