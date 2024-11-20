import re
from dataclasses import dataclass
from typing import cast

from core.repositories.product import IProductRepo
from core.schemas.product import Product
from core.value_objects.price_change import PriceChange
from utils.transform_types import get_int
from utils.types import ProductID

url_parse = re.compile(r'(http[s]?:\/\/)?([^\/\s]+\/)(catalog)\/(\d+)')  # product_id is 4 group


@dataclass
class ProductService:
    product_repo: IProductRepo

    async def add(self, product: Product) -> Product:
        created_product: Product | None = await self.product_repo.get(product.id)
        if not created_product:
            created_product = await self.product_repo.add(product)
        if created_product.price != product.price:
            updated_prod = await self.update_prices(
                {product.id: PriceChange(created_product.price, product.price)}
            )
            created_product = updated_prod[0]
        return cast(Product, created_product)

    async def update_prices(self, prices: dict[ProductID, PriceChange]) -> list[Product]:
        return await self.product_repo.update_prices(
            {pid: change.new for pid, change in prices.items()}
        )

    async def try_get_product(self, product_id: int) -> Product | None:
        return await self.product_repo.get(product_id)

    async def get_product(self, product_id: int) -> Product:
        product: Product | None = await self.product_repo.get(product_id)
        if product is None:
            raise ValueError(f'Нет товара с ид {product_id}!')
        return product

    @staticmethod
    def validate_product_id(product_string: str) -> int | None:
        """Returns product id from user message to bot"""

        #   message contain only product_id
        product_id: int | None = get_int(product_string)
        if product_id:
            return product_id

        # check product_id in url
        matching: re.Match | None = re.match(url_parse, product_string)
        if matching:
            product_id = matching.group(4)

        return get_int(product_id)
