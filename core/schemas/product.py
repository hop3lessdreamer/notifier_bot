""" Product's schema """
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from functools import cached_property
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.types import PositiveInt

from core.exceptions import WbApiError
from utils.transform_types import get_decimal
from utils.types import b64


class MPType(StrEnum):
    """Market Place type"""

    WB: str = 'WB'
    OZON: str = 'OZON'


class Product(BaseModel):
    id: PositiveInt = Field(alias='ID')
    price: Decimal = Field(alias='Price', gt=0)
    img: bytes = Field(alias='Img', min_length=1)
    title: str = Field(alias='Title', min_length=1)
    mp_type: MPType = Field(alias='MPType')

    @field_validator('price', mode='after')
    @classmethod
    def set_precision_to_price(cls, price: Decimal) -> Decimal | None:
        return get_decimal(price, 2)

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_json_api(cls, prod_info: dict[str, Any], prod_img: b64) -> 'Product':
        try:
            return Product(
                ID=prod_info['id'],
                Price=get_decimal(prod_info['salePriceU'] / 100, 2),
                Img=prod_img,
                Title=f'{prod_info["brand"]}/{prod_info["name"]}',
                MPType=MPType.WB,
            )
        except BaseException as ex:
            raise WbApiError(f'Не удалось получить Product из {prod_info}!') from ex


@dataclass
class WbProduct:
    id: int = 0
    title: str = ''
    price: float = 0

    @cached_property
    def empty(self) -> bool:
        return not any((self.id, self.title, self.price))

    @cached_property
    def rounded_price(self) -> Decimal:
        return get_decimal(self.price, precision=2)

    @classmethod
    def from_json(cls, data: dict[str, Any] | None) -> 'WbProduct':
        if not data:
            return cls()

        pid = data.get('id') or cls.id

        price: float = 0
        raw_price = data.get('salePriceU')
        if raw_price is not None:
            price = raw_price / 100

        title: str = ''
        brand, name = data.get('brand') or '', data.get('name') or ''
        if brand or name:
            title = f'{brand}/{name}'

        return cls(pid, title, price)
