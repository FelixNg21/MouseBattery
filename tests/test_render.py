from mousebattery.display import level_color
from mousebattery.render import SIZE, render_icon


def test_size():
    assert render_icon(87, False).size == (SIZE, SIZE)


def test_color_follows_level():
    assert render_icon(87, False).getpixel((32, 2)) == (*level_color(87), 255)
    assert render_icon(10, False).getpixel((32, 2)) == (*level_color(10), 255)


def test_charging_draws_white_border():
    assert render_icon(87, True).getpixel((32, 2)) == (255, 255, 255, 255)


def test_unknown_level_renders():
    assert render_icon(None, False).size == (SIZE, SIZE)