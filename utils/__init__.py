""" Module init """

from json import JSONEncoder
from typing import Any

from _decimal import Decimal


class Encoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, Decimal):
            return str(o)
        return JSONEncoder.default(self, o)
