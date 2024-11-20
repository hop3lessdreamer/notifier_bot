import datetime
import pytest
from sqlalchemy import insert

from core.schemas.product import Product
from core.schemas.sub_product import SubProduct
from core.schemas.user_product import UserProduct, UserProductAdd
from core.services.product import ProductService
from core.services.subscription import SubscriptionService
from infrastructure.db.models.user_product import UserProductModel
from infrastructure.db.repositories.product import ProductRepoImpl
from infrastructure.db.repositories.sub_product import SubProductRepoImpl
from infrastructure.db.repositories.subscription import SubscriptionRepoImpl
from db import db


@pytest.mark.asyncio
async def test_add_sub_w_not_existing_prod(subs):
    service = SubscriptionService(
        SubscriptionRepoImpl(db),
        SubProductRepoImpl(db),
        ProductService(ProductRepoImpl(db))
    )
    sub, product, sub_add = subs[0]
    added_sub = await service._add_sub(sub_add, product)

    assert added_sub.user_id == sub.user_id
    assert added_sub.product_id == sub.product_id
    assert added_sub.price_threshold == sub.price_threshold


@pytest.mark.asyncio
async def test_add_sub_w_existing_prod(subs_w_existing_prods):
    service = SubscriptionService(
        SubscriptionRepoImpl(db),
        SubProductRepoImpl(db),
        ProductService(ProductRepoImpl(db))
    )
    sub, product, sub_add = subs_w_existing_prods[0]
    added_sub = await service._add_sub(sub_add, product)

    assert added_sub.user_id == sub.user_id
    assert added_sub.product_id == sub.product_id
    assert added_sub.price_threshold == sub.price_threshold


@pytest.mark.asyncio
async def test_del_sub(subs_w_existing_prods):
    service = SubscriptionService(
        SubscriptionRepoImpl(db),
        SubProductRepoImpl(db),
        ProductService(ProductRepoImpl(db))
    )
    sub, product, _ = subs_w_existing_prods[0]

    with db.session() as session:
        session.execute(
            insert(UserProductModel)
            .values(
                UserID=sub.user_id,
                ProductID=product.id,
                PriceThreshold=sub.price_threshold,
                Added=datetime.datetime.utcnow()
            )
        )
        session.commit()

    deleted = await service.delete_sub(sub.user_id, sub.product_id)

    assert deleted is not None
    assert deleted.subscription.user_id == sub.user_id
    assert deleted.subscription.product_id == sub.product_id
    assert deleted.subscription.price_threshold == sub.price_threshold


@pytest.mark.asyncio
async def test_get_sub_by_user(subs_already_added):
    service = SubscriptionService(
        SubscriptionRepoImpl(db),
        SubProductRepoImpl(db),
        ProductService(ProductRepoImpl(db))
    )
    user_id = subs_already_added[0][0].user_id
    sub1, prod1 = subs_already_added[0][0], subs_already_added[0][1]
    sub2, prod2 = subs_already_added[1][0], subs_already_added[1][1]
    sub3, prod3 = subs_already_added[2][0], subs_already_added[2][1]

    #   Возвращаются отсортированные по дате добавление - сначала послений добавленный
    subs: list[SubProduct] = await service.get_sub_by_user(user_id)

    assert sub1.user_id == subs[2].subscription.user_id
    assert sub1.product_id == subs[2].subscription.product_id
    assert sub1.price_threshold == subs[2].subscription.price_threshold

    assert sub2.user_id == subs[1].subscription.user_id
    assert sub2.product_id == subs[1].subscription.product_id
    assert sub2.price_threshold == subs[1].subscription.price_threshold

    assert sub3.user_id == subs[0].subscription.user_id
    assert sub3.product_id == subs[0].subscription.product_id
    assert sub3.price_threshold == subs[0].subscription.price_threshold


