from shopcart.inventory import in_stock


def test_in_stock():
    assert in_stock("PEN-010", 10)


def test_out_of_stock():
    assert not in_stock("LAMP-200")
