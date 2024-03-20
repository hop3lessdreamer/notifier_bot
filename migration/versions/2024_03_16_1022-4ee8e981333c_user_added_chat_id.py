"""user added chat_id

Revision ID: 4ee8e981333c
Revises: ecdd30c487d0
Create Date: 2024-03-16 10:22:18.428621

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ee8e981333c'
down_revision: Union[str, None] = 'ecdd30c487d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('User', sa.Column('ChatID', sa.BigInteger(), nullable=False))


def downgrade() -> None:
    op.drop_column('User', 'ChatID')
