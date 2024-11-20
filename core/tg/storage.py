""" Custom storage classes """

from typing import Any

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage, StorageKey

from core.schemas.product import Product
from core.schemas.sub_product import SubProduct, SubProductCollection


class Storage(MemoryStorage):
    PRODUCT_KEY: str = 'product'
    SUBS_KEY: str = 'subs'

    async def get_product_id(self, key: StorageKey) -> int | None:
        data: dict[str, Any] = await self.get_data(key)
        return data.get('product_id')

    async def get_subs_info(self, key: StorageKey) -> SubProductCollection:
        data: dict[str, SubProductCollection] = await self.get_data(key)
        return data[self.SUBS_KEY]

    async def get_product(self, key: StorageKey) -> Product:
        data: dict[str, Any] = await self.get_data(key)
        product: Product | None = data.get(self.PRODUCT_KEY)
        if not product:
            raise ValueError('Не удалось получить информацию о продукте из хранилища!')
        return product

    async def write_product(self, key: StorageKey, product: Product) -> None:
        await self.set_data(key, {self.PRODUCT_KEY: product})

    async def init_subs(
        self, key: StorageKey, subs: list[SubProduct], sub_cnt: int
    ) -> SubProductCollection:
        sub_collection = SubProductCollection(subs, sub_cnt)
        await self.set_data(key, {self.SUBS_KEY: sub_collection})
        return sub_collection

    async def write_subs(self, key: StorageKey, subs: SubProductCollection) -> None:
        await self.set_data(key, {self.SUBS_KEY: subs})


class Context(FSMContext):
    def __init__(self, storage: Storage, key: StorageKey):
        self.storage: Storage = storage
        super().__init__(self.storage, key)
