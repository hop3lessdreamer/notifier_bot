from dataclasses import dataclass
from typing import cast

from core.repositories.user import IUserRepo
from core.schemas.user import User


@dataclass
class UserService:
    user_repo: IUserRepo

    async def create_user(self, user: User) -> User:
        created_user: User | None = await self.user_repo.get(user.id)
        if not created_user:
            created_user = await self.user_repo.add(user)

        return cast(User, created_user)

    async def get_user(self, user_id: int) -> User | None:
        return await self.user_repo.get(user_id)
