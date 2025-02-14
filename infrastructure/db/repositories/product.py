from dataclasses import dataclass
from decimal import Decimal
from typing import cast

from sqlalchemy import Result, exists, insert, select, text

from core.repositories.product import IProductRepo
from core.schemas.product import Product
from db import Database
from infrastructure.db.models.product import ProductModel
from utils.transform_types import from_dict_to_json
from utils.types import ProductID


@dataclass
class ProductRepoImpl(IProductRepo):
    db_conn: Database

    async def add(self, product: Product) -> Product:
        async with await self.db_conn() as session:
            prod_result: Result = await session.execute(
                insert(ProductModel)
                .values(
                    ID=product.id,
                    Price=product.price,
                    Img=product.img,
                    Title=product.title,
                    MPType=product.mp_type,
                )
                .returning(ProductModel)
            )
            await session.commit()
        return cast(Product, Product.model_validate(prod_result.scalar()))

    async def get(self, product_id: int) -> Product | None:
        async with await self.db_conn() as session:
            product_selection_res: Result = await session.execute(
                select(ProductModel).where(product_id == ProductModel.ID)
            )
            product_mdl: ProductModel | None = product_selection_res.scalar()
            return Product.model_validate(product_mdl) if product_mdl else None

    async def exist(self, product_id: int) -> bool:
        async with await self.db_conn() as session:
            user: Result = await session.execute(
                exists(ProductModel.ID).where(product_id == ProductModel.ID).select()
            )
            return cast(bool, user.scalar())

    async def update_prices(self, new_prices: dict[ProductID, Decimal]) -> list[Product]:
        async with await self.db_conn() as session:
            res: Result = await session.execute(
                text(
                    """
                    update "Product"
                    set "Price" = je.value::numeric
                    from jsonb_each_text((:prices)::jsonb) je
                    where je.key::int = "ID"
                    returning "Product".*;
                """
                ),
                {'prices': from_dict_to_json(new_prices)},
            )
            await session.commit()
        return [Product.model_validate(result) for result in res.all()]
