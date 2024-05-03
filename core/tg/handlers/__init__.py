from core.tg.handlers.base_handler import BaseHandler
from core.tg.handlers.choose_action_handler import ChooseActionHandler
from core.tg.handlers.choose_marketplace import ReChooseMP
from core.tg.handlers.delete_subscriptions_handler import DeleteSubscriptionHandlers
from core.tg.handlers.menu import PickMenu
from core.tg.handlers.on_notify_handler import OnNotifyHandler
from core.tg.handlers.product_handler import ProductHandler
from core.tg.handlers.show_subscriptions_handler import ShowSubscriptionsHandlers
from core.tg.handlers.start_handler import StartHandler
from core.tg.handlers.subscription_existing_handler import SubscriptionExistingHandlers
from core.tg.handlers.subscription_handler import SubscriptionHandlers

HANDLERS: tuple[type[BaseHandler], ...] = (
    StartHandler,
    ChooseActionHandler,
    ReChooseMP,
    ProductHandler,
    SubscriptionHandlers,
    SubscriptionExistingHandlers,
    ShowSubscriptionsHandlers,
    DeleteSubscriptionHandlers,
    PickMenu,
    OnNotifyHandler,
)
