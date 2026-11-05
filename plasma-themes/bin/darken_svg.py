"""Turn the light parts of a Windows 7 SVG dark, for the dark Aero look.

Every colour lighter than LIGHT becomes a dark one of the same hue. Two modes:
- "surface": backgrounds and text fields. White becomes a deep smoky blue-grey,
  and a white fill in a style also becomes see-through (SURFACE_OPACITY), so
  ShojiWM's blur behind the popup shows.
- "highlight": hover and selection boxes. Light blue becomes a mid blue glass,
  light enough to see on the dark menu.
Darker colours (borders, shadows, glyph outlines) stay as they are.

    from darken_svg import darken_file
    darken_file(path, "surface")
"""

import colorsys
import gzip
import pathlib
import re

LIGHT = 0.6
SURFACE_OPACITY = 0.72
HEX = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")


def dark_colour(hex_colour: str, mode: str) -> str:
    """The dark stand-in for one #rgb / #rrggbb colour; the same if not light."""
    h = hex_colour.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i : i + 2], 16) / 255 for i in (0, 2, 4))
    hue, light, sat = colorsys.rgb_to_hls(r, g, b)
    if light <= LIGHT:
        return hex_colour
    whiteness = (light - LIGHT) / (1 - LIGHT)  # 0 at LIGHT, 1 at white
    if mode == "surface":
        # White -> L 0.11, a light grey -> L 0.17; a cool blue-grey tint.
        light = 0.17 - 0.06 * whiteness
        if sat < 0.15:
            hue, sat = 0.6, 0.22
        else:
            sat = min(sat, 0.35)
    else:
        # Light blue -> mid blue glass; keep its hue, tame the saturation.
        light = 0.24 + 0.12 * whiteness
        sat = min(max(sat, 0.25), 0.55)
    r, g, b = colorsys.hls_to_rgb(hue, light, sat)
    return "#{:02x}{:02x}{:02x}".format(round(r * 255), round(g * 255), round(b * 255))


def is_near_white(hex_colour: str) -> bool:
    h = hex_colour.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return min(int(h[i : i + 2], 16) for i in (0, 2, 4)) >= 0xF0


def darken_style(style: str, mode: str) -> str:
    """Recolour one style="..." string; a near-white surface fill turns see-through."""
    see_through = False
    fill = re.search(r"(?:^|;)\s*fill\s*:\s*(#[0-9a-fA-F]{3,6})\b", style)
    if mode == "surface" and fill and is_near_white(fill.group(1)):
        see_through = True
    style = HEX.sub(lambda m: dark_colour(m.group(0), mode), style)
    if see_through:
        style = re.sub(r"(?:^|;)\s*fill-opacity\s*:[^;]*", "", style).strip(";")
        style += f";fill-opacity:{SURFACE_OPACITY}"
    return style


def darken_text(svg: str, mode: str) -> str:
    # style="fill:#fff;..." first, then plain attributes (fill="#fff", stop-color="#fff").
    svg = re.sub(r'style="([^"]*)"', lambda m: 'style="' + darken_style(m.group(1), mode) + '"', svg)
    svg = re.sub(
        r'\b(fill|stroke|stop-color|flood-color|color)="(#[0-9a-fA-F]{3,6})"',
        lambda m: f'{m.group(1)}="{dark_colour(m.group(2), mode)}"',
        svg,
    )
    return svg


def darken_file(path: pathlib.Path, mode: str) -> None:
    """Darken an .svg or .svgz in place (svgz stays gzipped)."""
    path = pathlib.Path(path)
    data = path.read_bytes()
    zipped = data[:2] == b"\x1f\x8b"
    svg = (gzip.decompress(data) if zipped else data).decode()
    out = darken_text(svg, mode).encode()
    path.write_bytes(gzip.compress(out) if zipped else out)
    print("darkened", mode, path.name)
