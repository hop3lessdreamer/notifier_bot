from aiogram import Router

from core.tg.handlers import (
    choose_action_handler,
    delete_subscriptions_handler,
    menu,
    on_notify_handler,
    product_handler,
    show_subscriptions_handler,
    start_handler,
    subscription_existing_handler,
    subscription_handler,
)


def get_main_router() -> Router:
    router = Router()
    router.include_router(choose_action_handler.router)
    router.include_router(delete_subscriptions_handler.router)
    router.include_router(menu.router)
    router.include_router(on_notify_handler.router)
    router.include_router(product_handler.router)
    router.include_router(show_subscriptions_handler.router)
    router.include_router(start_handler.router)
    router.include_router(subscription_existing_handler.router)
    router.include_router(subscription_handler.router)
    return router
