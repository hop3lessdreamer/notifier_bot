import pytest
from sqlalchemy import delete

from config import test_config
from db import db
from core.schemas.product import WbProduct
from infrastructure.db.models import ProductModel, UserModel, UserProductModel, Base
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


@pytest.fixture(scope='function', autouse=True)
def clear_tables():
    yield
    with db.session() as session:
        #   at first del UserProduct cause table has refs to Product and User
        session.execute(delete(UserProductModel))
        session.execute(delete(ProductModel))
        session.execute(delete(UserModel))
        session.commit()


@pytest.fixture(scope='session', autouse=True)
def setup_db():
    assert test_config.MODE == 'TEST', 'using a non-test environment!'

    # db.drop_db(Base)
    # db.init_db(Base)
    # yield
    # db.drop_db(Base)
