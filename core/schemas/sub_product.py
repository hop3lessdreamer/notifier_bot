from dataclasses import dataclass

from core.schemas.product import Product
from core.schemas.user_product import UserProduct


@dataclass
class SubProduct:
    subscription: UserProduct
    product: Product
