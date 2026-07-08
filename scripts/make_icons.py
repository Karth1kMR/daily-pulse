#!/usr/bin/env python3
"""Generate PWA icons: a pulse/heartbeat line on an indigo rounded square."""
from PIL import Image, ImageDraw
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "app" / "icons"
OUT.mkdir(parents=True, exist_ok=True)


def make_icon(size, radius_pct=0.22, fname=None):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = int(size * radius_pct)
    # vertical indigo gradient background
    top, bottom = (37, 61, 158), (79, 108, 224)
    grad = Image.new("RGBA", (size, size))
    gd = ImageDraw.Draw(grad)
    for y in range(size):
        t = y / size
        gd.line([(0, y), (size, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(top, bottom)) + (255,))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=255)
    img.paste(grad, (0, 0), mask)

    # heartbeat pulse line across the middle
    w = max(3, size // 26)
    y0 = size * 0.52
    pts = [
        (size * 0.14, y0), (size * 0.34, y0), (size * 0.42, size * 0.30),
        (size * 0.52, size * 0.70), (size * 0.60, size * 0.44),
        (size * 0.66, y0), (size * 0.86, y0),
    ]
    d.line(pts, fill=(255, 255, 255, 255), width=w, joint="curve")
    dot_r = max(2, size // 30)
    x, y = pts[-1]
    d.ellipse([x - dot_r, y - dot_r, x + dot_r, y + dot_r], fill=(255, 214, 90, 255))

    fname = fname or f"icon-{size}.png"
    # iOS home-screen icons must be opaque
    solid = Image.new("RGB", (size, size), top)
    solid.paste(img, (0, 0), img)
    (solid if fname.startswith("apple") else img).save(OUT / fname)
    print("wrote", OUT / fname)


make_icon(192)
make_icon(512)
make_icon(180, fname="apple-touch-icon.png")
