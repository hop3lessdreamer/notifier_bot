from abc import abstractmethod

from core.schemas.user import User


class IUserRepo:
    @abstractmethod
    async def add(self, user: User) -> User:
        ...

    @abstractmethod
    async def get(self, user_id: int) -> User | None:
        ...

    @abstractmethod
    async def exist(self, user_id: int) -> bool:
        ...
