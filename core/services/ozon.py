import random
import re
from decimal import Decimal
from time import sleep
from typing import Any, cast

from aiohttp import ClientSession, ClientTimeout
from loguru import logger

from core.exceptions import OzonApiError, OzonProductOutOfStock, OzonProductValidateError
from core.schemas.product import MPType, Product
from utils.response import DEFAULT_TIMEOUT, get_fake_headers
from utils.transform_types import from_bytes_to_b64, from_json_to_dict, get_int, try_get_decimal
from utils.types import ProductID

url_parse = re.compile(r'/product/[-\w]+-(\d+)/')
ONLY_DIGITS = re.compile(r'\d+')


class OzonService:
    API_URL = 'https://api.ozon.ru/'
    PRODUCT_URI = f'{API_URL}entrypoint-api.bx/page/json/v2?url=%2Fproduct%2F'

    @staticmethod
    def validate_product_url(url: str) -> ProductID:
        #   url like https://www.ozon.ru/product/1604786416
        try:
            return int(url.split('product/')[-1])
        except BaseException:
            pass
        #   url like https://www.ozon.ru/product/ketchup-heinz-tomatnyy-320-g-1617373497/?avtc=1&avte=4&avts=1736782751
        try:
            matching: re.Match | None = re.search(url_parse, url)
            if matching is None:
                raise BaseException('Регулярное выражение не нашло ид продукта!')
            return int(matching.group(1))
        except BaseException as ex:
            raise OzonProductValidateError(
                f'Ошибка при попытке провалидировать {url} от пользователя: {ex}!'
            ) from ex

    @staticmethod
    def try_validate_product_url(url: str) -> ProductID | None:
        prod_id: ProductID | None = None
        try:
            prod_id = OzonService.validate_product_url(url)
        except OzonProductValidateError as ex:
            logger.info(ex)
        return prod_id

    async def try_get_product(self, product_id: ProductID) -> Product | None:
        product: Product | None = None
        try:
            product = await self.get_product(product_id)
        except OzonApiError as ex:
            logger.error(f'Ошибка при получении товара ({ex})!')
        return product

    async def try_get_products(self, products_ids: list[ProductID]) -> dict[ProductID, Product]:
        products: dict[ProductID, Product] = {}
        for product_id in products_ids:
            prod: Product | None = await self.try_get_product(product_id)
            if prod is None:
                sleep(random.randrange(start=2, stop=10, step=1))
                continue
            products[product_id] = prod
            sleep(random.randrange(start=2, stop=10, step=1))
        return products

    async def get_product(self, product_id: ProductID) -> Product:
        """Returns parsed ozon product as Product"""

        product_info: dict[str, Any] = await self._request_product_info(product_id)
        widget_states: dict[str, str] = cast(dict[str, str], product_info.get('widgetStates'))
        if not widget_states:
            raise OzonApiError('Изменился ответ у OZON api!')

        title: str | None = None
        price: Decimal | None = None
        img: bytes = b''

        for k, v in widget_states.items():
            if (
                k.startswith('webOutOfStock-')
                and get_int(cast(dict[str, Any], from_json_to_dict(v)).get('sku')) == product_id
            ):
                raise OzonProductOutOfStock(f'Товар {product_id} закончился на складе!')
            if k.startswith('webGallery-'):
                imgs_info: dict[str, Any] = cast(dict[str, Any], from_json_to_dict(v))
                img_uri: str | None = imgs_info.get('coverImage')
                logger.debug(f'img_uri = {img_uri}')
                if img_uri is None:
                    raise OzonApiError('Изменился ответ у OZON api!')

                async with ClientSession(
                    timeout=ClientTimeout(total=DEFAULT_TIMEOUT), headers=get_fake_headers()
                ) as session, session.get(img_uri) as response:
                    img = await response.read()

            elif k.startswith('webPrice-'):
                price_info: dict[str, Any] = cast(dict[str, Any], from_json_to_dict(v))
                raw_price: str = price_info.get('price', '')
                price = try_get_decimal((re.search(ONLY_DIGITS, raw_price) or re.Match()).group())

            elif k.startswith('webProductHeading-'):
                heading_info: dict[str, Any] = cast(dict[str, Any], from_json_to_dict(v))
                title = heading_info.get('title')

        if not (any((title, price, img))):
            raise OzonApiError('Изменился ответ у OZON api!')

        return Product(
            ID=product_id,
            Price=cast(Decimal, price),
            Title=cast(str, title),
            Img=cast(bytes, from_bytes_to_b64(img)),
            MPType=MPType.OZON,
        )

    def _get_prod_uri(self, product_id: ProductID) -> str:
        return f'{self.PRODUCT_URI}{product_id}'

    async def _request_product_info(self, product_id: ProductID) -> dict[str, Any]:
        async with ClientSession(
            timeout=ClientTimeout(total=DEFAULT_TIMEOUT), headers=get_fake_headers()
        ) as session, session.get(self._get_prod_uri(product_id)) as response:
            return cast(dict[str, Any], await response.json())

    @staticmethod
    def form_url_by_product_id(product_id: ProductID) -> str:
        return f'https://www.ozon.ru/product/{product_id}'
