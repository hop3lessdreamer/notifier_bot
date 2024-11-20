from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class PriceChange:
    old: Decimal
    new: Decimal
