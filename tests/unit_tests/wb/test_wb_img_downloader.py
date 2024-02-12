""" Tests for WbImgDownloaderMixin """

from requests import get, Response
from http import HTTPStatus

import pytest

from core.wb.wb_img_downloader import WbImgDownloader

pytest_plugins = ('pytest_asyncio',)


SUCCESS_PRODUCT_IDS = [59328864, 99186165, 143503418]


@pytest.fixture(params=SUCCESS_PRODUCT_IDS)
def img_response(request) -> Response:
    return get(WbImgDownloader(request.param).img_url)


def test_scs_responses(img_response):
    assert img_response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_download():
    downloaded: bytes = await WbImgDownloader(SUCCESS_PRODUCT_IDS[0]).download()
    assert downloaded is not None
    assert isinstance(downloaded, bytes)
