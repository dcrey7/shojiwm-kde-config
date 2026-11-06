"""Make the "ShojiWM Aero" Plasma theme from AeroThemePlasma's Seven-Black.

Seven-Black's panel picture has edges but no middle ("center" element): on
AeroShell a KWin effect paints the glass body. ShojiWM has no such effect, so
the panel middle was empty. This copy adds a dark smoky glass middle with a
soft shine on top. Everything else is Seven-Black as is (GPL, Mirko Gennari
and WackyIdeas).

    python3 make-aero-plasma-theme.py [path/to/aerothemeplasma]
"""

import gzip
import json
import pathlib
import re
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from close_button import write_close_icons  # noqa: E402
from darken_svg import darken_file  # noqa: E402
from tooltip_frame import write_tooltip  # noqa: E402

SRC = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent.parent / "third_party/aerothemeplasma"
SEVEN_BLACK = SRC / "plasma/desktoptheme/Seven-Black"
OUT = pathlib.Path.home() / ".local/share/plasma/desktoptheme/ShojiWM-Aero"

# The glass middle: an 82% dark smoky tint in the title bar's colour, as dark as
# the title bars look (ShojiWM blurs behind it), then a white shine that fades
# out by half height (the Windows 7 taskbar's "two halves" look). Its own
# corner of the canvas keeps it apart from Seven-Black's drawings.
CENTER_DEFS = """
<defs><linearGradient id="shojiwm-aero-shine" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#ffffff" stop-opacity="0.10"/>
  <stop offset="0.48" stop-color="#ffffff" stop-opacity="0.05"/>
  <stop offset="0.5" stop-color="#ffffff" stop-opacity="0"/>
  <stop offset="1" stop-color="#000000" stop-opacity="0.12"/>
</linearGradient></defs>
"""
CENTER_GROUP = """<g id="{id}">
  <rect x="-2000" y="-2000" width="100" height="100" fill="#12141a" fill-opacity="0.82"/>
  <rect x="-2000" y="-2000" width="100" height="100" fill="url(#shojiwm-aero-shine)"/>
</g>
"""


def add_center(svg: pathlib.Path) -> None:
    """Give every panel edge (south = bottom panel, ...) the glass middle.

    Seven-Black's own "<edge>-center" is a faint texture meant to sit on
    KWin's blur; it is kept under a new name, unused."""
    text = svg.read_text()
    glass = ""
    for edge in ["", "south-", "north-", "east-", "west-"]:
        text = text.replace(f'id="{edge}center"', f'id="{edge}center-seven"')
        glass += CENTER_GROUP.format(id=f"{edge}center")
    # Insert just before the closing tag of the root <svg>.
    text = re.sub(r"</svg>\s*$", CENTER_DEFS + glass + "</svg>\n", text)
    svg.write_text(text)


TASK_ICON_MARGINS = {"top": 2, "bottom": 3, "left": 2, "right": 3}


def add_task_margins(svg: pathlib.Path) -> None:
    """Thin margins on the task buttons, so a ~37 px button holds a 32 px
    icon like the Windows 7 superbar. Icon-only tasks size the icon as the
    button height minus these margins: Seven-Black's 11 px sides (and its
    whole border pieces top and bottom) left ~16 px icons. The buttons get
    their width back from the task manager's iconSpacing setting."""
    text = svg.read_text()
    prefixes = sorted(set(re.findall(r'id="([a-z]+)-center"', text)))
    # Drop Seven-Black's own margin hints; the ones below replace them.
    text = re.sub(r'<rect\b[^>]*\bid="[a-z]+-hint-(top|bottom|left|right)-margin"[^>]*/>', "", text, flags=re.S)
    hints = ""
    for prefix in prefixes:
        for side, size in TASK_ICON_MARGINS.items():
            hint = f"{prefix}-hint-{side}-margin"
            hints += f'<rect id="{hint}" x="-3000" y="-3000" width="{size}" height="{size}" fill="none"/>\n'
    text = re.sub(r"</svg>\s*$", hints + "</svg>\n", text)
    svg.write_text(text)
    print("task margin hints for", ", ".join(prefixes))


