from faststream import FastStream
from faststream.rabbit import RabbitBroker

from config import bot_config
from core.services.ozon import OzonService
from core.services.price_checker import PriceCheckerService
from core.services.product import ProductService
from core.services.subscription import SubscriptionService
from core.services.user import UserService
from core.services.wb import WbProductImgService, WbProductInfoService, WbService
from core.tg.bot import bot
from core.tg.tg_dispatcher import tg_disp
from db import db
from infrastructure.db.repositories.product import ProductRepoImpl
from infrastructure.db.repositories.sub_product import SubProductRepoImpl
from infrastructure.db.repositories.subscription import SubscriptionRepoImpl
from infrastructure.db.repositories.user import UserRepoImpl

broker = RabbitBroker(
    f'amqp://{bot_config.RABBIT_LOGIN}:{bot_config.RABBIT_PASS}@{bot_config.RABBIT_HOST}:5672/'
)
faststream_app = FastStream(broker)


@faststream_app.on_startup
async def on_startup_faststream() -> None:
    await broker.connect()


@faststream_app.on_shutdown
async def on_shutdown_faststream() -> None:
    await broker.close()


@broker.subscriber('price-check')
async def check_wb_price() -> None:
    price_checker = PriceCheckerService(
        tg_disp,
        bot,
        UserService(UserRepoImpl(db)),
        SubscriptionService(
            SubscriptionRepoImpl(db),
            SubProductRepoImpl(db),
            ProductService(ProductRepoImpl(db)),  # noqa
        ),
        WbService(WbProductImgService(), WbProductInfoService()),
        OzonService(),
    )
    await price_checker.check_prod_prices()  # noqa
