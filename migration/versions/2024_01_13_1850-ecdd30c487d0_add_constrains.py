"""add constrains

Revision ID: ecdd30c487d0
Revises: 8d921dbd65d9
Create Date: 2024-01-13 18:50:16.687063

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ecdd30c487d0'
down_revision: Union[str, None] = '8d921dbd65d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TRIGGER user_product_check_fkeys 
        BEFORE INSERT ON "UserProduct" 
        FOR EACH ROW 
        BEGIN
            SELECT RAISE(ABORT, 'Внешний ключ не существует в ссылочной таблице')
            WHERE 
                (SELECT COUNT(*) FROM "User" u WHERE u."ID" = NEW."UserID") = 0 
                or (SELECT COUNT(*) FROM "Product" p WHERE p."ID" = NEW."ProductID") = 0;
        END;
    """)
    # ### end Alembic commands ###


def downgrade() -> None:
    op.execute("""
        DROP TRIGGER user_product_check_fkeys;
    """)
    # ### end Alembic commands ###
