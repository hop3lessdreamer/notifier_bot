from abc import abstractmethod
from decimal import Decimal

from core.schemas.user_product import UserProduct, UserProductAdd


class ISubscriptionRepo:
    @abstractmethod
    async def get(self, user_id: int, product_id: int) -> UserProduct | None:
        ...

    @abstractmethod
    async def exist(self, user_id: int, product_id: int) -> bool:
        ...

    @abstractmethod
    async def add(self, sub: UserProductAdd) -> UserProduct:
        ...

    @abstractmethod
    async def delete(self, user_id: int, product_id: int) -> UserProduct:
        ...

    @abstractmethod
    async def get_cnt_by_user(self, user_id: int) -> int:
        ...

    @abstractmethod
    async def update_threshold(
        self, user_id: int, product_id: int, threshold: Decimal | None = None
    ) -> UserProduct:
        ...
