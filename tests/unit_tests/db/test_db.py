import decimal
from datetime import datetime
from decimal import Decimal

import pytest

from sqlalchemy.sql.expression import select, insert

from db import db
from db.queries import DBQueries, UserModel, ProductModel, UserProductModel, SubscriptionsInfo, Subscription

from tests.unit_tests.db.conftest import users, products, user_products


class TestUsers:
    @pytest.mark.asyncio
    async def test_create_user_doesnt_exist(self, users):
        with db.session() as session:
            await DBQueries(db).create_user(
                user_id=users[0].id,
                chat_id=users[0].chat_id,
                tz_offset=users[0].tz_offset
            )

            created_user = session.execute(select(UserModel).where(UserModel.ID == users[0].id)).scalar()
            session.commit()

            assert created_user.ChatID == users[0].chat_id, 'for created user ChatID incorrect'
            assert created_user.TZOffset == users[0].tz_offset, 'for created user TZOffset incorrect'

    @pytest.mark.asyncio
    async def test_create_user_that_exist(self, users):
        with db.session() as session:
            session.execute(
                insert(UserModel)
                .values(ID=users[1].id, ChatID=users[1].chat_id, TZOffset=users[1].tz_offset)
            )
            session.commit()

            await DBQueries(db).create_user(
                user_id=users[1].id,
                chat_id=users[1].chat_id,
                tz_offset=users[1].tz_offset + 10
            )

            created_user = session.execute(select(UserModel).where(UserModel.ID == users[1].id)).scalar()
            session.commit()

            assert created_user.ChatID == users[1].chat_id, 'existing user has changed TZOffset'
            assert created_user.TZOffset == users[1].tz_offset, 'existing user has changed TZOffset'


class TestProducts:
    @pytest.mark.asyncio
    async def test_create_product_doesnt_exist(self, products):
        with db.session() as session:
            await DBQueries(db).create_product(
                products[0].id,
                products[0].price,
                products[0].img,
                products[0].title
            )

            created_product = session.execute(select(ProductModel).where(ProductModel.ID == products[0].id)).scalar()

            assert created_product.Price == products[0].price, 'incorrect product1 price!'
            assert created_product.Img is not None, 'incorrect product1 Img!'
            assert created_product.Title is not None, 'incorrect product1 Title!'

    @pytest.mark.asyncio
    async def test_create_product_that_exist_and_same_price(self, products):
        with db.session() as session:
            session.execute(insert(ProductModel).values(
                ID=products[1].id,
                Price=products[1].price,
                Img=products[1].img,
                Title=products[1].title
            ))
            session.commit()

            created_product = await DBQueries(db).create_product(
                products[1].id,
                products[1].price,
                b'',
                ''
            )

            assert created_product.price == products[1].price, 'incorrect product1 price!'
            assert created_product.img == products[1].img, 'incorrect product1 Img!'
            assert created_product.title == products[1].title, 'incorrect product1 Title!'

    @pytest.mark.asyncio
    async def test_create_product_that_exist_and_not_same_price(self, products):
        with db.session() as session:
            session.execute(insert(ProductModel).values(
                ID=products[2].id,
                Price=products[2].price,
                Img=products[2].img,
                Title=products[2].title
            ))
            session.commit()

            created_product = await DBQueries(db).create_product(
                products[2].id,
                products[2].price + 100,
                b'',
                ''
            )

            assert created_product.price == products[2].price + 100, 'created_product incorrect price!'
            assert created_product.img == products[2].img, 'created_product incorrect Img!'
            assert created_product.title == products[2].title, 'created_product incorrect Title!'


class TestUserProducts:
    @pytest.mark.asyncio
    @pytest.mark.parametrize('user_products', [pytest.param(False, id='w/o_db_write')], indirect=True)
    async def test_add_subscription(self, user_products):
        with db.session() as session:
            user_product, product = user_products[0]
            session.execute(insert(UserModel).values(ID=user_product.user_id, ChatID=111111, TZOffset=0))
            session.execute(insert(ProductModel)
                            .values(ID=product.id, Price=product.price, Img=product.img, Title=product.title))

            session.commit()

            added_sub = await DBQueries(db).add_subscription(
                user_id=user_product.user_id,
                product=product,
                threshold=user_product.price_threshold
            )

            assert added_sub.price_threshold == decimal.Decimal(900), 'incorrect user_products count in db!'

    @pytest.mark.parametrize('user_products', [pytest.param(False, id='with_db_write')], indirect=True)
    @pytest.mark.asyncio
    async def test_delete_subscription_that_exist(self, user_products):
        with db.session() as session:
            user_product, product = user_products[1]
            session.execute(insert(UserModel).values(ID=user_product.user_id, ChatID=111111, TZOffset=0))
            session.execute(insert(ProductModel)
                            .values(ID=product.id, Price=product.price, Img=product.img, Title=product.title))
            session.execute(
                insert(UserProductModel)
                .values(
                    UserID=user_product.user_id,
                    ProductID=product.id,
                    PriceThreshold=user_product.price_threshold,
                    Added=datetime.utcnow()
                )
            )
            session.commit()

            deleted_sub = await DBQueries(db).delete_subscription(user_id=user_product.user_id, product_id=product.id)

            assert deleted_sub.user_product.user_id == user_product.user_id
            assert deleted_sub.user_product.product_id == user_product.product_id

    @pytest.mark.asyncio
    @pytest.mark.parametrize('user_products', [pytest.param(True, id='with_db_write')], indirect=['user_products'])
    async def test_change_subscription_threshold(self, user_products):
        user_product, product = user_products[1]
        sub = await DBQueries(db).change_subscription_threshold(
            user_product.user_id, user_product.product_id, decimal.Decimal(1999)
        )

        assert sub.user_product.price_threshold == decimal.Decimal(1999)

    @pytest.mark.asyncio
    @pytest.mark.parametrize('user_products', [pytest.param(True, id='with_db_write')], indirect=['user_products'])
    async def test_get_cnt_subscription_by_user(self, user_products):
        user_product, product = user_products[0]
        cnt = await DBQueries(db).get_cnt_subscription_by_user(user_id=user_product.user_id)

        assert cnt == 3, 'incorrect subs cnt by user'

    @pytest.mark.asyncio
    @pytest.mark.parametrize('user_products', [pytest.param(True, id='with_db_write')], indirect=['user_products'])
    async def test_get_subscriptions_by_user(self, user_products):
        user_product, product = user_products[0]
        subs_info: SubscriptionsInfo = await DBQueries(db).get_subscriptions_by_user(
            user_id=user_product.user_id,
            limit=5,
            offset=0
        )

        assert subs_info.subs_cnt_by_user == 3
        assert subs_info.first_sub.user_product.user_id == 1
        assert subs_info.first_sub.user_product.product_id == 103
        assert subs_info.first_sub.user_product.price_threshold == Decimal(2900)

    @pytest.mark.asyncio
    async def test_get_subscription_by_user_n_product(self):
        with db.session() as session:
            #   TODO
            pass

    @pytest.mark.asyncio
    @pytest.mark.parametrize('user_products', [pytest.param(True, id='with_db_write')], indirect=['user_products'])
    async def test_get_all_subscriptions(self, user_products):
        subs: list[Subscription] = await DBQueries(db).get_all_subscriptions()

        first_sub: Subscription = subs[0]

        assert len(subs) == 3
        assert first_sub.user_product.user_id == 1
        assert first_sub.user_product.product_id == 103
        assert first_sub.product.price == Decimal(3000)
