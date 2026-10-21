from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont
from .display import level_color

SIZE = 64
_FONT_CANDIDATES =  ("segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf")

def _font(size: int):
    for name in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue

    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def render_icon(percent: int | None, charging: bool) -> Image.Image:
    image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(
        (0, 0, SIZE - 1, SIZE - 1),
        radius = 12,
        fill = level_color(percent=percent),
        outline="white" if charging else None,
        width=5,
    )

    text ="?" if percent is None else str(percent)
    font = _font(30 if len(text) >= 3 else 44)
    left, top, right, bottom = draw.textbbox((0,0), text, font=font)
    x = (SIZE - (right - left)) / 2 - left
    y = (SIZE - (bottom - top)) / 2 - top
    draw.text((x, y), text, font=font, fill="white")
    return image