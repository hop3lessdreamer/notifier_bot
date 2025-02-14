import pytest
from core.services.wb import WbProductImgService
from utils.transform_types import from_bytes_to_b64


SUCCESS_PRODUCT_ID = 19456624
SUCCESS_PRODUCT_IDS = [19456624, 19456621]


@pytest.fixture
def empty_get_img(monkeypatch):
    async def mocked_req_get_img(*args, **kwargs):
        return None

    async def mocked_req_get_alt_img(*args, **kwargs):
        return 'Альтернативное изображение товара'.encode()

    monkeypatch.setattr(WbProductImgService, '_request_to_get_img', mocked_req_get_img)
    monkeypatch.setattr(WbProductImgService, '_request_to_get_img_by_alt_url', mocked_req_get_alt_img)


@pytest.mark.asyncio
async def test_download_product_img(empty_get_img):
    assert await WbProductImgService().download_product_img(SUCCESS_PRODUCT_ID) \
        == from_bytes_to_b64('Альтернативное изображение товара'.encode())


@pytest.mark.asyncio
async def test_request_to_get_img():
    has_img: bool = bool(await WbProductImgService()._request_to_get_img(SUCCESS_PRODUCT_ID))
    if not has_img:
        has_img = bool(await WbProductImgService()._request_to_get_img_by_alt_url(SUCCESS_PRODUCT_ID))
    assert has_img == True
