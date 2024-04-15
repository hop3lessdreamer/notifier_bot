import pytest
from sqlalchemy import delete

from db import db
from core.wb.wb_parser import WbProduct
from db.models import ProductModel, UserModel, UserProductModel
from utils.types import ProductID


@pytest.fixture()
def mocked_wb_get_products(mocker) -> dict[ProductID, WbProduct]:
    wb_products = {
        101: WbProduct(
            id=101,
            title='Товар101',
            price=850
        )
    }
    return mocker.patch('core.wb.wb_parser.WbParser.get_wb_products', return_value=wb_products)


@pytest.fixture()
def clear_tables():
    yield
    with db.session() as session:
        session.execute(delete(ProductModel))
        session.execute(delete(UserModel))
        session.execute(delete(UserProductModel))
        session.commit()
