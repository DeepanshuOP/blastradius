from shopcart.tax import compute_tax


def test_gst_in_india():
    assert compute_tax(10000, "IN") == 1800


def test_export_is_zero_rated():
    assert compute_tax(10000, "EXPORT") == 0
