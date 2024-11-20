from dataclasses import dataclass, field
from functools import cached_property

from core.schemas.product import Product
from core.schemas.user_product import UserProduct


@dataclass
class SubProduct:
    subscription: UserProduct
    product: Product


@dataclass
class SubProductCollection:
    subs: list[SubProduct] = field(default_factory=list)
    total_sub_cnt: int = 0
    cur_pos: int = 0

    @cached_property
    def empty(self) -> bool:
        return not self.subs

    @cached_property
    def subs_length(self) -> int:
        return len(self.subs)

    @cached_property
    def first_sub(self) -> SubProduct | None:
        if self.empty:
            return None
        return self.subs[0]

    @cached_property
    def sub_by_cur_pos(self) -> SubProduct:
        try:
            return self.subs[self.cur_pos]
        except KeyError as ex:
            raise KeyError(f'subs - {self.subs}\ncur_pos - {self.cur_pos}') from ex

    @cached_property
    def prod_by_cur_pos(self) -> Product:
        if not self.sub_by_cur_pos or not self.sub_by_cur_pos.product:
            raise ValueError(
                f'Не удалось получить товар! (cur = {self.cur_pos}, subs = {self.subs})'
            )
        return self.sub_by_cur_pos.product

    @cached_property
    def has_more_sub_in_db(self) -> bool:
        return self.subs_length < self.total_sub_cnt

    @cached_property
    def is_cur_at_end(self) -> bool:
        return self.cur_pos == (self.subs_length - 1)

    @cached_property
    def is_cur_at_beginning(self) -> bool:
        return self.cur_pos == (self.subs_length - 1)

    def __pos__(self) -> None:
        self.cur_pos += 1

    def __repr__(self) -> str:
        subs_repr: str = '\n'.join(
            [f'pos = {str(i)} >> {sub.__repr__()}' for i, sub in enumerate(self.subs)]
        )
        return f'SubscriptionInfo:\n' f'cur_pos = {self.cur_pos}\n' f'subs:\n{subs_repr}\n'

    def set_pos_to_last(self) -> None:
        self.cur_pos = self.subs_length - 1

    def del_sub_by_cur_pos(self) -> SubProduct:
        deleted_sub: SubProduct = self.subs.pop(self.cur_pos)
        self.total_sub_cnt -= 1
        self.clear_cache()

        return deleted_sub

    def clear_cache(self) -> None:
        self.__dict__.pop('empty', None)
        self.__dict__.pop('subs_length', None)
        self.__dict__.pop('first_sub', None)
        self.__dict__.pop('sub_by_cur_pos', None)
        self.__dict__.pop('wb_prod_from_sub_by_cur_pos', None)
