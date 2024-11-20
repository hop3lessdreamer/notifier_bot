import datetime
import decimal
import pathlib
from aiogram import Bot
import pytest
from unittest.mock import MagicMock
from sqlalchemy import delete, insert

from core.schemas.product import Product
from core.schemas.user import User
from core.schemas.user_product import UserProduct, UserProductAdd
from core.tg.tg_dispatcher import TgDispatcher
from core.value_objects.price_change import PriceChange
from db import db
from infrastructure.db.models.product import ProductModel
from infrastructure.db.models.user import UserModel
from infrastructure.db.models.user_product import UserProductModel


@pytest.fixture
def users():
    yield [
        User(ID=1, ChatID=111111, TZOffset=-180),
        User(ID=2, ChatID=222222, TZOffset=0)
    ]

    with db.session() as session:
        session.execute(delete(UserModel).where(UserModel.ID == 1))
        session.execute(delete(UserModel).where(UserModel.ID == 2))
        session.commit()


@pytest.fixture
def products():
    relative_path_to_imgs = '../test_data/imgs/'
    cwd: pathlib.Path = pathlib.Path(__file__).parent

    with open(pathlib.Path(f'{cwd.absolute()}/{relative_path_to_imgs}1.png'), 'rb') as img:
        img_1: bytes = img.read()

    with open(pathlib.Path(f'{cwd.absolute()}/{relative_path_to_imgs}/2.png'), 'rb') as img:
        img_2: bytes = img.read()

    with open(pathlib.Path(f'{cwd.absolute()}/{relative_path_to_imgs}/3.png'), 'rb') as img:
        img_3: bytes = img.read()

    yield [
        Product(
            ID=101,
            Price=decimal.Decimal(1000),
            Img=img_1,
            Title='BIOREPAIR/Зубная щетка Gengive ультрамягкая для дёсен, бордовая'
        ),
        Product(
            ID=102,
            Price=decimal.Decimal(2000),
            Img=img_2,
            Title='BIOREPAIR/Зубная паста Fast Sensitive для чувствительных зубов, 75мл'
        ),
        Product(
            ID=103,
            Price=decimal.Decimal(3000),
            Img=img_3,
            Title='ArtofHome/Дозатор для жидкого мыла сенсорный диспенсер'
        ),
    ]

    with db.session() as session:
        session.execute(delete(ProductModel).where(ProductModel.ID == 101))
        session.execute(delete(ProductModel).where(ProductModel.ID == 102))
        session.execute(delete(ProductModel).where(ProductModel.ID == 103))
        session.commit()


@pytest.fixture
def _subs(users, products):
    user1: User = users[0]
    subs = [
        (
            UserProduct(
                UserID=user1.id,
                ProductID=products[0].id,
                PriceThreshold=decimal.Decimal(900),
                Added=datetime.datetime.now(),
                Changed=datetime.datetime.now()
            ),
            products[0],
            UserProductAdd(
                UserID=user1.id,
                ProductID=products[0].id,
                PriceThreshold=decimal.Decimal(900)
            )
        ),
        (
            UserProduct(
                UserID=user1.id,
                ProductID=products[1].id,
                PriceThreshold=decimal.Decimal(1900),
                Added=datetime.datetime.now(),
                Changed=datetime.datetime.now()
            ),
            products[1],
            UserProductAdd(
                UserID=user1.id,
                ProductID=products[1].id,
                PriceThreshold=decimal.Decimal(1900)
            )
        ),
        (
            UserProduct(
                UserID=user1.id,
                ProductID=products[2].id,
                PriceThreshold=decimal.Decimal(2900),
                Added=datetime.datetime.now(),
                Changed=datetime.datetime.now()
            ),
            products[2],
            UserProductAdd(
                UserID=user1.id,
                ProductID=products[2].id,
                PriceThreshold=decimal.Decimal(2900)
            )
        )
    ]
    yield subs


@pytest.fixture
def subs(users, _subs):
    user1: User = users[0]
    with db.session() as session:
        session.execute(insert(UserModel).values(ID=user1.id, ChatID=user1.chat_id, TZOffset=user1.tz_offset))
        session.commit()

    yield _subs


@pytest.fixture
def subs_w_existing_prods(products, subs):
    with db.session() as session:
        session.execute(insert(ProductModel)
                        .values(ID=products[0].id, Price=products[0].price, Img=products[0].img, Title=products[0].title))
        session.execute(insert(ProductModel)
                        .values(ID=products[1].id, Price=products[1].price, Img=products[1].img, Title=products[1].title))
        session.execute(insert(ProductModel)
                        .values(ID=products[2].id, Price=products[2].price, Img=products[2].img, Title=products[2].title))
        session.commit()

    yield subs


@pytest.fixture
def subs_already_added(subs_w_existing_prods):
    _sub1, _sub2, _sub3 = subs_w_existing_prods
    sub1, prod1, _ = _sub1
    sub2, prod2, _ = _sub2
    sub3, prod3, _ = _sub3

    with db.session() as session:
        session.execute(
            insert(UserProductModel)
            .values(
                UserID=sub1.user_id,
                ProductID=prod1.id,
                PriceThreshold=sub1.price_threshold,
                Added=datetime.datetime.utcnow()
            )
        )
        session.execute(
            insert(UserProductModel)
            .values(
                UserID=sub2.user_id,
                ProductID=prod2.id,
                PriceThreshold=sub2.price_threshold,
                Added=datetime.datetime.utcnow()
            )
        )
        session.execute(
            insert(UserProductModel)
            .values(
                UserID=sub3.user_id,
                ProductID=prod3.id,
                PriceThreshold=sub3.price_threshold,
                Added=datetime.datetime.utcnow()
            )
        )
        session.commit()

    yield subs_w_existing_prods


@pytest.fixture
def mock_tg_disp():
    return MagicMock(spec=TgDispatcher)


@pytest.fixture
def mock_bot():
    return MagicMock(spec=Bot)


@pytest.fixture
def mock_wb_service():
    return MagicMock(spec=Bot)


@pytest.fixture
def old_new_prods(products):
    old, new = {}, {}
    for p in products:
        old[p.id] = p
        new[p.id] = Product(ID=p.id, Price=p.price + decimal.Decimal(500), Img=p.img, Title=p.title)

    return old, new


@pytest.fixture
def changing_prods(products):
    return {
        p.id: PriceChange(old=p.price, new=p.price + decimal.Decimal(500))
        for p in products
    }


@pytest.fixture
def subs_already_added_by_pid(subs_already_added):
    return {item[0].product_id: item[0] for item in subs_already_added}
