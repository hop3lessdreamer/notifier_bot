import pytest

from core.schemas.product import Product
from core.services.product import ProductService
from core.services.subscription import SubscriptionService
from db import db
from core.services.price_checker import PriceCheckerService
from core.services.user import UserService
from infrastructure.db.repositories.product import ProductRepoImpl
from infrastructure.db.repositories.sub_product import SubProductRepoImpl
from infrastructure.db.repositories.subscription import SubscriptionRepoImpl
from infrastructure.db.repositories.user import UserRepoImpl
from utils.types import ProductID


def test_find_changing_prices(mock_tg_disp, mock_bot, mock_wb_service, old_new_prods):
    service = PriceCheckerService(
        tg_disp=mock_tg_disp,
        bot=mock_bot,
        user_service=UserService(UserRepoImpl(db)),
        sub_service=SubscriptionService(
            SubscriptionRepoImpl(db),
            SubProductRepoImpl(db),
            ProductService(ProductRepoImpl(db))
        ),
        wb_service=mock_wb_service
    )

    changing_prices = service._find_changing_prices(new_products=old_new_prods[1], old_products=old_new_prods[0])

    for p in changing_prices:
        assert changing_prices[p].old == old_new_prods[0][p].price
        assert changing_prices[p].new == old_new_prods[1][p].price


def test_find_who_to_notify(mock_tg_disp, mock_bot, mock_wb_service, changing_prods, subs_already_added_by_pid):
    service = PriceCheckerService(
        tg_disp=mock_tg_disp,
        bot=mock_bot,
        user_service=UserService(UserRepoImpl(db)),
        sub_service=SubscriptionService(
            SubscriptionRepoImpl(db),
            SubProductRepoImpl(db),
            ProductService(ProductRepoImpl(db))
        ),
        wb_service=mock_wb_service
    )

    who_notify = service._find_who_to_notify(changing_prods, subs_already_added_by_pid)

    for user_id in who_notify:
        pass
        # assert user_id ==
