"""Add named constraint to Engagement-Partner relationship

Revision ID: c0776425cc0f
Revises: 
Create Date: 2024-09-30 15:32:36.893132

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c0776425cc0f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # First, handle the partner_id column
    with op.batch_alter_table('engagement', schema=None) as batch_op:
        batch_op.alter_column('partner_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # Then, handle the deadline column
    with op.batch_alter_table('engagement', schema=None) as batch_op:
        batch_op.alter_column('deadline',
               existing_type=sa.DATE(),
               nullable=True)

    # Finally, add the foreign key constraint
    with op.batch_alter_table('engagement', schema=None) as batch_op:
        batch_op.create_foreign_key('fk_engagement_partner', 'partner', ['partner_id'], ['id'])


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('engagement', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('deadline')
        batch_op.drop_column('partner_id')

    # ### end Alembic commands ###