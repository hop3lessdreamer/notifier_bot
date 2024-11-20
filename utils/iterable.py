import functools
import operator
from collections.abc import Iterable
from typing import Any, TypeVar

T = TypeVar('T')


def first(iterable: Iterable[T], default: T | None = None) -> T | None:
    """Returns the first element if exists or default value"""
    return next(iter(iterable), default)


def get_value_by_path(dictionary: dict, path: str) -> Any:
    """
    Returns value of dict by path
    :param dictionary: dictionary value
    :param path: path divided "/"
    :return: Any
    """

    return functools.reduce(operator.getitem, path.split('/'), dictionary)
