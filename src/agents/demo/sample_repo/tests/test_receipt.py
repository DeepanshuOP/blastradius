from shopcart.receipt import format_rupees, receipt_line


def test_format_rupees():
    assert format_rupees(49900) == "Rs 499.00"


def test_receipt_line_contains_amount():
    assert "Rs 25.00" in receipt_line("PEN-010", 1, 2500)
