from dataclasses import dataclass
from typing import cast

from sqlalchemy import Function, Result, column, exists, insert, select, update

from core.repositories.product import IProductRepo
from core.schemas.product import NewPrices, Product
from db import Database
from infrastructure.db.models.product import ProductModel
from utils.transform_types import from_dict_to_json


@dataclass
class ProductRepoImpl(IProductRepo):
    db_conn: Database

    async def add(self, product: Product) -> Product:
        async with await self.db_conn() as session:
            user_result: Result = await session.execute(
                insert(ProductModel)
                .values(ID=product.id, Price=product.price, Img=product.img, Title=product.title)
                .returning(ProductModel)
            )
        await session.commit()
        return cast(Product, Product.model_validate(user_result.scalar()))

    async def get(self, product_id: int) -> Product | None:
        async with await self.db_conn() as session:
            product_selection_res: Result = await session.execute(
                select(ProductModel).where(product_id == ProductModel.ID)
            )
            product_mdl: ProductModel | None = product_selection_res.scalar()
            return cast(Product | None, Product.model_validate(product_mdl))

    async def exist(self, product_id: int) -> bool:
        async with await self.db_conn() as session:
            user: Result = await session.execute(
                exists(ProductModel.ID).where(product_id == ProductModel.ID).select()
            )
            return cast(bool, user.scalar())

    async def update_prices(self, new_prices: NewPrices) -> list[Product]:
        async with await self.db_conn() as session:
            subq_product_prices = (
                select(column('key'), column('value'))
                .select_from(Function('json_each', from_dict_to_json(new_prices)).alias('t'))  # type: ignore
                .subquery('product_prices')
            )
            res: Result = await session.execute(
                update(ProductModel)
                .where(subq_product_prices.c.key == ProductModel.ID)
                .values(Price=subq_product_prices.c.value)
                .returning(ProductModel)
            )
            await session.commit()
        return [Product.model_validate(result[0]) for result in res.all()]
