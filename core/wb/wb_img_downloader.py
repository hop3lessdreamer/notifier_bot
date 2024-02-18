""" Contains classes that allow download main product image """
from functools import cached_property
from typing import Generic

from aiohttp import ClientSession, ClientTimeout

from logger import loguru_logger
from utils.response import DEFAULT_TIMEOUT, get_fake_headers
from utils.transform_types import from_bytes_to_b64
from utils.types import b64


class WbImgDownloader(Generic[b64]):
    RAW_IMG_URL = 'https:{}/vol{}/part{}/{}/images/c{}/{}.jpg'
    DEFAULT_IMG_SIZE = '246x328'
    #   taking main product img
    DEFAULT_IMG_NUMBER = '1'

    def __init__(self, product_id: int):
        self.product_id: int = product_id

        self.__vol: int = product_id // 10**5
        self.__part: int = product_id // 10**3

    @cached_property
    def __img_url_host(self) -> str:
        if 0 <= self.__vol <= 143:
            return '//basket-01.wbbasket.ru'
        elif 144 <= self.__vol <= 287:
            return '//basket-02.wbbasket.ru'
        elif 288 <= self.__vol <= 431:
            return '//basket-03.wbbasket.ru'
        elif 432 <= self.__vol <= 719:
            return '//basket-04.wbbasket.ru'
        elif 720 <= self.__vol <= 1007:
            return '//basket-05.wbbasket.ru'
        elif 1008 <= self.__vol <= 1061:
            return '//basket-06.wbbasket.ru'
        elif 1062 <= self.__vol <= 1115:
            return '//basket-07.wbbasket.ru'
        elif 1116 <= self.__vol <= 1169:
            return '//basket-08.wbbasket.ru'
        elif 1170 <= self.__vol <= 1313:
            return '//basket-09.wbbasket.ru'
        elif 1314 <= self.__vol <= 1601:
            return '//basket-10.wbbasket.ru'
        elif 1602 <= self.__vol <= 1655:
            return '//basket-11.wbbasket.ru'
        else:
            return '//basket-12.wbbasket.ru'

    @cached_property
    def img_url(self) -> str:
        return self.RAW_IMG_URL.format(
            self.__img_url_host,
            self.__vol,
            self.__part,
            self.product_id,
            self.DEFAULT_IMG_SIZE,
            self.DEFAULT_IMG_NUMBER,
        )

    @loguru_logger.catch(BaseException)
    async def download(self) -> b64:
        loguru_logger.info(
            f'request ("{self.img_url}") to download img' f' by product = {self.product_id}.'
        )
        async with ClientSession(
            timeout=ClientTimeout(total=DEFAULT_TIMEOUT), headers=get_fake_headers()
        ) as session, session.get(self.img_url) as response:
            downloaded_img: bytes = await response.read()
            return from_bytes_to_b64(downloaded_img)


class WbImgsDownloader(list[WbImgDownloader]):
    def __init__(self, product_ids: list[int]):
        super().__init__([WbImgDownloader(pid) for pid in product_ids])
