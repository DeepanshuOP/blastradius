from shopcart.pricing import apply_discount


def test_no_code_leaves_subtotal():
    assert apply_discount(10000, None) == 10000


def test_welcome10_takes_ten_percent():
    assert apply_discount(10000, "WELCOME10") == 9000


def test_code_is_case_insensitive():
    assert apply_discount(10000, "student15") == 8500


def test_unknown_code_is_ignored():
    assert apply_discount(10000, "BOGUS") == 10000
