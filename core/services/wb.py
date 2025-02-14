import re
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, cast

from aiohttp import ClientSession, ClientTimeout
from loguru import logger

from core.exceptions import WbApiError, WbProductValidateError
from core.schemas.product import Product
from utils.response import DEFAULT_TIMEOUT, get_fake_headers
from utils.transform_types import from_bytes_to_b64
from utils.types import ProductID, b64

url_parse = re.compile(r'(http[s]?:\/\/)?([^\/\s]+\/)(catalog)\/(\d+)')


class WbProductImgService:
    RAW_URL_TO_GET_PRODUCT_IMG = 'https:{}/vol{}/part{}/{}/images/c{}/{}.jpg'
    ALT_RAW_URL_TO_GET_PRODUCT_IMG = 'https:{}/vol{}/part{}/{}/images/c{}/{}.webp'
    DEFAULT_IMG_SIZE = '246x328'
    #   Take main prod img
    DEFAULT_IMG_NUMBER = 1

    async def download_products_img(self, product_ids: list[ProductID]) -> dict[ProductID, b64]:
        return {pid: await self.download_product_img(pid) for pid in product_ids}

    async def download_product_img(self, product_id: ProductID) -> b64:
        downloaded_img: bytes | None = await self._request_to_get_img(product_id)
        if not downloaded_img:
            downloaded_img = await self._request_to_get_img_by_alt_url(product_id)
        if not downloaded_img:
            raise WbApiError(f'Не удалось получить изображение товара {product_id}!')

        return from_bytes_to_b64(downloaded_img)

    async def _request_to_get_img(self, product_id: ProductID) -> bytes | None:
        url: str = self._get_img_url(product_id)
        logger.info(f'request ("{url}") to download img' f' by product = {product_id}.')
        async with ClientSession(
            timeout=ClientTimeout(total=DEFAULT_TIMEOUT), headers=get_fake_headers()
        ) as session, session.get(url) as response:
            if response.status >= HTTPStatus.BAD_REQUEST:
                logger.warning(
                    f'Не удалось получить изображения товара "{product_id}".\
                    Попробуем альтернативный url.'
                )
                return None
            return cast(bytes, await response.read())

    async def _request_to_get_img_by_alt_url(self, product_id: ProductID) -> bytes | None:
        url: str = self._get_img_url_alt(product_id)
        logger.info(f'request ("{url}") to download img' f' by product = {product_id}.')
        async with ClientSession(
            timeout=ClientTimeout(total=DEFAULT_TIMEOUT), headers=get_fake_headers()
        ) as session, session.get(url) as response:
            if response.status >= HTTPStatus.BAD_REQUEST:
                logger.error(f'Не удалось получить изображения товара "{product_id}".')
                return None
            return cast(bytes, await response.read())

    def _get_img_url(self, product_id: ProductID) -> str:
        url_vol: int = self._get_img_url_vol(product_id)
        return self.RAW_URL_TO_GET_PRODUCT_IMG.format(
            self._get_img_url_host(url_vol),
            url_vol,
            self._get_img_url_part(product_id),
            product_id,
            self.DEFAULT_IMG_SIZE,
            self.DEFAULT_IMG_NUMBER,
        )

    def _get_img_url_alt(self, product_id: ProductID) -> str:
        url_vol: int = self._get_img_url_vol(product_id)
        return self.ALT_RAW_URL_TO_GET_PRODUCT_IMG.format(
            self._get_img_url_host(url_vol),
            url_vol,
            self._get_img_url_part(product_id),
            product_id,
            self.DEFAULT_IMG_SIZE,
            self.DEFAULT_IMG_NUMBER,
        )

    @staticmethod
    def _get_img_url_vol(product_id: ProductID) -> int:
        return product_id // 10**5

    @staticmethod
    def _get_img_url_part(product_id: ProductID) -> int:
        return product_id // 10**3

    @staticmethod
    def _get_img_url_host(vol: int) -> str:
        if 0 <= vol <= 143:
            return '//basket-01.wbbasket.ru'
        elif 144 <= vol <= 287:
            return '//basket-02.wbbasket.ru'
        elif 288 <= vol <= 431:
            return '//basket-03.wbbasket.ru'
        elif 432 <= vol <= 719:
            return '//basket-04.wbbasket.ru'
        elif 720 <= vol <= 1007:
            return '//basket-05.wbbasket.ru'
        elif 1008 <= vol <= 1061:
            return '//basket-06.wbbasket.ru'
        elif 1062 <= vol <= 1115:
            return '//basket-07.wbbasket.ru'
        elif 1116 <= vol <= 1169:
            return '//basket-08.wbbasket.ru'
        elif 1170 <= vol <= 1313:
            return '//basket-09.wbbasket.ru'
        elif 1314 <= vol <= 1601:
            return '//basket-10.wbbasket.ru'
        elif 1602 <= vol <= 1655:
            return '//basket-11.wbbasket.ru'
        elif 1656 <= vol <= 1919:
            return '//basket-12.wbbasket.ru'
        elif 1920 <= vol <= 2045:
            return '//basket-13.wbbasket.ru'
        elif 2045 <= vol <= 2189:
            return '//basket-14.wbbasket.ru'
        elif 2189 <= vol <= 2405:
            return '//basket-15.wbbasket.ru'
        elif 2405 <= vol <= 2621:
            return '//basket-16.wbbasket.ru'
        elif 2621 <= vol <= 2837:
            return '//basket-17.wbbasket.ru'

        return '//basket-18.wbbasket.ru'


