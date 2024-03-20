""" User's schema """

from pydantic import BaseModel, ConfigDict, Field
from pydantic.types import PositiveInt


class User(BaseModel):
    id: PositiveInt = Field(alias='ID')
    chat_id: int = Field(alias='ChatID')
    tz_offset: int = Field(alias='TZOffset')

    model_config = ConfigDict(from_attributes=True)
