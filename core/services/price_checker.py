from collections import defaultdict
from dataclasses import dataclass

from aiogram import Bot
from aiogram.fsm.storage.memory import StorageKey
from loguru import logger

from core.schemas.product import MPType, Product
from core.schemas.sub_product import SubProduct
from core.schemas.user import User
from core.services.ozon import OzonService
from core.services.subscription import SubscriptionService
from core.services.user import UserService
from core.services.wb import WbService
from core.tg.files import transferring_file
from core.tg.keyboards import OnSubNotifyKeyboard
from core.tg.message_texts import Messages
from core.tg.tg_dispatcher import TgDispatcher
from core.value_objects.price_change import PriceChange
from utils.types import ProductID, UserID


@dataclass
class PriceCheckerService:
    tg_disp: TgDispatcher
    bot: Bot
    user_service: UserService
    sub_service: SubscriptionService
    wb_service: WbService
    ozon_service: OzonService

    async def check_prod_prices(self) -> None:  # noqa
        logger.info('\nChecking prices...')

        subs: list[SubProduct] = await self.sub_service.get_all_subs()
        old_wb_prods, old_ozon_prods, subs_by_pid = self._split_product_by_mp_type(subs)
        new_wb_prods, new_ozon_prods = await self._find_new_products_from_mp(
            old_wb_prods, old_ozon_prods
        )

        #   combine old_prods and new_prods from different MP
        old_prods, new_prods = {}, {}
        old_prods.update(old_wb_prods)
        old_prods.update(old_ozon_prods)
        new_prods.update(new_wb_prods)
        new_prods.update(new_ozon_prods)

        changing_prices: dict[ProductID, PriceChange] = self._find_changing_prices(
            new_prods, old_prods
        )
        if not changing_prices:
            logger.info('No change in prices.')
            return

        await self.sub_service.product_service.update_prices(changing_prices)

        who_to_notify: dict[UserID, list[Product]] = self._find_who_to_notify(
            changing_prices, subs_by_pid
        )
        for user_id, products in who_to_notify.items():
            user: User = await self.user_service.get_user(user_id)
            for product in products:
                with transferring_file(product.img) as product_img:
                    await self.tg_disp.storage.write_product(
                        StorageKey(self.bot.id, user.chat_id, user.id), new_prods[product.id]
                    )
                    await self.bot.send_photo(
                        user.chat_id,
                        photo=product_img,
                        caption=Messages.sub_notification(product),
                        reply_markup=OnSubNotifyKeyboard(),
                    )
                await self.sub_service.delete_sub(user.id, product.id)

    def _split_product_by_mp_type(
        self, sub_products: list[SubProduct]
    ) -> tuple[
        dict[ProductID, Product], dict[ProductID, Product], dict[ProductID, list[SubProduct]]
    ]:
        wb_prods: dict[ProductID, Product] = {}
        ozon_prods: dict[ProductID, Product] = {}
        sub_by_pid: dict[ProductID, list[SubProduct]] = defaultdict(list)
        for sub in sub_products:
            if sub.product.mp_type == MPType.WB:
                wb_prods[sub.product.id] = sub.product
            elif sub.product.mp_type == MPType.OZON:
                ozon_prods[sub.product.id] = sub.product
            else:
                raise BaseException(f'Wrong MpType - {sub.product.mp_type}')
            sub_by_pid[sub.product.id].append(sub)
        return wb_prods, ozon_prods, sub_by_pid

    async def _find_new_products_from_mp(
        self, old_wb_prods: dict[ProductID, Product], old_ozon_prods: dict[ProductID, Product]
    ) -> tuple[dict[ProductID, Product], dict[ProductID, Product]]:
        logger.debug(f'old_wb_prods:\n{old_wb_prods}\n')
        logger.debug(f'old_ozon_prods:\n{old_ozon_prods}\n')
        new_wb_prods: dict[ProductID, Product] = await self.wb_service.get_prods_by_prod_id(
            product_ids=list(old_wb_prods.keys())
        )
        new_ozon_prods: dict[ProductID, Product] = await self.ozon_service.try_get_products(
            products_ids=list(old_ozon_prods.keys())
        )
        logger.debug(f'new_wb_prods:\n{new_wb_prods}\n')
        logger.debug(f'new_ozon_prods:\n{new_ozon_prods}\n')
        return new_wb_prods, new_ozon_prods

    def _find_changing_prices(
        self, new_products: dict[ProductID, Product], old_products: dict[ProductID, Product]
    ) -> dict[ProductID, PriceChange]:
        changing_prices: dict[ProductID, PriceChange] = {}
        for pid, new_product in new_products.items():
            old_product: Product | None = old_products.get(pid)
            if old_product is None:
                logger.error('new product from response was not found in db!')
                continue
            logger.info(f'old_product.price={old_product.price}')
            logger.info(f'new_product.price={new_product.price}')
            if old_product.price != new_product.price:
                changing_prices[pid] = PriceChange(old_product.price, new_product.price)

        logger.info(f'products that changed prices:\n{str(changing_prices)}')
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
                logger.error('new product from response was not found in db!')
                continue
            for sub in subs_w_changing_price:
                if price_change.new < sub.subscription.price_threshold:
                    sub.product.price = price_change.new
                    who_to_notify[sub.subscription.user_id].append(sub.product)

        logger.info(f'users that will receive notification: {str(who_to_notify.keys())}')
        return who_to_notify
