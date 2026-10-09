"""Product catalogue: SKU to unit price in paise (1 rupee = 100 paise)."""

PRICES = {
    "BOOK-001": 49900,
    "PEN-010": 2500,
    "BAG-100": 129900,
    "LAMP-200": 89900,
}


def unit_price(sku: str) -> int:
    """Return the unit price of `sku` in paise."""
    if sku not in PRICES:
        raise KeyError(f"unknown SKU {sku}")
    return PRICES[sku]
