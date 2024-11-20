""" OzonParser """


import re
from decimal import Decimal
from functools import cached_property
from typing import Any, cast

from aiohttp import ClientSession, ClientTimeout

from core.exceptions import OzonProductOutOfStock, OzonProductValidateError, ResponseError
from core.schemas.product import Product
from utils.iterable import first
from utils.response import DEFAULT_TIMEOUT, get_fake_headers
from utils.transform_types import from_json_to_dict, get_int, try_get_decimal

PRODUCT_ID_IN_URI = re.compile(r'product.+-(\d+)\/')
ONLY_DIGITS = re.compile(r'\d+')


class OzonProductParser:
    BASE_URL = 'https://api.ozon.ru/'
    PRODUCT_URL = f'{BASE_URL}entrypoint-api.bx/page/json/v2?url=%2Fproduct%2F'

    def __init__(self, product_id: int):
        self.product_id: int = product_id

    @cached_property
    def url(self) -> str:
        return f'{self.PRODUCT_URL}{self.product_id}'

    async def _request_product_info(self) -> dict[str, Any]:
        """Makes request to ozon api and returns product info"""

        async with ClientSession(
            timeout=ClientTimeout(total=DEFAULT_TIMEOUT), headers=get_fake_headers()
        ) as session, session.get(self.url) as response:
            return cast(dict[str, Any], await response.json())

    async def get_product(self) -> Product:
        """Returns parsed ozon product as Product"""

        product_info: dict[str, Any] = await self._request_product_info()
        widget_states: dict[str, str] = cast(dict[str, str], product_info.get('widgetStates'))
        if not widget_states:
            raise ResponseError('Изменился ответ у OZON api!')

        title: str | None = None
        price: Decimal | None = None
        img: bytes | None = None

        for k, v in widget_states.items():
            if (
                k.startswith('webOutOfStock-')
                and get_int(cast(dict[str, Any], from_json_to_dict(v)).get('sku'))
                == self.product_id
            ):
                raise OzonProductOutOfStock(f'Товар {self.product_id} закончился на складе!')
            if k.startswith('webGallery-'):
                imgs_info: dict[str, Any] = cast(dict[str, Any], from_json_to_dict(v))
                img_uri: str | None = imgs_info.get('coverImage')
                if img_uri is None:
                    raise ResponseError('Изменился ответ у OZON api!')

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
            raise ResponseError('Изменился ответ у OZON api!')

        return Product(
            ID=self.product_id,
            Price=cast(Decimal, price),
            Title=cast(str, title),
            Img=cast(bytes, img),
        )

    @staticmethod
    def validate_product_id(value: str) -> int:
        """Returns product id by uri or product id or raise OzonProductValidateError"""

        product_id: int | None = get_int(value)
        if product_id is not None:
            return product_id

        product_id = first(re.findall(PRODUCT_ID_IN_URI, value) or [])
        if product_id is None:
            raise OzonProductValidateError

        return cast(int, product_id)