@pytest.mark.asyncio
async def test_get_all_subs(subs_already_added):
    service = SubscriptionService(
        SubscriptionRepoImpl(db),
        SubProductRepoImpl(db),
        ProductService(ProductRepoImpl(db))
    )
    sub1, prod1 = subs_already_added[0][0], subs_already_added[0][1]
    sub2, prod2 = subs_already_added[1][0], subs_already_added[1][1]
    sub3, prod3 = subs_already_added[2][0], subs_already_added[2][1]

    #   Возвращаются отсортированные по дате добавление - сначала послений добавленный
    subs: list[SubProduct] = await service.get_all_subs()

    assert sub1.user_id == subs[2].subscription.user_id
    assert sub1.product_id == subs[2].subscription.product_id
    assert sub1.price_threshold == subs[2].subscription.price_threshold

    assert sub2.user_id == subs[1].subscription.user_id
    assert sub2.product_id == subs[1].subscription.product_id
    assert sub2.price_threshold == subs[1].subscription.price_threshold

    assert sub3.user_id == subs[0].subscription.user_id
    assert sub3.product_id == subs[0].subscription.product_id
    assert sub3.price_threshold == subs[0].subscription.price_threshold


@pytest.mark.asyncio
async def test_sub_cnt_by_user(subs_already_added):
    service = SubscriptionService(
        SubscriptionRepoImpl(db),
        SubProductRepoImpl(db),
        ProductService(ProductRepoImpl(db))
    )
    user_id = subs_already_added[0][0].user_id

    cnt = await service.sub_cnt_by_user(user_id)

    assert cnt == len(subs_already_added)


@pytest.mark.asyncio
async def test_get_sub_by_user_product(subs_already_added):
    service = SubscriptionService(
        SubscriptionRepoImpl(db),
        SubProductRepoImpl(db),
        ProductService(ProductRepoImpl(db))
    )
    user_id = subs_already_added[0][0].user_id
    sub1, prod1 = subs_already_added[0][0], subs_already_added[0][1]

    subprod = await service.get_sub_by_user_product(user_id, product_id=prod1.id)

    assert sub1.user_id == subprod.subscription.user_id
    assert sub1.product_id == subprod.subscription.product_id
    assert sub1.price_threshold == subprod.subscription.price_threshold


@pytest.mark.asyncio
async def test_subscribe_to_price_reduction(subs_w_existing_prods):
    service = SubscriptionService(
        SubscriptionRepoImpl(db),
        SubProductRepoImpl(db),
        ProductService(ProductRepoImpl(db))
    )
    user_id = subs_w_existing_prods[0][0].user_id
    product: Product = subs_w_existing_prods[0][1]

    sub: SubProduct = await service.subscribe_to_price_reduction(user_id, product)

    assert sub.subscription.product_id == product.id
    assert sub.subscription.user_id == user_id
    assert sub.subscription.price_threshold == product.price


@pytest.mark.asyncio
async def test_subscribe_to_price_reduction_for_exist(subs_already_added):
    service = SubscriptionService(
        SubscriptionRepoImpl(db),
        SubProductRepoImpl(db),
        ProductService(ProductRepoImpl(db))
    )
    user_id = subs_already_added[0][0].user_id
    product: Product = subs_already_added[0][1]
    existing_sub: UserProduct = subs_already_added[0][0]

    assert existing_sub.price_threshold != product.price

    sub: SubProduct = await service.subscribe_to_price_reduction_for_exist(user_id, product)

    assert sub.subscription.product_id == product.id
    assert sub.subscription.user_id == user_id
    assert sub.subscription.price_threshold == product.price


@pytest.mark.asyncio
async def test_subscribe(subs_w_existing_prods):
    service = SubscriptionService(
        SubscriptionRepoImpl(db),
        SubProductRepoImpl(db),
        ProductService(ProductRepoImpl(db))
    )
    user_id = subs_w_existing_prods[0][0].user_id
    product: Product = subs_w_existing_prods[0][1]
    userprod_add: UserProductAdd = subs_w_existing_prods[0][2]

    sub: SubProduct = await service.subscribe(user_id, product, userprod_add.price_threshold)

    assert sub.subscription.product_id == product.id
    assert sub.subscription.user_id == user_id
    assert sub.subscription.price_threshold == userprod_add.price_threshold


@pytest.mark.asyncio
async def test_resub(subs_already_added):
    service = SubscriptionService(
        SubscriptionRepoImpl(db),
        SubProductRepoImpl(db),
        ProductService(ProductRepoImpl(db))
    )
    user_id = subs_already_added[0][0].user_id
    product: Product = subs_already_added[0][1]
    existing_sub: UserProduct = subs_already_added[0][0]

    assert existing_sub.price_threshold != product.price

    sub: SubProduct = await service.resubscribe(user_id, product.id, product.price)

    assert sub.subscription.product_id == product.id
    assert sub.subscription.user_id == user_id
    assert sub.subscription.price_threshold == product.price
