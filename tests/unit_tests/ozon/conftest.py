import pytest

from core.ozon.parser import OzonProductParser


SUCCESS_PRODUCTS = [146427172]


@pytest.fixture(scope='session')
def ozon_parser():
    return OzonProductParser(SUCCESS_PRODUCTS[0])
