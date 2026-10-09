"""The cart: line items, subtotal and the checkout total."""

from shopcart.catalog import unit_price
from shopcart.pricing import apply_discount
from shopcart.tax import compute_tax


class Cart:
    """A shopping cart holding SKU quantities."""

    def __init__(self) -> None:
        self.items: dict[str, int] = {}

    def add(self, sku: str, qty: int = 1) -> None:
        """Add `qty` units of `sku`."""
        if qty <= 0:
            raise ValueError("quantity must be positive")
        unit_price(sku)  # validates the SKU
        self.items[sku] = self.items.get(sku, 0) + qty

    def remove(self, sku: str) -> None:
        """Remove `sku` entirely."""
        self.items.pop(sku, None)

    def subtotal(self) -> int:
        """Sum of unit price x quantity, in paise."""
        return sum(unit_price(sku) * qty for sku, qty in self.items.items())

    def total(self, code: str | None = None, region: str = "IN") -> int:
        """Checkout total: discount first, then tax on the discounted amount."""
        discounted = apply_discount(self.subtotal(), code)
        return discounted + compute_tax(discounted, region)
