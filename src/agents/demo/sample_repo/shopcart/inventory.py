"""Stock levels per SKU."""

STOCK = {"BOOK-001": 12, "PEN-010": 300, "BAG-100": 4, "LAMP-200": 0}


def in_stock(sku: str, qty: int = 1) -> bool:
    """True when at least `qty` units of `sku` are available."""
    return STOCK.get(sku, 0) >= qty
