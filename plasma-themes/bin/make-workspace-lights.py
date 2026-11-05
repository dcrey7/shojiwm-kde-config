"""Draw the workspace lights: the macOS 27 glass traffic light, in blue.

The same recipe as ShojiWM's mac-glass-*.svg title bar lights (a soft dark
edge, the body colour, a faint top shade, a lighter glow in the lower half,
a faint top shine, bright rims at the top and the bottom), so the workspace
circles sit in the same family as the red, yellow and green lights.

  ws-light-active.svg    the current workspace: blue glass
  ws-light-inactive.svg  the other workspaces: grey glass

The plasmoid (patch-workspace-indicator.py) shows them as images and puts
the number on top. With --preview, it also renders a comparison sheet.

Run: uv run python make-workspace-lights.py [--preview OUT.png]
"""
import pathlib
import subprocess
import sys

HOME = pathlib.Path.home()
IMAGES = HOME / ".local/share/plasma/plasmoids/cachyos.workspace-indicator/contents/images"

# macOS-style blue, tuned to sit with the red (#F25A50), yellow and green lights.
BLUE_EDGE = "#14469E"
BLUE_BODY = "#2F7BF5"
BLUE_GLOW = "#7DB6FF"

ACTIVE = f"""<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 28 28">
  <defs>
    <radialGradient id="glow" cx="14" cy="20" r="11" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{BLUE_GLOW}" stop-opacity="0.95"/>
      <stop offset="1" stop-color="{BLUE_GLOW}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="shade" x1="0" y1="1" x2="0" y2="27" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#000000" stop-opacity="0.10"/>
      <stop offset="0.5" stop-color="#000000" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="rim" x1="0" y1="1" x2="0" y2="27" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity="0.60"/>
      <stop offset="0.28" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset="0.72" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0.75"/>
    </linearGradient>
    <linearGradient id="shine" x1="0" y1="2.5" x2="0" y2="11" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity="0.14"/>
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <circle cx="14" cy="14" r="13.5" fill="{BLUE_EDGE}" fill-opacity="0.30"/>
  <circle cx="14" cy="14" r="12.9" fill="{BLUE_BODY}"/>
  <circle cx="14" cy="14" r="12.9" fill="url(#shade)"/>
  <circle cx="14" cy="14" r="12.9" fill="url(#glow)"/>
  <ellipse cx="14" cy="7.2" rx="7.6" ry="4.6" fill="url(#shine)"/>
  <circle cx="14" cy="14" r="12.4" fill="none" stroke="url(#rim)" stroke-width="1.1"/>
</svg>
"""

# The title bar's grey glass light (mac-glass-inactive.svg), unchanged.
INACTIVE = """<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 28 28">
  <defs>
    <linearGradient id="rim" x1="0" y1="1" x2="0" y2="27" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity="0.55"/>
      <stop offset="0.3" stop-color="#FFFFFF" stop-opacity="0.12"/>
      <stop offset="0.7" stop-color="#FFFFFF" stop-opacity="0.12"/>
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0.70"/>
    </linearGradient>
  </defs>
  <circle cx="14" cy="14" r="13.5" fill="#000000" fill-opacity="0.25"/>
  <circle cx="14" cy="14" r="12.9" fill="#FFFFFF" fill-opacity="0.20"/>
  <circle cx="14" cy="14" r="12.4" fill="none" stroke="url(#rim)" stroke-width="1.1"/>
</svg>
"""


def write_assets():
    IMAGES.mkdir(parents=True, exist_ok=True)
    (IMAGES / "ws-light-active.svg").write_text(ACTIVE)
    (IMAGES / "ws-light-inactive.svg").write_text(INACTIVE)
    print("wrote", IMAGES)


_light_count = 0


