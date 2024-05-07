from collections import defaultdict
from decimal import Decimal
from typing import NamedTuple

from core.tg.files import transferring_file
from core.tg.keyboards import OnSubNotifyKeyboard
from core.tg.message_texts import Messages
from core.tg.tg_dispatcher import TgDispatcher
from core.wb.wb_parser import WbParser, WbProduct
from db.queries import DBQueries, Subscription
from logger import log_node, logger
from schemas.product import Product
from schemas.user import User
from utils.transform_types import get_decimal
from utils.types import ProductID, UserID


class PriceChange(NamedTuple):
    old: Decimal
    new: Decimal


@log_node('checking product prices!')
async def check_product_prices(db: DBQueries, dp: TgDispatcher) -> dict[UserID, list[Product]]:
    """Handler that collects all products and then checks prices for changes"""

    subs: list[Subscription] = await db.get_all_subscriptions()
    old_products_by_pid: dict[ProductID, Product] = {}
    subs_by_pid: dict[ProductID, list[Subscription]] = defaultdict(list)
    sub_by_user: dict[UserID, list[Subscription]] = defaultdict(list)
    for sub in subs:
        old_products_by_pid[sub.product.id] = sub.product
        subs_by_pid[sub.product.id].append(sub)
        sub_by_user[sub.user_product.user_id].append(sub)

    new_wb_products: dict[ProductID, WbProduct] = await WbParser(
        list(old_products_by_pid.keys())
    ).get_wb_products()

    changing_prices: dict[ProductID, PriceChange] = {}
    for pid, new_product in new_wb_products.items():
        old_product: Product | None = old_products_by_pid.get(pid)

        if old_product is None:
            logger.error('new product from response was not found in db!')
            continue
        if old_product.price != new_product.price:
            new_price: Decimal | None = get_decimal(new_product.price, 2)
            if new_price is None:
                raise ValueError('Ошибка валидации цены на товар!')
            changing_prices[pid] = PriceChange(old_product.price, new_price)

    if not changing_prices:
        logger.info('No change in prices.')
        return {}

    send_notifications: dict[UserID, list[Product]] = defaultdict(list)
    for pid, price_change in changing_prices.items():
        subs_w_changing_price: list[Subscription] | None = subs_by_pid.get(pid)
        if subs_w_changing_price is None:
            logger.error('new product from response was not found in db!')
            continue
        for sub in subs_w_changing_price:
            new_price = get_decimal(price_change.new, 2)
            if new_price is None:
                raise ValueError('Ошибка валидации цены на товар!')
            if new_price < sub.user_product.price_threshold:
                sub.product.price = new_price
                send_notifications[sub.user_product.user_id].append(sub.product)

    logger.info(f'products that changed prices:\n{str(changing_prices)}')
    await db.change_products_prices({pid: change.new for pid, change in changing_prices.items()})

    logger.info(f'users that will receive notification: {str(send_notifications.keys())}')
    for user_id, products in send_notifications.items():
        user: User = await db.get_user(user_id)
        for product in products:
            with transferring_file(product.img) as product_img:
                await dp.storage.write_wb_product(
                    user.id, user.chat_id, new_wb_products[product.id]
                )
                await dp.bot.send_photo(
                    user.chat_id,
                    photo=product_img,
                    caption=Messages.sub_notification(product),
                    reply_markup=OnSubNotifyKeyboard(),
                )
            await db.delete_subscription(user.id, product.id)

    return send_notifications
