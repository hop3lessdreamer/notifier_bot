from decimal import Decimal

import pytest

from core.wb.utils import check_product_prices
from schemas.product import Product
from tests.unit_tests.wb.conftest import MockedDBQueries, MockerTGDispatcher
from utils.types import UserID


@pytest.mark.asyncio
async def test_check_product_prices(mocked_wb_get_products, mocked_get_all_subs, mocked_change_products_prices):

    notifications: dict[UserID, list[Product]] = await check_product_prices(
        MockedDBQueries(),
        MockerTGDispatcher()
    )

    assert notifications.get(101) == [Product(ID=1, Price=Decimal(850), Img=b'', Title='Товар1')]
