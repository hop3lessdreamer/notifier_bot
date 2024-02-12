""" Test WB API and WbParser """

from requests import get
from http import HTTPStatus

import pytest

from core.wb.wb_parser import WbParser, WbProduct

from utils.iterable import first

pytest_plugins = ('pytest_asyncio',)

SUCCESS_PRODUCT_ID = [19456624]
SUCCESS_PRODUCT_IDS = [19456624, 19456621]


@pytest.fixture
def product_response():
    return get(WbParser(SUCCESS_PRODUCT_ID).url)


@pytest.fixture
def products_response():
    return get(WbParser(SUCCESS_PRODUCT_IDS).url)


def test_status_success_response(product_response):
    assert product_response.status_code == HTTPStatus.OK


def test_answer_success_response_single_product(product_response):
    assert product_response.json() is not None


def test_answer_success_response_mass_product(products_response):
    assert products_response.json() is not None


def test_response_structure(product_response):
    data = product_response.json().get('data', {})
    products = data.get('products', [])
    product = first(products, {})
    product_id = product.get('id')
    product_price = product.get('salePriceU')

    assert data is not None
    assert products is not None
    assert product is not None
    assert product_id is not None
    assert product_price is not None


@pytest.mark.asyncio
async def test_get_wb_products():
    products: dict[int, WbProduct] = await WbParser(SUCCESS_PRODUCT_ID).get_wb_products()
    product: WbProduct = first(products.values())

    assert product.id == first(SUCCESS_PRODUCT_ID)
    assert isinstance(product.price, float) and product.price is not None
    assert isinstance(product.title, str) and product.title is not None
