"""pytest module binding to pkg/shapes.py by naming convention."""
from pkg.shapes import area, perimeter


def test_area():
    assert area(2, 3) == 6


def test_perimeter():
    assert perimeter(2, 3) == 10
