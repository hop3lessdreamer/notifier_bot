from sqlalchemy import insert
from core.services.user import UserService
from db import db
from infrastructure.db.models.user import UserModel
from infrastructure.db.repositories.user import UserRepoImpl

import pytest


@pytest.mark.asyncio
async def test_create_user(users):
    service = UserService(UserRepoImpl(db))
    user1 = await service.create_user(users[0])
    user2 = await service.create_user(users[1])

    assert user1.id == users[0].id and user1.chat_id == users[0].chat_id and user1.tz_offset == users[0].tz_offset, 'creation user1 failed'
    assert user2.id == users[1].id and user2.chat_id == users[1].chat_id and user2.tz_offset == users[1].tz_offset, 'creation user2 failed'


@pytest.mark.asyncio
async def test_create_existing_user(users):
    with db.session() as session:
            session.execute(
                insert(UserModel)
                .values(ID=users[1].id, ChatID=users[1].chat_id, TZOffset=users[1].tz_offset)
            )
            session.commit()

    service = UserService(UserRepoImpl(db))
    user2 = await service.create_user(users[1])

    assert user2.id == users[1].id and user2.chat_id == users[1].chat_id and user2.tz_offset == users[1].tz_offset, 'creation user2 failed'


@pytest.mark.asyncio
async def test_get_existing_user(users):
    with db.session() as session:
            session.execute(
                insert(UserModel)
                .values(ID=users[1].id, ChatID=users[1].chat_id, TZOffset=users[1].tz_offset)
            )
            session.commit()

    service = UserService(UserRepoImpl(db))
    user = await service.try_get_user(users[1].id)

    assert user.id == users[1].id and user.chat_id == users[1].chat_id and user.tz_offset == users[1].tz_offset


@pytest.mark.asyncio
async def test_get_not_existing_user(users):
    service = UserService(UserRepoImpl(db))
    user = await service.try_get_user(users[1].id)

    assert user is None
