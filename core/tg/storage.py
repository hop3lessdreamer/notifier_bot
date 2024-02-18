""" Custom storage classes """

from typing import Any

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from core.wb.wb_parser import WbProduct
from db.queries import SubscriptionsInfo


class Storage(MemoryStorage):
    async def get_product_id(self, user: int, chat: int) -> int | None:
        data: dict[str, Any] = await self.get_data(user=user, chat=chat)
        return data.get('product_id')

    async def get_subs_info(self, user: int, chat: int) -> SubscriptionsInfo:
        data: dict[str, Any] = await self.get_data(user=user, chat=chat)
        return data.get('subs_info') or SubscriptionsInfo()

    async def get_wb_product(self, user: int, chat: int) -> WbProduct | None:
        data: dict[str, Any] = await self.get_data(user=user, chat=chat)
        return data.get('wb_product')

    async def write_wb_product(self, user: int, chat: int, wb_product: WbProduct) -> None:
        await self.update_data(user=user, chat=chat, wb_product=wb_product)

    async def init_subs(self, user: int, chat: int, subs_info: SubscriptionsInfo) -> None:
        await self.update_data(user=user, chat=chat, subs_info=subs_info)

    async def write_subs(self, user: int, chat: int, subs_info: SubscriptionsInfo) -> None:
        await self.init_subs(user, chat, subs_info)


class Context(FSMContext):
    def __init__(self, storage: Storage, chat: int, user: int):
        self.storage: Storage = storage
        super().__init__(self.storage, chat, user)
