import pytest
from core.services.wb import WbProductInfoService


SUCCESS_PRODUCT_ID = 19456624
SUCCESS_PRODUCT_IDS = [19456624, 19456621]


@pytest.mark.asyncio
async def test_get_raw_prod_info():
    has_info: dict[str, Any] = bool(await WbProductInfoService()._get_raw_products_info([SUCCESS_PRODUCT_ID]))
    assert has_info == True
