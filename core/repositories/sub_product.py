from abc import abstractmethod

from core.schemas.sub_product import SubProduct


class ISubProductRepo:
    @abstractmethod
    async def get_by_user(self, user_id: int, limit: int, offset: int) -> list[SubProduct]:
        ...

    @abstractmethod
    async def get_by_user_product(self, user_id: int, product_id: int) -> SubProduct | None:
        ...

    @abstractmethod
    async def get_all(self) -> list[SubProduct]:
        ...
