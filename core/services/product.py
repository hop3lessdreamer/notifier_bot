import re
from dataclasses import dataclass
from typing import cast

from core.repositories.product import IProductRepo
from core.schemas.product import MPType, Product
from core.services.ozon import OzonService
from core.services.wb import WbService
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

    async def try_get_product(self, product_id: ProductID) -> Product | None:
        return await self.product_repo.get(product_id)

    async def get_product(self, product_id: ProductID) -> Product:
        product: Product | None = await self.product_repo.get(product_id)
        if product is None:
            raise ValueError(f'Нет товара с ид {product_id}!')
        return product

    @staticmethod
    def validate_product_id(product_string: str) -> tuple[ProductID | None, MPType | None]:
        """Returns product id from user message to bot"""

        prod_id, prod_type = ProductService._define_prod_type(product_string)
        #   Если не удалось определить тип по сообщению, то вероятно пользователь ввел артикул
        if prod_id:
            return prod_id, prod_type

        #   message contains only product_id
        prod_id = get_int(product_string)
        if prod_id:
            return prod_id, None

        return None, None

    @staticmethod
    def form_url_by_product(product: Product) -> str:
        if product.mp_type == MPType.WB:
            return WbService.form_url_by_product_id(product_id=product.id)
        elif product.mp_type == MPType.OZON:
            return OzonService.form_url_by_product_id(product_id=product.id)

    @staticmethod
    def _define_prod_type(product_string: str) -> tuple[ProductID | None, MPType | None]:
        if prod_id := WbService.try_validate_product_url(product_string):
            return prod_id, MPType.WB
        elif prod_id := OzonService.try_validate_product_url(product_string):
            return prod_id, MPType.OZON
        return None, None
