from dataclasses import dataclass

from core.repositories.subscription import ISubscriptionRepo
from core.schemas.product import Product
from core.schemas.user_product import UserProduct, UserProductAdd
from core.services.product import ProductService


@dataclass
class SubscriptionService:
    subscription_repo: ISubscriptionRepo
    product_service: ProductService

    async def add_sub(self, sub: UserProductAdd, product: Product) -> UserProduct:
        await self.product_service.add_if_not_exists(product)
        return await self.subscription_repo.add(sub)

    async def delete_sub(self, user_id: int, product_id: int) -> None:
        sub: UserProduct | None = await self.subscription_repo.get(user_id, product_id)
        if not sub:
            return
        await self.subscription_repo.delete(user_id, product_id)
