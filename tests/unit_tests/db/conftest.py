import datetime
import decimal
import pathlib

import pytest
from sqlalchemy import delete, insert

from db import db
from infrastructure.db.models.user import UserModel
from infrastructure.db.models import ProductModel
from infrastructure.db.models.user_product import UserProductModel
from core.schemas.product import Product
from core.schemas.user import User
from core.schemas.user_product import UserProduct


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
    relative_path_to_imgs = '../../test_data/imgs/'
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
def user_products(request):
    user = User(ID=1, ChatID=111111, TZOffset=-180)
    data_set = [
        (
            UserProduct(
                UserID=1,
                ProductID=101,
                PriceThreshold=decimal.Decimal(900),
                Added=datetime.datetime.now(),
                Changed=datetime.datetime.now()
            ),
            Product(
                ID=101,
                Price=decimal.Decimal(1000),
                Img=b'',
                Title=''
            )
        ),
        (
            UserProduct(
                UserID=1,
                ProductID=102,
                PriceThreshold=decimal.Decimal(1900),
                Added=datetime.datetime.now(),
                Changed=datetime.datetime.now()
            ),
            Product(
                ID=102,
                Price=decimal.Decimal(2000),
                Img=b'',
                Title=''
            )
        ),
        (
            UserProduct(
                UserID=1,
                ProductID=103,
                PriceThreshold=decimal.Decimal(2900),
                Added=datetime.datetime.now(),
                Changed=datetime.datetime.now()
            ),
            Product(
                ID=103,
                Price=decimal.Decimal(3000),
                Img=b'',
                Title=''
            )
        )
    ]
    if request.param:
        with db.session() as session:
            session.execute(insert(UserModel).values(ID=user.id, ChatID=user.chat_id, TZOffset=user.tz_offset))
            session.commit()
            for user_product, product in data_set:
                session.execute(insert(ProductModel)
                                .values(ID=product.id, Price=product.price, Img=product.img, Title=product.title))
                session.execute(
                    insert(UserProductModel).values(
                        UserID=user_product.user_id,
                        ProductID=user_product.product_id,
                        PriceThreshold=user_product.price_threshold,
                        Added=datetime.datetime.utcnow()
                    ))
            session.commit()

    yield data_set

    with db.session() as session:
        session.execute(delete(UserModel).where(UserModel.ID == 1))

        session.execute(delete(ProductModel).where(ProductModel.ID == 101))
        session.execute(delete(ProductModel).where(ProductModel.ID == 102))
        session.execute(delete(ProductModel).where(ProductModel.ID == 103))

        session.execute(delete(UserProductModel)
                        .where(UserProductModel.UserID == 1, UserProductModel.ProductID == 101))
        session.execute(delete(UserProductModel)
                        .where(UserProductModel.UserID == 1, UserProductModel.ProductID == 102))
        session.execute(delete(UserProductModel)
                        .where(UserProductModel.UserID == 1, UserProductModel.ProductID == 103))
        session.commit()
