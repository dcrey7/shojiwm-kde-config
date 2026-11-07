"""Hover and tray highlights for the ShojiWM Aero Plasma theme.

Seven-Black is drawn for AeroThemePlasma's own task manager and system tray.
ShojiWM runs KDE's stock ones, which read the theme differently:

1. Task buttons. The stock task manager swaps the button picture on hover.
   It asks for "<state>-hover" first, then "hover", then the state itself.
   Seven-Black has only a dim "hover" (AeroThemePlasma adds its glow from
   another file). So the bright active button went dim on hover, a running
   button barely changed, and a pinned button showed nothing at all.
   Fix: "hover" and "launcher-hover" show the bright active glass,
   "focus-hover" shows it brighter still, "attention-hover" stays orange.

2. System tray. The stock tray draws the tab bar's "south-active-tab" frame
   behind the open item. For the hidden-icons popup the item is the whole
   tray, so the highlight covered the whole tray, edge to edge. Seven-Black's
   own tray hides that frame and draws a small button on the arrow instead.
   Fix: the frame is clear except a glass button in its right border column.
   The arrow is the last item of the tray, so the button sits on the arrow;
   for an open tray icon the frame is one icon wide, so it sits on the icon.
"""

import gzip
import pathlib
import re

PIECES = ["center", "top", "bottom", "left", "right", "topleft", "topright", "bottomleft", "bottomright"]


def element_span(text: str, element_id: str) -> tuple[int, int]:
    """Start and end offsets of the element with this id (a <g> with its children)."""
    at = text.index(f'id="{element_id}"')
    start = text.rindex("<", 0, at)
    tag = re.match(r"<([a-zA-Z:]+)", text[start:]).group(1)
    open_end = text.index(">", at)
    if text[open_end - 1] == "/":
        return start, open_end + 1
    depth = 1
    pos = open_end + 1
    pattern = re.compile(rf"<{tag}\b[^>]*?(/?)>|</{tag}>")
    while depth:
        m = pattern.search(text, pos)
        if m.group(0).startswith("</"):
            depth -= 1
        elif m.group(1) != "/":
            depth += 1
        pos = m.end()
    return start, pos


def copy_element(text: str, old_id: str, new_id: str) -> str:
    """The element's XML with a new id. Inner ids get a suffix, so none repeat."""
    start, end = element_span(text, old_id)
    part = text[start:end].replace(f'id="{old_id}"', f'id="{new_id}"', 1)
    suffix = new_id.replace("-", "_")
    return re.sub(r'(\s)id="(?!' + re.escape(new_id) + r'")([^"]+)"', rf'\1id="\2__{suffix}"', part)


def add_task_hovers(svg: pathlib.Path) -> None:
    text = svg.read_text()
    extra = ""
    for piece in PIECES:
        # Keep Seven-Black's dim hover under a name nobody asks for.
        text = text.replace(f'id="hover-{piece}"', f'id="hover-seven-{piece}"')
    for piece in PIECES:
        focus = f"focus-{piece}"
        extra += copy_element(text, focus, f"hover-{piece}")
        extra += copy_element(text, focus, f"launcher-hover-{piece}")
        extra += copy_element(text, f"attention-{piece}", f"attention-hover-{piece}")
        # Brighter than the active button: the glass drawn twice.
        twice = copy_element(text, focus, f"focus-hover-b-{piece}")
        extra += f'<g id="focus-hover-{piece}">{copy_element(text, focus, f"focus-hover-a-{piece}")}{twice}</g>\n'
    text = re.sub(r"</svg>\s*$", extra + "</svg>\n", text)
    svg.write_text(text)
    print("task hover: hover, launcher-hover, focus-hover, attention-hover in", svg.name)




# The tray button: a rounded glass button, BUTTON_W px wide, in the frame's
# right column. The top and bottom pieces (CAP px) hold the round corners;
# the "right" piece stretches over the rest of the height. Every stroke stays
# inside its piece's clear box, so the piece sizes stay exact.
BUTTON_W = 26
CAP = 4
MID = 32
R = 3  # corner radius
TOP_WHITE = 0.30
BOTTOM_WHITE = 0.12
DARK = 'stroke="#000000" stroke-opacity="0.55" stroke-width="1" fill="none"'
LIGHT = 'stroke="#ffffff" stroke-opacity="0.40" stroke-width="1" fill="none"'
GLASS_DEFS = f"""<defs>
<linearGradient id="shojiwm-tray-glass" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#ffffff" stop-opacity="{TOP_WHITE}"/>
  <stop offset="0.47" stop-color="#ffffff" stop-opacity="0.14"/>
  <stop offset="0.5" stop-color="#ffffff" stop-opacity="0.05"/>
  <stop offset="1" stop-color="#ffffff" stop-opacity="{BOTTOM_WHITE}"/>
</linearGradient>
</defs>
"""


