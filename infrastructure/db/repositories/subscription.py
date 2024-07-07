from datetime import datetime
from decimal import Decimal
from typing import cast

from sqlalchemy import Result, delete, exists, insert, select, update
from sqlalchemy.sql.functions import count

from core.repositories.subscription import ISubscriptionRepo
from core.schemas.user_product import UserProduct, UserProductAdd
from db import Database
from infrastructure.db.models.user_product import UserProductModel


class SubscriptionRepoImpl(ISubscriptionRepo):
    db_conn: Database

    async def get(self, user_id: int, product_id: int) -> UserProduct | None:
        async with await self.db_conn() as session:
            user_product_selection_res: Result = await session.execute(
                select(UserProductModel).where(
                    user_id == UserProductModel.UserID, product_id == UserProductModel.ProductID
                )
            )
            user_prd_mdl: UserProductModel | None = user_product_selection_res.scalar()
        return cast(UserProduct | None, UserProduct.model_validate(user_prd_mdl))

    async def exist(self, user_id: int, product_id: int) -> bool:
        async with await self.db_conn() as session:
            sub: Result = await session.execute(
                exists(UserProductModel.UserID)
                .where(user_id == UserProductModel.UserID, product_id == UserProductModel.ProductID)
                .select()
            )
            return cast(bool, sub.scalar())

    async def add(self, sub: UserProductAdd) -> UserProduct:
        async with await self.db_conn() as session:
            user_product_selection_res = await session.execute(
                insert(UserProductModel)
                .values(
                    UserID=sub.user_id,
                    ProductID=sub.product_id,
                    PriceThreshold=sub.price_threshold,
                    Added=datetime.utcnow(),
                )
                .returning(UserProductModel)
            )
            await session.commit()
        return cast(UserProduct, UserProduct.model_validate(user_product_selection_res.scalar()))

    async def delete(self, user_id: int, product_id: int) -> UserProduct:
        async with await self.db_conn() as session:
            deleted_sub_result: Result = await session.execute(
                delete(UserProductModel)
                .where(user_id == UserProductModel.UserID, product_id == UserProductModel.ProductID)
                .returning(UserProductModel)
            )
            await session.commit()
        return cast(UserProduct, UserProduct.model_validate(deleted_sub_result.scalar()))

    async def get_cnt_by_user(self, user_id: int) -> int:
        async with await self.db_conn() as session:
            product_cnt: Result = await session.execute(
                select(count())
                .select_from(UserProductModel)
                .where(user_id == UserProductModel.UserID)
            )
            await session.commit()

        return cast(int, product_cnt.scalar())

    async def update_threshold(
        self, user_id: int, product_id: int, threshold: Decimal | None = None
    ) -> UserProduct:
        async with await self.db_conn() as session:
            query_result: Result = await session.execute(
                update(UserProductModel)
                .where(user_id == UserProductModel.UserID, product_id == UserProductModel.ProductID)
                .values(PriceThreshold=threshold, Changed=datetime.utcnow())
                .returning(UserProductModel)
            )
            return cast(UserProduct, UserProduct.model_validate(query_result.scalar()))
