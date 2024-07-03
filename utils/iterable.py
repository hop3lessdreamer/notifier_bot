import functools
import operator
from collections.abc import Iterable, Sequence
from typing import Any, TypeVar

T = TypeVar('T')


def first(iterable: Iterable[T], default: T | None = None) -> T | None:
    """Returns the first element if exists or default value"""
    return next(iter(iterable), default)


def get_batches(value: Sequence[T], batch_size: int) -> list[Sequence[T]]:
    if not value or batch_size < 0:
        return [value]
    return [value[i : i + batch_size] for i in range(0, len(value), batch_size)]


def get_value_by_path(dictionary: dict, path: str) -> Any:
    """
    Returns value of dict by path
    :param dictionary: dictionary value
    :param path: path divided "/"
    :return: Any
    """

    return functools.reduce(operator.getitem, path.split('/'), dictionary)
