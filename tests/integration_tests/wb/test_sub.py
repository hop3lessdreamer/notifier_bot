from decimal import Decimal

import pytest
from sqlalchemy import insert, select, delete

from core.wb.utils import check_product_prices
from db import db
from db.models import ProductModel, UserModel
from db.queries import DBQueries, User, Product, UserProduct, SubscriptionsInfo
from tests.unit_tests.wb.conftest import MockerTGDispatcher
from utils.types import UserID


@pytest.mark.asyncio
async def test_sub_discounting_below_threshold(mocked_wb_get_products, clear_tables):
    queries = DBQueries(db)
    created_user: User = await queries.create_user(user_id=1, chat_id=1, tz_offset=-180)
    sub: UserProduct = await queries.add_subscription(
        created_user.id,
        product=Product(ID=101, Price=Decimal(1000), Img=b'', Title='Товар101'),
        threshold=Decimal(900)
    )

    notifications: dict[UserID, list[Product]] = await check_product_prices(queries, MockerTGDispatcher())

    user_subs: SubscriptionsInfo = await queries.get_subscriptions_by_user(user_id=1)

    with db.session() as session:
        product_price = session.execute(select(ProductModel).where(ProductModel.ID == 101)).scalar().Price
        session.commit()

    assert notifications.get(created_user.id) == [Product(ID=101, Price=Decimal(850), Img=b'', Title='Товар101')]
    assert user_subs.empty is True
    #   Check changing product price
    assert product_price == 850
