""" Custom storage classes """

from typing import Any

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import StorageKey
from aiogram.fsm.storage.redis import RedisStorage

from core.schemas.product import Product
from core.schemas.sub_product import SubProduct, SubProductCollection


class Storage(RedisStorage):
    PRODUCT_KEY: str = 'product'
    PRODUCT_ID_KEY: str = 'product_id'
    SUBS_KEY: str = 'subs'

    async def get_subs_info(self, key: StorageKey) -> SubProductCollection:
        data: dict[str, dict] = await self.get_data(key)
        sub_prod_col: SubProductCollection = SubProductCollection.model_validate_json(
            data[self.SUBS_KEY]
        )
        return sub_prod_col

    async def get_product(self, key: StorageKey) -> Product:
        data: dict[str, Any] = await self.get_data(key)
        product: Product | None = Product.model_validate_json(data.get(self.PRODUCT_KEY))
        if not product:
            raise ValueError('Не удалось получить информацию о продукте из хранилища!')
        return product

    async def get_prod_id(self, key: StorageKey) -> int:
        data: dict[str, Any] = await self.get_data(key)
        prod_id: int | None = data.get(self.PRODUCT_ID_KEY)
        if not prod_id:
            raise ValueError('Не удалось получить информацию о Ид продукта из хранилища!')
        return prod_id

    async def write_product(self, key: StorageKey, product: Product) -> None:
        await self.set_data(key, {self.PRODUCT_KEY: product.model_dump_json(by_alias=True)})

    async def write_prod_id(self, key: StorageKey, prod_id: int) -> None:
        await self.set_data(key, {self.PRODUCT_ID_KEY: prod_id})

    async def init_subs(
        self, key: StorageKey, subs: list[SubProduct], sub_cnt: int
    ) -> SubProductCollection:
        sub_collection = SubProductCollection(subs=subs, total_sub_cnt=sub_cnt)
        await self.set_data(key, {self.SUBS_KEY: sub_collection.model_dump_json(by_alias=True)})
        return sub_collection

    async def write_subs(self, key: StorageKey, subs: SubProductCollection) -> None:
        await self.set_data(key, {self.SUBS_KEY: subs.model_dump_json(by_alias=True)})


class Context(FSMContext):
    def __init__(self, storage: Storage, key: StorageKey):
        self.storage: Storage = storage
        super().__init__(self.storage, key)
