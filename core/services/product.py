from dataclasses import dataclass
from typing import cast

from core.repositories.product import IProductRepo
from core.schemas.product import NewPrices, Product


@dataclass
class ProductService:
    product_repo: IProductRepo

    async def add_if_not_exists(self, product: Product) -> Product:
        created_product: Product | None = await self.product_repo.get(product.id)
        if not created_product:
            created_product = await self.product_repo.add(product)
        return cast(Product, created_product)

    async def update_prices(self, new_prices: NewPrices) -> list[Product]:
        return await self.product_repo.update_prices(new_prices)

    async def get_product(self, product_id: int) -> Product | None:
        return await self.product_repo.get(product_id)
