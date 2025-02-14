from dataclasses import dataclass
from typing import cast

from sqlalchemy import Result, exists, insert, select

from core.repositories.user import IUserRepo
from core.schemas.user import User
from db import Database
from infrastructure.db.models.user import UserModel


@dataclass
class UserRepoImpl(IUserRepo):
    db_conn: Database

    async def add(self, user: User) -> User:
        async with await self.db_conn() as session:
            user_result: Result = await session.execute(
                insert(UserModel)
                .values(ID=user.id, ChatID=user.chat_id, TZOffset=user.tz_offset)
                .returning(UserModel)
            )
            await session.commit()
        return cast(User, User.model_validate(user_result.scalar()))

    async def get(self, user_id: int) -> User | None:
        async with await self.db_conn() as session:
            user: Result = await session.execute(select(UserModel).where(user_id == UserModel.ID))
            user_mdl: UserModel | None = user.scalar()
            return User.model_validate(user_mdl) if user_mdl else None

    async def exist(self, user_id: int) -> bool:
        async with await self.db_conn() as session:
            user: Result = await session.execute(
                exists(UserModel.ID).where(user_id == UserModel.ID).select()
            )
            return cast(bool, user.scalar())
