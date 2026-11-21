#!/usr/bin/env python3
"""Render the Veldoria travel poster (entry.png).

The poster is a real Pexels file photo — a lone peak rising out of a sea
of clouds — typeset as a vintage travel poster for an invented place.
The place name is set in large letterspaced serif across the clear sky,
with a one-line descriptor beneath it and a thin cream frame.

  python3 tools/render.py            # writes entry.png (768x1024)

Photo: "A tranquil mountain peak emerges through a sea of clouds under
a clear blue sky at sunrise" by Yunus Tug, Pexels photo 9446343
(https://www.pexels.com/photo/9446343/), freely licensed.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = Path(__file__).resolve().parent.parent
W, H = 768, 1024
NAME = "VELDORIA"
TAGLINE = "THE ISLE ABOVE THE CLOUDS"
CREAM = (250, 244, 224)
SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def tracked(draw, xy, text, font, fill, tracking):
    """Draw text with extra letter spacing, centred on xy."""
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = xy[0] - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, xy[1]), ch, font=font, fill=fill)
        x += w + tracking
    return total


def main() -> int:
    photo = Image.open(HERE / "assets" / "peak.jpg").convert("RGB")
    # Centre-crop the portrait photo to the 3:4 poster frame.
    tw, th = W, H
    scale = max(tw / photo.width, th / photo.height)
    nw, nh = round(photo.width * scale), round(photo.height * scale)
    photo = photo.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - tw) // 2, (nh - th) // 2
    poster = photo.crop((left, top, left + tw, top + th))

    # A whisper of a scrim behind the name so the cream type stays
    # legible against the sky, fading out before the peak.
    scrim = Image.new("L", (W, 300), 0)
    sd = ImageDraw.Draw(scrim)
    for y in range(300):
        alpha = round(70 * (1 - y / 300) ** 1.6)
        sd.line([(0, y), (W, y)], fill=alpha)
    scrim = scrim.filter(ImageFilter.GaussianBlur(8))
    navy = Image.new("RGB", (W, 300), (10, 32, 64))
    poster.paste(navy, (0, 0), scrim)

    draw = ImageDraw.Draw(poster, "RGBA")

    # The name: large serif, tracked out, cream, with a soft shadow.
    # Auto-fit the size so the tracked name sits inside the frame.
    def tracked_width(font, tracking):
        return (
            sum(draw.textlength(ch, font=font) for ch in NAME)
            + tracking * (len(NAME) - 1)
        )

    name_size = 118
    name_font = ImageFont.truetype(SERIF_BOLD, name_size)
    while tracked_width(name_font, 14) > W - 2 * 22 - 40 and name_size > 40:
        name_size -= 4
        name_font = ImageFont.truetype(SERIF_BOLD, name_size)
    name_y = 78
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = ImageDraw.Draw(shadow)
    tracked(sh, (W / 2, name_y + 4), NAME, name_font, (10, 30, 60, 170), 14)
    shadow = shadow.filter(ImageFilter.GaussianBlur(3))
    poster.paste(Image.alpha_composite(poster.convert("RGBA"), shadow).convert("RGB"), (0, 0))
    draw = ImageDraw.Draw(poster, "RGBA")
    tracked(draw, (W / 2, name_y), NAME, name_font, CREAM, 14)

    # A hairline rule, then the descriptor in small tracked capitals.
    rule_y = name_y + name_size + 26
    draw.line([(W / 2 - 120, rule_y), (W / 2 + 120, rule_y)], fill=CREAM, width=2)
    tag_font = ImageFont.truetype(SANS, 30)
    tracked(draw, (W / 2, rule_y + 22), TAGLINE, tag_font, CREAM, 7)

    # Thin cream frame, inset from the edge.
    inset = 22
    draw.rectangle(
        [inset, inset, W - inset - 1, H - inset - 1], outline=CREAM, width=3
    )

    out = HERE / "entry.png"
    poster.save(out, format="PNG", optimize=True)
    print(f"wrote {out} {poster.size} {out.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
