from dataclasses import dataclass, field
from decimal import Decimal

import pytest
from datetime import datetime

from core.wb.wb_parser import WbProduct
from db.queries import Subscription
from schemas.product import Product
from schemas.user import User
from schemas.user_product import UserProduct
from utils.types import ProductID


@dataclass
class MockedBot:
    async def send_message(self, *args, **kwargs) -> None: ...


@dataclass
class MockerTGDispatcher:
    bot: MockedBot = field(default_factory=MockedBot)


class MockedDBQueries:
    async def get_all_subscriptions(self) -> list[Subscription]:
        return [
            Subscription(
                Product(
                    ID=1,
                    Price=Decimal(1000),
                    Img=b'',
                    Title='Товар1'
                ),
                UserProduct(
                    UserID=101,
                    ProductID=1,
                    PriceThreshold=Decimal(900),
                    Added=datetime(day=30, month=3, year=2024, hour=20, minute=0, second=0),
                    Changed=None
                )
            )
        ]

    async def change_products_prices(self, product_prices: dict[int, Decimal]) -> list[Product]:
        return [
            Product(
                ID=1,
                Price=Decimal(850),
                Img=b'',
                Title='Товар1'
            )
        ]

    async def get_user(self, user_id: int) -> User:
        return User(
            ID=user_id,
            ChatID=11,
            TZOffset=-180
        )

    async def delete_subscription(self, user_id: int, product_id: int) -> Subscription | None:
        return Subscription(
            Product(
                ID=product_id,
                Price=Decimal(1000),
                Img=b'',
                Title='Товар1'
            ),
            UserProduct(
                UserID=user_id,
                ProductID=product_id,
                PriceThreshold=Decimal(900),
                Added=datetime(day=30, month=3, year=2024, hour=20, minute=0, second=0),
                Changed=None
            )
        )


@pytest.fixture()
def mocked_wb_get_products(mocker) -> dict[ProductID, WbProduct]:
    wb_products = {
        1: WbProduct(
            id=1,
            title='Товар1',
            price=850
        )
    }
    return mocker.patch('core.wb.wb_parser.WbParser.get_wb_products', return_value=wb_products)


@pytest.fixture()
def mocked_get_all_subs(mocker) -> list[Subscription]:
    subs: list[Subscription] = [
        Subscription(
            Product(
                ID=1,
                Price=Decimal(1000),
                Img=b'',
                Title='Товар1'
            ),
            UserProduct(
                UserID=101,
                ProductID=1,
                PriceThreshold=Decimal(900),
                Added=datetime(day=30, month=3, year=2024, hour=20, minute=0, second=0),
                Changed=None
            )
        )
    ]
    return mocker.patch('db.queries.DBQueries.get_all_subscriptions', return_value=subs)


@pytest.fixture()
def mocked_change_products_prices(mocker):
    changed: dict[ProductID, Decimal] = {1: Decimal(850)}
    return mocker.patch('db.queries.DBQueries.change_products_prices', return_value=changed)
