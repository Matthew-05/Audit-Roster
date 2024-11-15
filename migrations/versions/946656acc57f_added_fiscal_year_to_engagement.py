"""Added fiscal year to engagement

Revision ID: 946656acc57f
Revises: c0776425cc0f
Create Date: 2024-10-11 15:35:29.460584

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = '946656acc57f'
down_revision = 'c0776425cc0f'
branch_labels = None
depends_on = None


def upgrade():
    # Create an Inspector
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    
    # Check if the column already exists
    columns = inspector.get_columns('engagement')
    if 'fiscal_year' not in [c['name'] for c in columns]:
        with op.batch_alter_table('engagement', schema=None) as batch_op:
            batch_op.add_column(sa.Column('fiscal_year', sa.String(length=10), nullable=True))
    else:
        print("Column 'fiscal_year' already exists in 'engagement' table. Skipping...")


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('engagement', schema=None) as batch_op:
        batch_op.drop_column('fiscal_year')

    # ### end Alembic commands ###
