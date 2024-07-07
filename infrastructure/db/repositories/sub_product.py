from sqlalchemy import Result, Row, desc, select

from core.repositories.sub_product import ISubProductRepo
from core.schemas.product import Product
from core.schemas.sub_product import SubProduct
from core.schemas.user_product import UserProduct
from db import Database
from infrastructure.db.models.product import ProductModel
from infrastructure.db.models.user_product import UserProductModel


class SubProductRepoImpl(ISubProductRepo):
    db_conn: Database

    async def get_by_user(self, user_id: int, limit: int, offset: int) -> list[SubProduct]:
        async with await self.db_conn() as session:
            selection_res: Result = await session.execute(
                select(UserProductModel, ProductModel)
                .join(ProductModel.users)
                .where(user_id == UserProductModel.UserID)
                .order_by(desc(UserProductModel.Added))
                .limit(limit)
                .offset(offset)
            )
            await session.commit()

        return [
            SubProduct(
                UserProduct.model_validate(user_prod_mdl[0]),
                Product.model_validate(user_prod_mdl[1]),
            )
            for user_prod_mdl in selection_res.all()
        ]

    async def get_by_user_product(self, user_id: int, product_id: int) -> SubProduct | None:
        async with await self.db_conn() as session:
            query_result: Result = await session.execute(
                select(UserProductModel, ProductModel)
                .join(ProductModel.users)
                .where(user_id == UserProductModel.UserID, product_id == UserProductModel.ProductID)
            )
            result_row: Row = query_result.first()
            await session.commit()
            if not result_row:
                return None

        return SubProduct(
            UserProduct.model_validate(result_row[0]), Product.model_validate(result_row[1])
        )

    async def get_all(self) -> list[SubProduct]:
        async with await self.db_conn() as session:
            query_result = await session.execute(
                select(UserProductModel, ProductModel)
                .join(ProductModel.users)
                .order_by(desc(UserProductModel.Added))
            )
            await session.commit()
        return [
            SubProduct(UserProduct.model_validate(result[0]), Product.model_validate(result[1]))
            for result in query_result.all()
        ]