def light(svg: str, x: float, y: float, size: float, opacity: float = 1.0) -> str:
    """Place one light SVG (28 px viewBox) at (x, y), `size` px wide."""
    global _light_count
    _light_count += 1
    inner = svg.split(">", 1)[1].rsplit("</svg>", 1)[0]
    # Each copy gets its own gradient ids, or the first copy's colours win.
    for gid in ("glow", "shade", "rim", "shine"):
        inner = inner.replace(f'id="{gid}"', f'id="{gid}{_light_count}"')
        inner = inner.replace(f"url(#{gid})", f"url(#{gid}{_light_count})")
    scale = size / 28
    return (f'<g transform="translate({x},{y}) scale({scale})" opacity="{opacity}">'
            f"{inner}</g>")


def number(text: str, cx: float, cy: float, size: float, color: str, bold: bool) -> str:
    weight = "bold" if bold else "normal"
    return (f'<text x="{cx}" y="{cy + size * 0.36}" font-family="Noto Sans" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}" '
            f'text-anchor="middle">{text}</text>')


def preview(out: pathlib.Path):
    """Variants on the dark panel colour, at panel size (22 px lights), 4x."""
    d = 22  # light diameter on the panel, logical px
    rows = [
        ("white number", "#FFFFFF", "#D8DEE8"),
        ("dark-blue glyph", "#0B2F6E", "#2A2F38"),
    ]
    parts = []
    w, h = 300, 40 + len(rows) * 44 + 50
    parts.append(f'<rect width="{w}" height="{h}" fill="#1b2027"/>')
    labels = ["active", "inactive", "hover", "press"]
    for i, lab in enumerate(labels):
        parts.append(f'<text x="{110 + i * 46}" y="18" font-family="Noto Sans" font-size="8" '
                     f'fill="#9aa4b2" text-anchor="middle">{lab}</text>')
    for r, (name, active_num, inactive_num) in enumerate(rows):
        y = 30 + r * 44
        parts.append(f'<text x="8" y="{y + 15}" font-family="Noto Sans" font-size="8" '
                     f'fill="#9aa4b2">{name}</text>')
        # active
        cx = 110
        parts.append(light(ACTIVE, cx - d / 2, y, d))
        parts.append(number("1", cx, y + d / 2, 11, active_num, True))
        # inactive
        cx = 156
        parts.append(light(INACTIVE, cx - d / 2, y, d))
        parts.append(number("2", cx, y + d / 2, 11, inactive_num if r else "#B8C0CC", False))
        # hover on an inactive one: grows 1.1x, blue tint fades in (55%)
        cx, s = 202, d * 1.1
        parts.append(light(INACTIVE, cx - s / 2, y + d / 2 - s / 2, s))
        parts.append(light(ACTIVE, cx - s / 2, y + d / 2 - s / 2, s, 0.55))
        parts.append(number("2", cx, y + d / 2, 11 * 1.1, active_num, False))
        # press: 1.2x, full blue
        cx, s = 248, d * 1.2
        parts.append(light(ACTIVE, cx - s / 2, y + d / 2 - s / 2, s))
        parts.append(number("3", cx, y + d / 2, 11 * 1.2, active_num, True))
    # The title bar lights, for scale (16 px each, 10 px apart).
    y = 30 + len(rows) * 44
    parts.append(f'<text x="8" y="{y + 12}" font-family="Noto Sans" font-size="8" '
                 f'fill="#9aa4b2">title bar lights</text>')
    # The installed ShojiWM config's title bar lights.
    assets = HOME / ".config/shojiwm/assets"
    for i, name in enumerate(["minimize", "maximize", "close"]):
        svg = (assets / f"mac-glass-{name}.svg").read_text()
        parts.append(light(svg, 102 + i * 26, y, 16))
    sheet = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">{"".join(parts)}</svg>'
    tmp = out.with_suffix(".svg")
    tmp.write_text(sheet)
    subprocess.run(["rsvg-convert", "-z", "4", "-o", str(out), str(tmp)], check=True)
    print("preview", out)


if __name__ == "__main__":
    write_assets()
    if len(sys.argv) == 3 and sys.argv[1] == "--preview":
        preview(pathlib.Path(sys.argv[2]))
