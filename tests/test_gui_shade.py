from app.gui import _shade


def test_shade_darkens():
    assert _shade("#d04f99", -0.15) == "#b14382"


def test_shade_lightens():
    assert _shade("#d04f99", 0.15) == "#d769a8"


def test_shade_clamps_to_valid_range():
    assert _shade("#000000", -0.5) == "#000000"
    assert _shade("#ffffff", 0.5) == "#ffffff"
