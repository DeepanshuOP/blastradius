import pytest

from shopcart.cart import Cart


def test_subtotal_sums_lines():
    cart = Cart()
    cart.add("BOOK-001", 2)
    cart.add("PEN-010")
    assert cart.subtotal() == 2 * 49900 + 2500


def test_total_applies_discount_then_tax():
    cart = Cart()
    cart.add("BOOK-001")
    # 49900 - 10% = 44910; GST 18% of 44910 = 8083
    assert cart.total("WELCOME10") == 44910 + 8083


def test_add_rejects_zero_quantity():
    with pytest.raises(ValueError):
        Cart().add("BOOK-001", 0)
