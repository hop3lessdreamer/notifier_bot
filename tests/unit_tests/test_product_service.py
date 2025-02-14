from decimal import Decimal
import pytest
from sqlalchemy import insert

from core.services.product import ProductService
from core.value_objects.price_change import PriceChange
from db import db
from infrastructure.db.models.product import ProductModel
from infrastructure.db.repositories.product import ProductRepoImpl


@pytest.mark.asyncio
async def test_add(products):
    service = ProductService(ProductRepoImpl(db))
    prod1 = await service.add(products[0])

    assert prod1.price == products[0].price, 'incorrect product1 price!'
    assert prod1.img == products[0].img, 'incorrect product1 Img!'
    assert prod1.title == products[0].title, 'incorrect product1 Title!'


@pytest.mark.asyncio
async def test_add_existing_and_same_price(products):
    with db.session() as session:
        session.execute(insert(ProductModel).values(
            ID=products[1].id,
            Price=products[1].price,
            Img=products[1].img,
            Title=products[1].title,
            MPType=products[1].mp_type
        ))
        session.commit()

    service = ProductService(ProductRepoImpl(db))
    prod1 = await service.add(products[1])

    assert prod1.price == products[1].price, 'incorrect product1 price!'
    assert prod1.img == products[1].img, 'incorrect product1 Img!'
    assert prod1.title == products[1].title, 'incorrect product1 Title!'
    assert prod1.mp_type == products[1].mp_type, 'incorrect product1 MpType!'


@pytest.mark.asyncio
async def test_add_existing_and_not_same_price(products):
    with db.session() as session:
        session.execute(insert(ProductModel).values(
            ID=products[1].id,
            Price=products[1].price,
            Img=products[1].img,
            Title=products[1].title,
            MPType=products[1].mp_type
        ))
        session.commit()

    service = ProductService(ProductRepoImpl(db))
    products[1].price += 100
    prod1 = await service.add(products[1])

    assert prod1.price == products[1].price, 'incorrect product1 price!'
    assert prod1.img == products[1].img, 'incorrect product1 Img!'
    assert prod1.title == products[1].title, 'incorrect product1 Title!'
    assert prod1.mp_type == products[1].mp_type, 'incorrect product1 MpType!'


@pytest.mark.asyncio
async def test_update_prices(products):
    with db.session() as session:
        session.execute(insert(ProductModel).values(
            ID=products[1].id,
            Price=products[1].price,
            Img=products[1].img,
            Title=products[1].title,
            MPType=products[1].mp_type
        ))
        session.commit()

    service = ProductService(ProductRepoImpl(db))
    updated_prods = await service.update_prices({products[1].id: PriceChange(products[1].price, Decimal(2500))})

    assert updated_prods[0].price == Decimal(2500)


@pytest.mark.asyncio
async def test_try_get_not_existing_product(products):
    with db.session() as session:
        session.execute(insert(ProductModel).values(
            ID=products[1].id,
            Price=products[1].price,
            Img=products[1].img,
            Title=products[1].title,
            MPType=products[1].mp_type
        ))
        session.commit()

    service = ProductService(ProductRepoImpl(db))
    prod = await service.try_get_product(products[1].id)

    assert prod.id == products[1].id
    assert prod.img == products[1].img
    assert prod.title == products[1].title
    assert prod.price == products[1].price
    assert prod.mp_type == products[1].mp_type


@pytest.mark.asyncio
async def test_get_existing_product(products):
    with db.session() as session:
        session.execute(insert(ProductModel).values(
            ID=products[1].id,
            Price=products[1].price,
            Img=products[1].img,
            Title=products[1].title,
            MPType=products[1].mp_type
        ))
        session.commit()

    service = ProductService(ProductRepoImpl(db))
    prod = await service.get_product(products[1].id)

    assert prod.id == products[1].id
    assert prod.img == products[1].img
    assert prod.title == products[1].title
    assert prod.price == products[1].price
    assert prod.mp_type == products[1].mp_type


@pytest.mark.asyncio
@pytest.mark.xfail(raises=ValueError)
async def test_get_not_existing_product(products):
    service = ProductService(ProductRepoImpl(db))
    await service.get_product(products[1].id)


def test_validate_product():
    service = ProductService(ProductRepoImpl(db))
    prod_id1, _ = service.validate_product_id('123456')
    prod_id2, _ = service.validate_product_id('https://www.wildberries.ru/catalog/14131375/detail.aspx')
    prod_id3, _ = service.validate_product_id('werdsfsdf')

    assert prod_id1 == 123456
    assert prod_id2 == 14131375
    assert prod_id3 is None
