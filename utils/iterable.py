from collections.abc import Iterable, Sequence
from typing import TypeVar

T = TypeVar('T')


def first(iterable: Iterable[T], default: T | None = None) -> T | None:
    """Returns the first element if exists or default value"""
    return next(iter(iterable), default)


def get_batches(value: Sequence[T], batch_size: int) -> list[Sequence[T]]:
    if not value or batch_size < 0:
        return [value]
    return [value[i : i + batch_size] for i in range(0, len(value), batch_size)]
