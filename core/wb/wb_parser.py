""" Module contains class that allow parse product card by products id """

from dataclasses import dataclass
from decimal import Decimal
from functools import cached_property as cached_prop
from typing import Any

from aiohttp import ClientSession, ClientTimeout
from asyncstdlib.functools import cached_property

from core.wb.wb_img_downloader import WbImgsDownloader
from logger import logger
from utils.response import DEFAULT_TIMEOUT, get_fake_headers
from utils.transform_types import get_decimal


@dataclass
class WbProduct:
    id: int | None = None
    title: str = ''
    price: float | None = None

    @cached_prop
    def empty(self) -> bool:
        return not any((self.id, self.title, self.price))

    @cached_prop
    def rounded_price(self) -> Decimal | None:
        return get_decimal(self.price, precision=2) if self.price else None

    @classmethod
    def from_json(cls, data: dict[str, Any] | None) -> 'WbProduct':

        if not data:
            return cls()

        price = None
        raw_price = data.get('salePriceU')
        if raw_price is not None:
            price = raw_price / 100

        brand, name = data.get('brand') or '', data.get('name') or ''
        title: str = ''
        if brand or name:
            title = f'{brand}/{name}'

        return cls(
            data.get('id'),
            title,
            price
        )


class WbParser:
    """ Class that allow parse product card by product ids """

    RAW_URL = 'https://card.wb.ru/cards/detail?nm={}'

    def __init__(self, product_ids: list[int]):
        self.product_ids: list[int] = product_ids

        self.downloaders: WbImgsDownloader = WbImgsDownloader(product_ids)

    @cached_prop
    def url(self):
        """ Return prepared url """
        return self.RAW_URL.format(self.__prepare_query_param_nm())

    def __prepare_query_param_nm(self):
        """ Returns query param nm from product_ids """
        return ';'.join(map(str, self.product_ids))

    @logger.catch
    async def request_products_info(self) -> dict[str, Any]:
        """ Returns product info """
        async with ClientSession(timeout=ClientTimeout(total=DEFAULT_TIMEOUT), headers=get_fake_headers()) as session:
            async with session.get(self.url) as response:
                return await response.json()

    @cached_property
    async def prepared_products_info(self) -> list[dict[str, Any]] | None:

        product_info: dict[str, Any] = await self.request_products_info()
        data: dict[str, Any] = product_info.get('data')
        if not data:
            logger.warning('Не удалось получить данные из запроса!')
            return None

        products_info: list[dict[str, Any]] = data.get('products')
        if not products_info:
            logger.warning('Не удалось получить данные о товарах! (Возможно изменился ответ запроса)')
            return None

        return products_info

    async def get_wb_products(self) -> dict[int, WbProduct]:
        """ Returns product prices """

        products: dict[int, WbProduct] = {}

        prepared_products_info = await self.prepared_products_info
        if not prepared_products_info:
            return products

        for product in prepared_products_info:
            wb_product = WbProduct.from_json(product)
            if wb_product.empty:
                logger.warning(f'Не удалось получить информацию по товару {wb_product.id}!'
                               f' (ids = {self.product_ids})')
                continue
            products[wb_product.id] = wb_product

        return products


if __name__ == '__main__':
    wb_parser = WbParser([61938863, 115779302, 23]).get_wb_products()
    print(wb_parser)
