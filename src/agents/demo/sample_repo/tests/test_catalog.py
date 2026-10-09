import pytest

from shopcart.catalog import unit_price


def test_known_sku_price():
    assert unit_price("BOOK-001") == 49900


def test_unknown_sku_raises():
    with pytest.raises(KeyError):
        unit_price("NOPE")
