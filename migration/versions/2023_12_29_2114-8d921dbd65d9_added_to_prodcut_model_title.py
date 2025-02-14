"""added to prodcut model title

Revision ID: 8d921dbd65d9
Revises: d5e4d34831da
Create Date: 2023-12-29 21:14:46.343702

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d921dbd65d9'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Product',
    sa.Column('ID', sa.BigInteger(), nullable=False),
    sa.Column('Price', sa.Numeric(), nullable=False),
    sa.Column('Img', sa.LargeBinary(), nullable=False),
    sa.Column('Title', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('ID')
    )
    op.create_table('User',
    sa.Column('ID', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('TZOffset', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('ID')
    )
    op.create_index(op.f('ix_User_ID'), 'User', ['ID'], unique=False)
    op.create_table('UserProduct',
    sa.Column('UserID', sa.BigInteger(), nullable=False),
    sa.Column('ProductID', sa.BigInteger(), nullable=False),
    sa.Column('PriceThreshold', sa.Numeric(), nullable=True),
    sa.Column('Added', sa.DateTime(), nullable=False),
    sa.Column('Changed', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['ProductID'], ['Product.ID'], ),
    sa.ForeignKeyConstraint(['UserID'], ['User.ID'], ),
    sa.PrimaryKeyConstraint('UserID', 'ProductID')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('UserProduct')
    op.drop_index(op.f('ix_User_ID'), table_name='User')
    op.drop_table('User')
    op.drop_table('Product')
    # ### end Alembic commands ###
