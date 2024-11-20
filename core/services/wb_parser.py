from functools import cached_property
from typing import Any, cast

from aiohttp import ClientSession, ClientTimeout
from loguru import logger as loguru_logger

from core.schemas.product import WbProduct
from core.wb.wb_img_downloader import WbImgsDownloader
from utils.response import DEFAULT_TIMEOUT, get_fake_headers
from utils.types import ProductID


class WbParserService:
    """Class that allow parse product card by product ids"""

    RAW_URL = 'https://card.wb.ru/cards/detail?curr=rub&dest=-1257786&nm={}'

    def __init__(self, product_ids: list[int]) -> None:
        self.product_ids: list[int] = product_ids

        self.downloaders: WbImgsDownloader = WbImgsDownloader(product_ids)

    async def get_wb_products(self) -> dict[ProductID, WbProduct]:
        """Returns product prices"""

        products: dict[ProductID, WbProduct] = {}

        products_info = await self.get_products_info()
        if not products_info:
            return products

        for product in products_info:
            wb_product = WbProduct.from_json(product)
            if wb_product.empty:
                loguru_logger.error(
                    f'Не удалось получить информацию по товару {wb_product.id}!'
                    f' (ids = {self.product_ids})'
                )
                continue
            products[wb_product.id] = wb_product

        return products

    @cached_property
    def url(self) -> str:
        """Return prepared url"""
        return self.RAW_URL.format(self.__prepare_query_param_nm())

    @loguru_logger.catch(BaseException)
    async def request_products_info(self) -> dict[str, Any]:
        """Returns product info"""
        loguru_logger.info(f'request ("{self.url}") for products info ({self.product_ids})')
        async with ClientSession(
            timeout=ClientTimeout(total=DEFAULT_TIMEOUT), headers=get_fake_headers()
        ) as session, session.get(self.url) as response:
            return cast(dict[str, Any], await response.json())

    async def get_products_info(self) -> list[dict[str, Any]] | None:
        product_info: dict[str, Any] = await self.request_products_info()
        data: dict[str, Any] = product_info.get('data', {})
        if not data:
            loguru_logger.error('Не удалось получить данные из запроса!')
            return None

        products_info: list[dict[str, Any]] = data.get('products', [])
        if not products_info:
            loguru_logger.error(
                'Не удалось получить данные о товарах! ' '(Возможно изменился ответ запроса)'
            )
            return None

        return products_info

    def __prepare_query_param_nm(self) -> str:
        """Returns query param nm from product_ids"""
        return ';'.join(map(str, self.product_ids))