class WbProductInfoService:
    RAW_URL_TO_GET_PRODUCT_INFO = 'https://card.wb.ru/cards/detail?curr=rub&dest=-1257786&nm={}'

    async def request_products_data(self, product_ids: list[ProductID]) -> list[dict[str, Any]]:
        prod_info: dict[str, Any] = await self._get_raw_products_info(product_ids)
        data: dict[str, Any] = prod_info.get('data', {})
        if not data:
            raise WbApiError(
                f'Не удалось получить информацию по товарам {product_ids}! \
                Вероятно изменился ответ в API!'
            )

        prods: list[dict[str, Any]] = data.get('products', [])
        if not prods:
            raise WbApiError(
                f'Не удалось получить информацию по товарам {product_ids}! \
                Вероятно изменился ответ в API!'
            )

        return prods

    async def _get_raw_products_info(self, product_ids: list[ProductID]) -> dict[str, Any]:
        url: str = self._url_to_get_info(product_ids)
        logger.info(f'request ("{url}") for products info ({product_ids})')
        async with ClientSession(
            timeout=ClientTimeout(total=DEFAULT_TIMEOUT), headers=get_fake_headers()
        ) as session, session.get(url) as response:
            return cast(dict[str, Any], await response.json())

    def _url_to_get_info(self, product_ids: list[ProductID]) -> str:
        return self.RAW_URL_TO_GET_PRODUCT_INFO.format(';'.join(map(str, product_ids)))


@dataclass
class WbService:
    wb_img_service: WbProductImgService
    wb_prod_info_service: WbProductInfoService

    async def get_products(self, product_ids: list[ProductID]) -> list[Product]:
        if not product_ids:
            return []
        prod_imgs: dict[int, b64] = await self.wb_img_service.download_products_img(product_ids)
        prod_data: list[dict[str, Any]] = await self.wb_prod_info_service.request_products_data(
            product_ids
        )
        logger.info(f'prod_data = {prod_data}')
        return [
            Product.from_json_api(prod_item, prod_imgs[prod_item['id']]) for prod_item in prod_data
        ]

    async def get_prods_by_prod_id(self, product_ids: list[ProductID]) -> dict[ProductID, Product]:
        return {product.id: product for product in await self.get_products(product_ids)}

    async def try_get_product(self, product_id: ProductID) -> Product | None:
        product: Product | None = None
        try:
            products: list[Product] = await self.get_products(product_ids=[product_id])
            product = products[0]
        except WbApiError as ex:
            logger.error(f'Ошибка при получении товара ({ex})!')
        return product

    @staticmethod
    def validate_product_url(url: str) -> ProductID:
        try:
            matching: re.Match | None = re.match(url_parse, url)
            if matching is None:
                raise BaseException('Регулярное выражение не нашло ид продукта!')
            return int(matching.group(4))
        except BaseException as ex:
            raise WbProductValidateError(
                f'Ошибка при попытке провалидировать {url} от пользователя: {ex}!'
            ) from ex

    @staticmethod
    def try_validate_product_url(url: str) -> ProductID | None:
        prod_id: ProductID | None = None
        try:
            prod_id = WbService.validate_product_url(url)
        except WbProductValidateError as ex:
            logger.info(ex)
        return prod_id

    @staticmethod
    def form_url_by_product_id(product_id: ProductID) -> str:
        return f'https://www.wildberries.ru/catalog/{str(product_id)}/detail.aspx'
