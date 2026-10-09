"""Plain-text order receipts."""


def format_rupees(paise: int) -> str:
    """Format an amount in paise as rupees, e.g. 49900 -> 'Rs 499.00'."""
    return f"Rs {paise // 100}.{paise % 100:02d}"


def receipt_line(sku: str, qty: int, amount: int) -> str:
    """One receipt line: SKU, quantity and amount."""
    return f"{sku:<10} x{qty:<3} {format_rupees(amount):>12}"
