"""Discount codes and how they reduce a cart subtotal."""

# code -> percent off
DISCOUNT_CODES = {
    "WELCOME10": 10,
    "STUDENT15": 15,
}


def apply_discount(subtotal: int, code: str | None) -> int:
    """Return the subtotal after applying discount `code` (paise).

    An unknown or empty code leaves the subtotal unchanged.
    """
    if not code:
        return subtotal
    percent = DISCOUNT_CODES.get(code.upper())
    if percent is None:
        return subtotal
    return subtotal - (subtotal * percent) // 100
