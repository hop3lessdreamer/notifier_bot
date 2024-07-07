from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from functools import cached_property
from typing import cast

from sqlalchemy import Result, Row, column, desc
from sqlalchemy.sql.expression import Function, delete, exists, insert, select, update
from sqlalchemy.sql.functions import count

from constants import MOSCOW_TZ_OFFSET
from core.schemas.product import Product
from core.schemas.user import User
from core.schemas.user_product import UserProduct
from core.wb.wb_parser import WbProduct
from db import Database
from infrastructure.db.models.product import ProductModel
from infrastructure.db.models.user import UserModel
from infrastructure.db.models.user_product import UserProductModel
from utils.transform_types import from_dict_to_json


@dataclass
class Subscription:
    product: Product
    user_product: UserProduct

    @cached_property
    def empty(self) -> bool:
        return not (self.product and self.user_product)

    def __repr__(self) -> str:
        repr: str = ''
        if self.product:
            repr += (
                f'Product('
                f'ID={self.product.id},'
                f' Price={self.product.price},'
                f' Title={self.product.title}'
                ')\n'
            )
        if self.user_product:
            repr += (
                f'UserProduct('
                f'UserID={self.user_product.user_id},'
                f' PriceThreshold={self.user_product.price_threshold}'
                f')\n'
            )
        return repr


@dataclass
class SubscriptionsInfo:
    subscriptions: list[Subscription] = field(default_factory=list)
    subs_cnt_by_user: int = 0
    current_position: int = 0

    @cached_property
    def empty(self) -> bool:
        return not self.subscriptions

    @cached_property
    def subs_length(self) -> int:
        return len(self.subscriptions)

    @cached_property
    def first_sub(self) -> Subscription | None:
        if self.empty:
            return None
        return self.subscriptions[0]

    @cached_property
    def sub_by_cur_pos(self) -> Subscription | None:
        if self.empty:
            return None
        try:
            return self.subscriptions[self.current_position]
        except KeyError:
            return None

    @cached_property
    def wb_prod_from_sub_by_cur_pos(self) -> WbProduct:
        if not self.sub_by_cur_pos or not self.sub_by_cur_pos.product:
            return WbProduct()
        return WbProduct(
            self.sub_by_cur_pos.product.id,
            self.sub_by_cur_pos.product.title,
            float(self.sub_by_cur_pos.product.price),
        )

    def __pos__(self) -> None:
        self.current_position += 1

    def __repr__(self) -> str:
        subs_repr: str = '\n'.join(
            [f'pos = {str(i)} >> {sub.__repr__()}' for i, sub in enumerate(self.subscriptions)]
        )
        return f'SubscriptionInfo:\n' f'cur_pos = {self.current_position}\n' f'subs:\n{subs_repr}\n'

    def del_sub_by_cur_pos(self) -> Subscription:
        deleted_sub: Subscription = self.subscriptions.pop(self.current_position)
        self.subs_cnt_by_user -= 1
        self.clear_cache()

        return deleted_sub

    def go_to_prev_pos(self) -> None:
        #   beginning?
        if self.current_position == 0:
            if self.subs_length < self.subs_cnt_by_user:
                #   TODO: Подгрузим еще данные, если будет доступна зацикленная навигация
                pass
            else:
                self.current_position = self.subs_length - 1
        else:
            self.current_position -= 1

        self.clear_cache()

    async def go_to_next_pos(self, user_id: int, db_connection: 'DBQueries') -> None:
        #   beginning?
        if self.current_position == (self.subs_length - 1):
            if self.subs_length < self.subs_cnt_by_user:
                read_subs: SubscriptionsInfo = await db_connection.get_subscriptions_by_user(
                    user_id=user_id, offset=self.subs_length
                )
                self.subscriptions.extend(read_subs.subscriptions)
                self.current_position += 1
            #   fix position to beginning
            else:
                self.current_position = 0
        else:
            self.current_position += 1

        self.clear_cache()

    def clear_cache(self) -> None:
        self.__dict__.pop('empty', None)
        self.__dict__.pop('subs_length', None)
        self.__dict__.pop('first_sub', None)
        self.__dict__.pop('sub_by_cur_pos', None)
        self.__dict__.pop('wb_prod_from_sub_by_cur_pos', None)


