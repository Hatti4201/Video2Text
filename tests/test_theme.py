import re

from app.theme import get_palette

HEX_RE = re.compile(r"^#[0-9a-f]{6}$")


def test_light_and_dark_palettes_have_matching_keys_and_valid_hex():
    light = get_palette("default", "light")
    dark = get_palette("default", "dark")

    assert set(light.keys()) == set(dark.keys())
    for value in list(light.values()) + list(dark.values()):
        assert HEX_RE.match(value)


def test_env_var_overrides(monkeypatch):
    monkeypatch.setenv("VIDEO2TEXT_MODE", "dark")
    assert get_palette("default") == get_palette("default", "dark")


def test_unknown_theme_falls_back_to_default():
    assert get_palette("does-not-exist", "light") == get_palette("default", "light")
