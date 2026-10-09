"""GST on the discounted amount."""

GST_RATE_PERCENT = {"IN": 18, "EXPORT": 0}


def compute_tax(amount: int, region: str = "IN") -> int:
    """Return the tax on `amount` (paise) for `region`."""
    return (amount * GST_RATE_PERCENT[region]) // 100
