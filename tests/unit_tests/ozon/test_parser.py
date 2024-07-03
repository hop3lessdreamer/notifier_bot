""" Tests OzonParser """

import pytest

from core.exceptions import OzonProductOutOfStock
from core.ozon.parser import OzonProductParser
from schemas.product import Product


@pytest.mark.asyncio
@pytest.mark.xfail(raises=OzonProductOutOfStock)
async def test_parser(ozon_parser: OzonProductParser):
    product: Product = await ozon_parser.get_product()

    assert product.title.startswith('Пюре фруктовое ФрутоНяня')
    assert product.price is not None
    assert product.img is not None
