""" Message texts for bot """

import typing

from _decimal import Decimal
from aiogram.utils import markdown as fmt

from core.schemas.product import Product
from core.schemas.sub_product import SubProduct, SubProductCollection
from core.wb import form_url_from_product_id


class Messages:
    HELLO: str = fmt.text(
        'Приветствую вас! Я бот для уведомления о снижении цен на товары маркетплейса ',
        fmt.hlink('Wildberries', 'https://www.wildberries.ru/'),
        '.',
        sep='',
    )
    CHOSE_MARKET_PLACE = 'Выберете маркетплейс'
    CHOSE_ACTION = 'Выберете действие'
    PRINT_PRODUCT = 'Введите ссылку на товар или артикул'
    INVALID_PRINTED_PRODUCT = 'Неверно указан товар. Попробуйте еще раз!'
    PRINT_THRESHOLD = 'Введите порог цены для уведомления.'
    PRINT_THRESHOLD_IN_PERCENT = 'Введите процент снижения цены для уведомления.'

    @staticmethod
    def current_product_price(product: Product) -> str:
        return typing.cast(
            str,
            fmt.text(
                'Текущая цена на ',
                fmt.hbold(product.title),
                f' - {product.price} (без учета пользовательских скидок).',
                sep='',
            ),
        )

    @staticmethod
    def current_product_price_w_exist_subscription_wo_thr(subscription: SubProduct) -> str:
        return typing.cast(
            str,
            fmt.text(
                'Текущая цена на ',
                fmt.hbold(f'"{subscription.product.title}"'),
                f' - {subscription.product.price} (без учета пользовательских скидок).\n',
                'Товар уже добавлен в отслеживаемые, вам придет уведомление о снижении цены.',
                sep='',
            ),
        )

    @staticmethod
    def current_product_price_w_exist_subscription_w_thr(subscription: SubProduct) -> str:
        return typing.cast(
            str,
            fmt.text(
                'Текущая цена на ',
                fmt.hbold(f'"{subscription.product.title}"'),
                f' - {subscription.product.price} (без учета пользовательских скидок).\n',
                f'Товар уже добавлен в отслеживаемые,'
                f' вам придет уведомление когда цена станет - '
                f'{subscription.subscription.price_threshold}.',
                sep='',
            ),
        )

    @staticmethod
    def product_added(product_title: str) -> str:
        return typing.cast(
            str,
            fmt.text(
                'Товар ',
                fmt.hbold(f'"{product_title}"'),
                ' добавлен в отслеживаемые.',
                '\nБот уведомит вас при снижении цены.',
                sep='',
            ),
        )

    @staticmethod
    def product_added_yet_wo_threshold(product_id: int) -> str:
        return typing.cast(
            str,
            fmt.text(
                'Товар ',
                fmt.hlink(str(product_id), form_url_from_product_id(product_id)),
                ' уже добавлен в отслеживаемые.',
                ' Бот уведомит вас при снижении цены.',
                sep='',
            ),
        )

    @staticmethod
    def product_added_w_threshold(product: Product, threshold: Decimal) -> str:
        return typing.cast(
            str,
            fmt.text(
                'Товар ',
                fmt.hbold(f'"{product.title}"'),
                ' добавлен в отслеживаемые.',
                f'\nБот уведомит вас при снижении цены до значения - {str(threshold)}.',
                sep='',
            ),
        )

    @staticmethod
    def product_added_yet_w_threshold(product_id: int, threshold: Decimal) -> str:
        return typing.cast(
            str,
            fmt.text(
                'Товар ',
                fmt.hlink(str(product_id), form_url_from_product_id(product_id)),
                ' уже добавлен в отслеживаемые.',
                f' Бот уведомит вас при снижении цены до значения - {str(threshold)}.',
                sep='',
            ),
        )

    @staticmethod
    def product_added_w_threshold_in_percent(
        product: Product, price_threshold: float | Decimal
    ) -> str:
        return typing.cast(
            str,
            fmt.text(
                'Товар ',
                fmt.hbold(f'"{product.title}"'),
                ' добавлен в отслеживаемые.',
                f'\nБот уведомит вас при снижении цены до значения -' f' {str(price_threshold)}.',
                sep='',
            ),
        )

    @staticmethod
    def product_deleted(product_id: int) -> str:
        return typing.cast(
            str,
            fmt.text(
                'Товар ',
                fmt.hlink(str(product_id), form_url_from_product_id(product_id)),
                ' удален из отслеживаемых',
                sep='',
            ),
        )

    @staticmethod
    def product_deleted_not_found(product_id: int) -> str:
        return typing.cast(
            str,
            fmt.text(
                'Товар ',
                fmt.hlink(str(product_id), form_url_from_product_id(product_id)),
                ' не найден в списке отслеживаемых',
                sep='',
            ),
        )

    @staticmethod
    def subscription(subprod_collection: SubProductCollection) -> str:
        subprod: SubProduct | None = subprod_collection.sub_by_cur_pos
        if not subprod:
            return Messages.subscriptions_not_found()

        if subprod.subscription.price_threshold == subprod.product.price:
            return typing.cast(
                str,
                fmt.text(
                    f'Отслеживаемый товар '
                    f'{abs(subprod_collection.cur_pos) + 1}/{subprod_collection.total_sub_cnt}\n',
                    fmt.hbold(f'"{subprod.product.title}"'),
                    ' - ',
                    f'уведомление придет при снижении цены ' f'{str(subprod.product.price)}',
                    sep='',
                ),
            )

        return typing.cast(
            str,
            fmt.text(
                f'Отслеживаемый товар '
                f'{abs(subprod_collection.cur_pos) + 1}/{subprod_collection.total_sub_cnt}\n',
                fmt.hbold(f'"{subprod.product.title}"'),
                ' - ',
                f'уведомление придет при снижении цены до '
                f'{str(subprod.subscription.price_threshold)}',
                sep='',
            ),
        )

    @staticmethod
    def subscriptions_not_found() -> str:
        return typing.cast(str, fmt.text('У вас нет отслеживаемых товаров.', sep=''))

    @staticmethod
    def subscriptions_not_found_after_deletion() -> str:
        return typing.cast(
            str, fmt.text('У вас не осталось отслеживаемых товаром после удаления.', sep='')
        )

    @staticmethod
    def info_about_deletion(deleted_sub: SubProduct) -> str:
        return typing.cast(
            str,
            fmt.text(
                'Товар ',
                fmt.hbold(f'"{deleted_sub.product.title}"'),
                ' удален из отслеживаемых.',
                sep='',
            ),
        )

    @staticmethod
    def sub_notification(product: Product) -> str:
        return typing.cast(
            str,
            fmt.text(
                'Цена на товар ',
                f'"{fmt.hlink(str(product.title), form_url_from_product_id(product.id))}"',
                'стала ',
                fmt.hbold(f'{product.price}!'),
                sep='',
            ),
        )
