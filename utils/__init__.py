""" Module init """

from _decimal import Decimal
from json import JSONEncoder
from typing import Any


class Encoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, Decimal):
            return str(o)
        return JSONEncoder.default(self, o)
