"""doing Intial migrations

Revision ID: 7ce669673adb
Revises: 
Create Date: 2022-09-09 18:25:02.577117

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7ce669673adb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('favourate_color', sa.String(length=150), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'favourate_color')
    # ### end Alembic commands ###
