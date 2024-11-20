from dataclasses import dataclass
from decimal import Decimal
from typing import cast

from core.repositories.sub_product import ISubProductRepo
from core.repositories.subscription import ISubscriptionRepo
from core.schemas.product import Product
from core.schemas.sub_product import SubProduct, SubProductCollection
from core.schemas.user_product import UserProduct, UserProductAdd
from core.services.product import ProductService


@dataclass
class SubscriptionService:
    subscription_repo: ISubscriptionRepo
    sub_product_repo: ISubProductRepo
    product_service: ProductService

    async def subscribe(self, user_id: int, product: Product, threshold: Decimal) -> SubProduct:
        return SubProduct(
            await self._add_sub(
                UserProductAdd(UserID=user_id, ProductID=product.id, PriceThreshold=threshold),
                product,
            ),
            await self.product_service.get_product(product.id),
        )

    async def resubscribe(self, user_id: int, product_id: int, threshold: Decimal) -> SubProduct:
        sub: UserProduct = await self.subscription_repo.update_threshold(
            user_id, product_id, threshold
        )
        return SubProduct(sub, await self.product_service.get_product(product_id))

    async def delete_sub(self, user_id: int, product_id: int) -> SubProduct | None:
        sub: UserProduct = await self.subscription_repo.delete(user_id, product_id)
        if not sub.user_id or not sub.product_id:
            return None
        product: Product = cast(Product, await self.product_service.try_get_product(product_id))
        return SubProduct(sub, product)

    async def get_sub_by_user(
        self, user_id: int, limit: int = 100, offset: int = 0
    ) -> list[SubProduct]:
        return await self.sub_product_repo.get_by_user(user_id, limit, offset)

    async def get_all_subs(self) -> list[SubProduct]:
        return await self.sub_product_repo.get_all()

    async def sub_cnt_by_user(self, user_id: int) -> int:
        return await self.subscription_repo.get_cnt_by_user(user_id)

    async def get_sub_by_user_product(self, user_id: int, product_id: int) -> SubProduct | None:
        return await self.sub_product_repo.get_by_user_product(user_id, product_id)

    async def subscribe_to_price_reduction(self, user_id: int, product: Product) -> SubProduct:
        sub: UserProduct = await self._add_sub(
            UserProductAdd(UserID=user_id, ProductID=product.id, PriceThreshold=product.price),
            product,
        )
        return SubProduct(sub, await self.product_service.get_product(product.id))

    async def subscribe_to_price_reduction_for_exist(
        self, user_id: int, product: Product
    ) -> SubProduct:
        return await self.resubscribe(user_id, product.id, product.price)

    async def shift_forward_pos_by_sub_collection(
        self, sub_collection: SubProductCollection, user_id: int
    ) -> None:
        if sub_collection.is_cur_at_end:
            if sub_collection.has_more_sub_in_db:
                new_batch_subs: list[SubProduct] = await self.sub_product_repo.get_by_user(
                    user_id, limit=20, offset=sub_collection.subs_length
                )
                sub_collection.subs.extend(new_batch_subs)
                sub_collection.cur_pos += 1
            else:
                sub_collection.cur_pos = 0

        else:
            sub_collection.cur_pos += 1

        sub_collection.clear_cache()

    @staticmethod
    def shift_backward_pos_by_sub_collection(sub_collection: SubProductCollection) -> None:
        if sub_collection.is_cur_at_beginning:
            sub_collection.set_pos_to_last()
        else:
            sub_collection.cur_pos -= 1

        sub_collection.clear_cache()

    async def _add_sub(self, sub: UserProductAdd, product: Product) -> UserProduct:
        await self.product_service.add(product)
        return await self.subscription_repo.add(sub)