class DBQueries:
    __slots__ = ('db',)

    SUBS_READING_LIMIT_PER_QUERY: int = 5

    def __init__(self, db: Database) -> None:
        self.db: Database = db

    async def create_user(
        self, user_id: int, chat_id: int, tz_offset: int = MOSCOW_TZ_OFFSET
    ) -> User:
        async with await self.db() as session:
            user: Result = await session.execute(select(UserModel).where(user_id == UserModel.ID))
            user_mdl: UserModel = user.scalar()
            if not user_mdl:
                user_result: Result = await session.execute(
                    insert(UserModel)
                    .values(ID=user_id, ChatID=chat_id, TZOffset=tz_offset)
                    .returning(UserModel)
                )
                await session.commit()
                return cast(User, User.model_validate(user_result.scalar()))
            await session.commit()
        return cast(User, User.model_validate(user_mdl))

    async def get_user(self, user_id: int) -> User:
        async with await self.db() as session:
            user: Result = await session.execute(select(UserModel).where(user_id == UserModel.ID))
            user_mdl: UserModel = user.scalar()
            await session.commit()
        return cast(User, User.model_validate(user_mdl))

    async def create_product(
        self, product_id: int, price: Decimal, img: bytes, title: str
    ) -> Product:
        async with await self.db() as session:
            product_selection_res: Result = await session.execute(
                select(ProductModel).where(product_id == ProductModel.ID)
            )
            product_mdl: ProductModel | None = product_selection_res.scalar()
            if not product_mdl:
                product_selection_res = await session.execute(
                    insert(ProductModel)
                    .values(ID=product_id, Price=price, Img=img, Title=title)
                    .returning(ProductModel)
                )
                await session.commit()
                return cast(Product, Product.model_validate(product_selection_res.scalar()))

            product: Product = Product.model_validate(product_mdl)
            if product.price != price:
                product_selection_res = await session.execute(
                    update(ProductModel)
                    .where(
                        product_id == ProductModel.ID,
                    )
                    .values(Price=price)
                    .returning(ProductModel)
                )
                await session.commit()
                return cast(Product, Product.model_validate(product_selection_res.scalar()))

            await session.commit()
        return product

    async def add_subscription(
        self, user_id: int, product: Product, threshold: Decimal | None = None
    ) -> UserProduct:
        async with await self.db() as session:
            product_exist: Result = await session.execute(
                exists(ProductModel.ID)
                .where(product.id == ProductModel.ID, product.price == ProductModel.Price)
                .select()
            )
            if not product_exist.scalar():
                await self.create_product(product.id, product.price, product.img, product.title)

            user_product_selection_res: Result = await session.execute(
                select(UserProductModel).where(
                    user_id == UserProductModel.UserID, product.id == UserProductModel.ProductID
                )
            )
            user_prd_mdl: UserProductModel | None = user_product_selection_res.scalar()
            if not user_prd_mdl:
                user_product_selection_res = await session.execute(
                    insert(UserProductModel)
                    .values(
                        UserID=user_id,
                        ProductID=product.id,
                        PriceThreshold=threshold,
                        Added=datetime.utcnow(),
                    )
                    .returning(UserProductModel)
                )
                await session.commit()
                return cast(
                    UserProduct, UserProduct.model_validate(user_product_selection_res.scalar())
                )

            await session.commit()
        return cast(UserProduct, UserProduct.model_validate(user_prd_mdl))

    async def delete_subscription(self, user_id: int, product_id: int) -> Subscription | None:
        async with await self.db() as session:
            sub_exist_res: Result = await session.execute(
                select(UserProductModel).where(
                    user_id == UserProductModel.UserID, product_id == UserProductModel.ProductID
                )
            )
            sub_exist: UserProductModel | None = sub_exist_res.scalar()
            if not sub_exist:
                await session.commit()
                return None

            deleted_sub_result: Result = await session.execute(
                delete(UserProductModel)
                .where(user_id == UserProductModel.UserID, product_id == UserProductModel.ProductID)
                .returning(UserProductModel)
            )
            deleted_sub: UserProduct = UserProduct.model_validate(deleted_sub_result.scalar())
            product_res: Result = await session.execute(
                select(ProductModel).where(deleted_sub.product_id == ProductModel.ID)
            )
            product_from_del_sub = Product.model_validate(product_res.scalar())
            await session.commit()

        return Subscription(product_from_del_sub, deleted_sub)

    async def change_subscription_threshold(
        self, user_id: int, product_id: int, threshold: Decimal | None = None
    ) -> Subscription:
        async with await self.db() as session:
            query_result: Result = await session.execute(
                update(UserProductModel)
                .where(user_id == UserProductModel.UserID, product_id == UserProductModel.ProductID)
                .values(PriceThreshold=threshold, Changed=datetime.utcnow())
                .returning(UserProductModel)
            )
            user_product: UserProduct = UserProduct.model_validate(query_result.scalar())

            product_res: Result = await session.execute(
                select(ProductModel).where(user_product.product_id == ProductModel.ID)
            )
            await session.commit()
        return Subscription(Product.model_validate(product_res.scalar()), user_product)

    async def get_cnt_subscription_by_user(self, user_id: int) -> int:
        async with await self.db() as session:
            product_cnt: Result = await session.execute(
                select(count())
                .select_from(UserProductModel)
                .where(user_id == UserProductModel.UserID)
            )
            await session.commit()

        return cast(int, product_cnt.scalar())

    async def get_subscriptions_by_user(
        self, user_id: int, limit: int = SUBS_READING_LIMIT_PER_QUERY, offset: int = 0
    ) -> SubscriptionsInfo:
        async with await self.db() as session:
            product_cnt: int = await self.get_cnt_subscription_by_user(user_id)

            selection_res: Result = await session.execute(
                select(UserProductModel, ProductModel)
                .join(ProductModel.users)
                .where(user_id == UserProductModel.UserID)
                .order_by(desc(UserProductModel.Added))
                .limit(limit)
                .offset(offset)
            )
            await session.commit()
        return SubscriptionsInfo(
            [
                Subscription(
                    Product.model_validate(user_prod_mdl[1]),
                    UserProduct.model_validate(user_prod_mdl[0]),
                )
                for user_prod_mdl in selection_res.all()
            ],
            product_cnt,
        )

    async def get_subscription_by_user_n_product(
        self, user_id: int, product_id: int
    ) -> Subscription | None:
        async with await self.db() as session:
            query_result: Result = await session.execute(
                select(ProductModel, UserProductModel)
                .join(ProductModel.users)
                .where(user_id == UserProductModel.UserID, product_id == UserProductModel.ProductID)
            )
            result_row: Row = query_result.first()
            await session.commit()
            if not result_row:
                return None

        return Subscription(
            product=Product.model_validate(result_row[0]),
            user_product=UserProduct.model_validate(result_row[1]),
        )

    async def get_all_subscriptions(self) -> list[Subscription]:
        async with await self.db() as session:
            query_result = await session.execute(
                select(ProductModel, UserProductModel)
                .join(ProductModel.users)
                .order_by(desc(UserProductModel.Added))
            )
            await session.commit()
        return [
            Subscription(Product.model_validate(result[0]), UserProduct.model_validate(result[1]))
            for result in query_result.all()
        ]

    async def change_products_prices(self, product_prices: dict[int, Decimal]) -> list[Product]:
        async with await self.db() as session:
            subq_product_prices = (
                select(column('key'), column('value'))
                .select_from(Function('json_each', from_dict_to_json(product_prices)).alias('t'))
                .subquery('product_prices')
            )
            res = await session.execute(
                update(ProductModel)
                .where(subq_product_prices.c.key == ProductModel.ID)
                .values(Price=subq_product_prices.c.value)
                .returning(ProductModel)
            )
            await session.commit()
        return [Product.model_validate(result[0]) for result in res.all()]
