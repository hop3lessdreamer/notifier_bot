from collections import defaultdict
from dataclasses import dataclass

from aiogram import Bot
from aiogram.fsm.storage.memory import StorageKey

from core.schemas.product import Product
from core.schemas.sub_product import SubProduct
from core.schemas.user import User
from core.services.subscription import SubscriptionService
from core.services.user import UserService
from core.services.wb import WbService
from core.tg.files import transferring_file2
from core.tg.keyboards import OnSubNotifyKeyboard
from core.tg.message_texts import Messages
from core.tg.tg_dispatcher import TgDispatcher
from core.value_objects.price_change import PriceChange
from logger import logger as loguru_logger
from utils.types import ProductID, UserID


@dataclass
class PriceCheckerService:
    tg_disp: TgDispatcher
    bot: Bot
    user_service: UserService
    sub_service: SubscriptionService
    wb_service: WbService

    async def ping(self) -> None:  # noqa
        from datetime import datetime

        print(f'ping - {datetime.now()}')  # noqa: T201

    async def wb_price_check(self) -> None:  # noqa
        loguru_logger.info('wb price check')

        subs: list[SubProduct] = await self.sub_service.get_all_subs()

        old_products: dict[ProductID, Product] = {}
        subs_by_pid: dict[ProductID, list[SubProduct]] = defaultdict(list)
        for sub in subs:
            old_products[sub.product.id] = sub.product
            subs_by_pid[sub.product.id].append(sub)

        new_products: dict[ProductID, Product] = await self.wb_service.get_prods_by_prod_id(
            product_ids=list(old_products.keys())
        )

        changing_prices: dict[ProductID, PriceChange] = self._find_changing_prices(
            new_products, old_products
        )
        if not changing_prices:
            loguru_logger.info('No change in prices.')
            return

        await self.sub_service.product_service.update_prices(changing_prices)

        who_to_notify: dict[UserID, list[Product]] = self._find_who_to_notify(
            changing_prices, subs_by_pid
        )
        for user_id, products in who_to_notify.items():
            user: User = await self.user_service.get_user(user_id)
            for product in products:
                with transferring_file2(product.img) as product_img:
                    await self.tg_disp.storage.write_product(
                        StorageKey(self.bot.id, user.chat_id, user.id), new_products[product.id]
                    )
                    await self.bot.send_photo(
                        user.chat_id,
                        photo=product_img,
                        caption=Messages.sub_notification(product),
                        reply_markup=OnSubNotifyKeyboard(),
                    )
                await self.sub_service.delete_sub(user.id, product.id)

    def _find_changing_prices(
        self, new_products: dict[ProductID, Product], old_products: dict[ProductID, Product]
    ) -> dict[ProductID, PriceChange]:
        changing_prices: dict[ProductID, PriceChange] = {}
        for pid, new_product in new_products.items():
            old_product: Product | None = old_products.get(pid)
            if old_product is None:
                loguru_logger.error('new product from response was not found in db!')
                continue
            if old_product.price != new_product.price:
                changing_prices[pid] = PriceChange(old_product.price, new_product.price)

        loguru_logger.info(f'products that changed prices:\n{str(changing_prices)}')
        return changing_prices

    def _find_who_to_notify(
        self,
        changing_prices: dict[ProductID, PriceChange],
        subs_by_pid: dict[ProductID, list[SubProduct]],
    ) -> dict[UserID, list[Product]]:
        who_to_notify: dict[UserID, list[Product]] = defaultdict(list)
        for pid, price_change in changing_prices.items():
            subs_w_changing_price: list[SubProduct] | None = subs_by_pid.get(pid)
            if subs_w_changing_price is None:
                loguru_logger.error('new product from response was not found in db!')
                continue
            for sub in subs_w_changing_price:
                if price_change.new < sub.subscription.price_threshold:
                    sub.product.price = price_change.new
                    who_to_notify[sub.subscription.user_id].append(sub.product)

        loguru_logger.info(f'users that will receive notification: {str(who_to_notify.keys())}')
        return who_to_notify