def cap(x: float, y: float, top: bool) -> str:
    """The top (or bottom) CAP px of the button: round corners, edge lines, fill."""
    w = BUTTON_W

    def fy(v: float) -> float:
        # v is measured from the button's outer edge; flip for the bottom cap.
        return y + v if top else y + CAP - v

    s = 1 if top else 0  # arc sweep
    white = TOP_WHITE if top else BOTTOM_WHITE
    fill = (
        f"M{x + 0.5},{fy(CAP)} V{fy(R + 0.5)} A{R},{R} 0 0 {s} {x + R + 0.5},{fy(0.5)} "
        f"H{x + w - R - 0.5} A{R},{R} 0 0 {s} {x + w - 0.5},{fy(R + 0.5)} V{fy(CAP)} Z"
    )
    outer = (
        f"M{x + 0.5},{fy(CAP)} V{fy(R + 0.5)} A{R},{R} 0 0 {s} {x + R + 0.5},{fy(0.5)} "
        f"H{x + w - R - 0.5} A{R},{R} 0 0 {s} {x + w - 0.5},{fy(R + 0.5)} V{fy(CAP)}"
    )
    r2 = R - 1
    inner = (
        f"M{x + 1.5},{fy(CAP)} V{fy(r2 + 1.5)} A{r2},{r2} 0 0 {s} {x + r2 + 1.5},{fy(1.5)} "
        f"H{x + w - r2 - 1.5} A{r2},{r2} 0 0 {s} {x + w - 1.5},{fy(r2 + 1.5)} V{fy(CAP)}"
    )
    return (
        f'<path d="{fill}" fill="#ffffff" fill-opacity="{white}"/>'
        f'<path d="{outer}" {DARK}/><path d="{inner}" {LIGHT}/>'
    )


def middle(x: float, y: float) -> str:
    w = BUTTON_W
    return (
        f'<rect x="{x + 1}" y="{y}" width="{w - 2}" height="{MID}" fill="url(#shojiwm-tray-glass)"/>'
        f'<rect x="{x}" y="{y}" width="1" height="{MID}" fill="#000000" fill-opacity="0.55"/>'
        f'<rect x="{x + w - 1}" y="{y}" width="1" height="{MID}" fill="#000000" fill-opacity="0.55"/>'
        f'<rect x="{x + 1}" y="{y}" width="1" height="{MID}" fill="#ffffff" fill-opacity="0.40"/>'
        f'<rect x="{x + w - 2}" y="{y}" width="1" height="{MID}" fill="#ffffff" fill-opacity="0.40"/>'
    )


def tray_button_pieces(prefix: str) -> str:
    """Nine frame pieces: clear, except the button in the right column."""
    x, y = -4000, -4000  # own corner of the canvas
    out = GLASS_DEFS
    parts = {
        "topright": (y, CAP, cap(x, y, top=True)),
        "right": (y + 10, MID, middle(x, y + 10)),
        "bottomright": (y + 50, CAP, cap(x, y + 50, top=False)),
    }
    for piece, (py, height, art) in parts.items():
        box = f'<rect x="{x}" y="{py}" width="{BUTTON_W}" height="{height}" fill="#000000" fill-opacity="0"/>'
        out += f'<g id="{prefix}-{piece}">{box}{art}</g>\n'
    # Clear pieces: the left column and the middle are 1 px wide.
    clear = {"topleft": (1, CAP), "left": (1, MID), "bottomleft": (1, CAP), "top": (1, CAP), "center": (1, 1), "bottom": (1, CAP)}
    for i, (piece, (w, height)) in enumerate(clear.items()):
        out += f'<rect id="{prefix}-{piece}" x="{x + 100 + 10 * i}" y="{y}" width="{w}" height="{height}" fill="#000000" fill-opacity="0"/>\n'
    return out


def tray_button_highlight(svgz: pathlib.Path) -> None:
    text = gzip.decompress(svgz.read_bytes()).decode()
    prefix = "south-active-tab"  # the tray on a bottom panel
    for piece in PIECES:
        text = text.replace(f'id="{prefix}-{piece}"', f'id="{prefix}-seven-{piece}"')
    text = re.sub(r"</svg>\s*$", tray_button_pieces(prefix) + "</svg>\n", text)
    svgz.write_bytes(gzip.compress(text.encode()))
    print("tray: small glass button instead of a whole-tray highlight in", svgz.name)