# Seven-Black parts that come out light: text fields and media boxes are
# surfaces, list and tab highlights are glass highlights. "solid" is the
# no-compositing variant.
DARK_SVGS = [
    ("widgets/lineedit.svg", "surface"),
    ("widgets/media-delegate.svg", "surface"),
    # Push buttons (notification actions, dialogs): white with light text.
    ("widgets/button.svg", "surface"),
    ("solid/dialogs/background.svg", "surface"),
    ("solid/widgets/tooltip.svg", "surface"),
    ("widgets/viewitem.svg", "highlight"),
    ("widgets/tabbar.svgz", "highlight"),
]

TEXT_RGB = "230,233,239"
DARK_BG_RGB = "24,28,36"


def dark_colors(path: pathlib.Path) -> None:
    """Light text everywhere: Seven-Black's colours give tooltips a near-white
    background and lists and buttons black text, which read as white boxes or
    unreadable text on the dark glass."""
    text = path.read_text()
    group = ""
    out = []
    for line in text.splitlines():
        if line.startswith("["):
            group = line
        elif group.startswith("[Colors:") and "=" in line:
            key, value = line.split("=", 1)
            rgb = [int(v) for v in value.split(",")[:3]] if re.fullmatch(r"\d+,\d+,\d+(,\d+)?", value) else None
            if rgb and key == "ForegroundNormal" and sum(rgb) < 3 * 128:
                line = f"{key}={TEXT_RGB}"
            elif rgb and key.startswith("Background") and min(rgb) >= 200:
                line = f"{key}={DARK_BG_RGB}"
        out.append(line)
    path.write_text("\n".join(out) + "\n")
    print("light text in", path.relative_to(OUT))


# Popups (notifications, menus): Seven-Black's popup middle is fully clear and
# leans on KWin's blur. With ShojiWM's glass off, the page behind showed
# through and white text sat on white. This dark tint keeps them readable.
DIALOG_TINT = "opacity:1;fill:#12141a;fill-opacity:0.8;"


def tint_dialog(svgz: pathlib.Path) -> None:
    text = gzip.decompress(svgz.read_bytes()).decode()
    start = text.index('id="center"')
    end = text.index("</g>", start)
    group = text[start:end]
    old = "opacity:0;fill:#000000;fill-opacity:0.2;"
    if group.count(old) != 1:
        sys.exit(f"{svgz}: popup middle not found (upstream changed?)")
    text = text[:start] + group.replace(old, DIALOG_TINT) + text[end:]
    svgz.write_bytes(gzip.compress(text.encode()))
    print("dark popup middle in", svgz.relative_to(OUT))


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SEVEN_BLACK, OUT)
    for f in ["widgets/panel-background.svg", "translucent/widgets/panel-background.svg", "opaque/widgets/panel-background.svg"]:
        add_center(OUT / f)
    add_task_margins(OUT / "widgets/tasks.svg")
    # Dark Aero: no white anywhere in popups (see darken_svg.py).
    for f, mode in DARK_SVGS:
        if (OUT / f).exists():
            darken_file(OUT / f, mode)
    for f in ["dialogs/background.svgz", "translucent/dialogs/background.svgz"]:
        tint_dialog(OUT / f)
    for f in ["colors", "translucent/colors"]:
        dark_colors(OUT / f)
    # Notifications and tray popups: the macOS 27 red glass close.
    write_close_icons(OUT / "icons/window.svgz")
    # Tooltips: a solid dark frame. ShojiWM gives them no blur, and
    # Seven-Black's clear body left their light text unreadable.
    for f in ["widgets", "translucent/widgets", "opaque/widgets", "solid/widgets"]:
        write_tooltip(OUT / f / "tooltip.svg")
    meta_path = OUT / "metadata.json"
    meta = json.loads(meta_path.read_text())
    meta["KPlugin"]["Id"] = "ShojiWM-Aero"
    meta["KPlugin"]["Name"] = "ShojiWM Aero"
    meta["KPlugin"]["Description"] = "Seven Black with a glass panel body for ShojiWM (no KWin needed)"
    meta_path.write_text(json.dumps(meta, indent=4) + "\n")
    print("built", OUT)


if __name__ == "__main__":
    main()
