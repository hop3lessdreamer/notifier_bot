from core.wb.wb_parser import WbParser, WbProduct
from db.queries import DBQueries, Subscription


async def check_product_prices(db: DBQueries):
    """ Handler that collects all products and then checks prices for changes """

    subs: list[Subscription] = await db.get_all_subscriptions()
    products_ids: list[int] = [sub.product.id for sub in subs]
    old_wb_products: dict[int, WbProduct] = {
        sub.product.id: WbProduct(
            sub.product.id,
            sub.product.title,
            sub.product.price
        )
        for sub in subs
    }
    new_wb_products: dict[int, WbProduct] = await WbParser(products_ids).get_wb_products()

    changing_prices: dict[int, float] = {}
    for pid, new_product in new_wb_products.items():
        old_product: WbProduct = old_wb_products.get(pid)
        if old_product.price != new_product.price:
            changing_prices[pid] = new_product.price

    if not changing_prices:
        return

    for pid, changing_price in changing_prices.items():
        pass
