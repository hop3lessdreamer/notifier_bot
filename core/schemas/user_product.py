""" UserProduct's schema """

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.types import PositiveInt

from utils.transform_types import get_decimal


class UserProduct(BaseModel):
    user_id: PositiveInt = Field(alias='UserID')
    product_id: PositiveInt = Field(alias='ProductID')
    price_threshold: Decimal = Field(alias='PriceThreshold')
    added: datetime = Field(alias='Added')
    changed: datetime | None = Field(alias='Changed')

    model_config = ConfigDict(from_attributes=True)

    @field_validator('price_threshold', mode='after')
    @classmethod
    def set_precision_to_price(cls, price_threshold: Decimal) -> Decimal:
        return get_decimal(price_threshold, 2)


class UserProductAdd(BaseModel):
    user_id: PositiveInt = Field(alias='UserID')
    product_id: PositiveInt = Field(alias='ProductID')
    price_threshold: Decimal = Field(alias='PriceThreshold')
