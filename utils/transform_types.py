""" Functions that helps work with types """

from base64 import b64decode, b64encode
from decimal import Decimal
from json import dumps, loads

from utils import Encoder, JSONEncoder
from utils.types import b64


def get_int(value: str | int | None, default: int | None = None) -> int | None:
    """Return int value or default"""
    try:
        return int(value)  # type: ignore
    except (ValueError, TypeError):
        return default


def from_json_to_dict(value: str, default: dict | None = None) -> dict | None:
    if not value:
        return default
    return loads(value)  # type: ignore


def from_dict_to_json(value: dict, default: str = '', encoder: type[JSONEncoder] = Encoder) -> str:
    if not value:
        return default
    return dumps(value, cls=encoder)


def from_bytes_to_b64(data: bytes, default: b64 = b'') -> b64:  # type: ignore
    if not data:
        return default
    return b64encode(data)  # type: ignore


def from_b64_to_bytes(data: b64, default: bytes = b'') -> bytes:
    if not data:
        return default
    return b64decode(data)


def get_decimal(
    value: str | int | float | Decimal, precision: int | None = None, default: Decimal | None = None
) -> Decimal | None:
    try:
        decimal_value = Decimal(value)
        if precision:
            decimal_value = decimal_value.quantize(Decimal(str(1 / (10 * precision))))
        return decimal_value
    except BaseException:
        return default


def get_percents(value: int | float | str, default: float | None = None) -> float | None:
    percents: Decimal | None = get_decimal(value, 1)
    if not percents or percents >= 100:
        return default

    return float(percents)
