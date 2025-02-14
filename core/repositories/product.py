from abc import abstractmethod
from decimal import Decimal

from core.schemas.product import Product
from utils.types import ProductID


class IProductRepo:
    @abstractmethod
    async def add(self, product: Product) -> Product:
        ...

    @abstractmethod
    async def get(self, product_id: int) -> Product | None:
        ...

    @abstractmethod
    async def exist(self, product_id: int) -> bool:
        ...

    @abstractmethod
    async def update_prices(self, new_prices: dict[ProductID, Decimal]) -> list[Product]:
        ...
