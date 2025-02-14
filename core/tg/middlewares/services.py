from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from core.services.ozon import OzonService
from core.services.product import ProductService
from core.services.subscription import SubscriptionService
from core.services.user import UserService
from core.services.wb import WbProductImgService, WbProductInfoService, WbService
from db import Database
from infrastructure.db.repositories.product import ProductRepoImpl
from infrastructure.db.repositories.sub_product import SubProductRepoImpl
from infrastructure.db.repositories.subscription import SubscriptionRepoImpl
from infrastructure.db.repositories.user import UserRepoImpl


@dataclass
class ServicesMiddleware(BaseMiddleware):
    db: Database

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user_service = UserService(UserRepoImpl(self.db))
        product_service = ProductService(ProductRepoImpl(self.db))

        subscription_service = SubscriptionService(
            subscription_repo=SubscriptionRepoImpl(self.db),  # noqa
            sub_product_repo=SubProductRepoImpl(self.db),
            product_service=product_service,
        )

        wb_service = WbService(
            wb_img_service=WbProductImgService(), wb_prod_info_service=WbProductInfoService()
        )
        ozon_service = OzonService()

        data.update(
            user_service=user_service,
            product_service=product_service,
            sub_service=subscription_service,
            wb_service=wb_service,
            ozon_service=ozon_service,
        )

        return await handler(event, data)
