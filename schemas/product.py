""" Product's schema """

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.types import PositiveInt

from utils.transform_types import get_decimal


class Product(BaseModel):
    id: PositiveInt = Field(alias='ID')
    price: Decimal = Field(alias='Price')
    img: bytes = Field(alias='Img')
    title: str = Field(alias='Title')

    @field_validator('price', mode='after')
    @classmethod
    def set_precision_to_price(cls, price: Decimal) -> Decimal | None:
        return get_decimal(price, 2)

    model_config = ConfigDict(from_attributes=True)
