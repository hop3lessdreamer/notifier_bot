""""""

from typing import Iterable, Any, TypeVar


T = TypeVar('T')


def first(iterable: Iterable, default=None) -> Any:
    """ Returns the first element if exists or default value """
    return next(iter(iterable), default)


def get_batches(value: list[T], batch_size: int) -> list[list[T]]:
    if not value or batch_size < 0:
        return value
    return [value[i:i+batch_size] for i in range(0, len(value), batch_size)]
