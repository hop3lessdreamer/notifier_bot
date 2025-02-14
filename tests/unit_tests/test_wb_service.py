import pytest
from core.services.wb import WbService
from core.exceptions import WbProductValidateError

def test_validate_product_url_valid():
    url = 'https://www.wildberries.ru/catalog/171235215/detail.aspx'
    expected_product_id = 171235215
    assert WbService.validate_product_url(url) == expected_product_id

def test_validate_product_url_invalid():
    with pytest.raises(WbProductValidateError):
        WbService.validate_product_url('https://www.ozon.ru/product/polaris-trimmer-dlya-volos-phc-1704-kol-vo-nasadok-1-1619434497/?avtc=1&avte=4&avts=1735392248')

def test_validate_product_url_no_product_id():
    with pytest.raises(WbProductValidateError):
        WbService.validate_product_url('https://example.com/catalog/qwerty')

def test_validate_product_url_empty():
    with pytest.raises(WbProductValidateError):
        WbService.validate_product_url('')
