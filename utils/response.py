""" Supporting tools for working with http requests """
from typing import cast

from fake_useragent import FakeUserAgent

DEFAULT_TIMEOUT = 3


def get_fake_ua() -> str:
    return cast(str, FakeUserAgent().random)


def get_fake_headers() -> dict[str, str]:
    return {'user-agent': get_fake_ua()}
