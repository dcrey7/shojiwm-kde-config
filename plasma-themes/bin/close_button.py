"""The macOS 27 traffic-light close for Plasma's popups (notifications, tray).

Plasma widgets look up `window-close` in the desktop theme's icons/window.svgz
before the app icon theme. Stock Breeze has no such element, so a plain cross
shows. write_close_icons() writes a copy of the system window.svgz (pin, list,
...) plus a red glass light with a dark cross (ShojiWM's mac title bar close,
drawn at 16 px), at x 32..48 of a wider canvas.

    python3 close_button.py            # the "default" (Breeze) theme: ShojiWM Mac
    from close_button import write_close_icons   # used by make-aero-plasma-theme.py
"""

import gzip
import pathlib
import sys

SRC = pathlib.Path("/usr/share/plasma/desktoptheme/default/icons/window.svgz")
DEFAULT_DST = pathlib.Path.home() / ".local/share/plasma/desktoptheme/default/icons/window.svgz"

CLOSE = """
    <defs>
        <radialGradient id="shoji-close-glow" cx="14" cy="20" r="11" gradientUnits="userSpaceOnUse">
            <stop offset="0" stop-color="#FF9A90" stop-opacity="0.95"/>
            <stop offset="1" stop-color="#FF9A90" stop-opacity="0"/>
        </radialGradient>
        <linearGradient id="shoji-close-rim" x1="0" y1="1" x2="0" y2="27" gradientUnits="userSpaceOnUse">
            <stop offset="0" stop-color="#FFFFFF" stop-opacity="0.60"/>
            <stop offset="0.28" stop-color="#FFFFFF" stop-opacity="0"/>
            <stop offset="0.72" stop-color="#FFFFFF" stop-opacity="0"/>
            <stop offset="1" stop-color="#FFFFFF" stop-opacity="0.75"/>
        </linearGradient>
    </defs>
    <g id="window-close" transform="translate(32 0)">
        <rect width="16" height="16" fill="none" opacity="0"/>
        <g transform="scale(0.5714286)">
            <circle cx="14" cy="14" r="13.5" fill="#B3261E" fill-opacity="0.30"/>
            <circle cx="14" cy="14" r="12.9" fill="#F25A50"/>
            <circle cx="14" cy="14" r="12.9" fill="url(#shoji-close-glow)"/>
            <circle cx="14" cy="14" r="12.4" fill="none" stroke="url(#shoji-close-rim)" stroke-width="1.1"/>
            <path d="M9.4 9.4 L18.6 18.6 M18.6 9.4 L9.4 18.6" fill="none" stroke="#7A0E08"
                  stroke-opacity="0.92" stroke-width="3" stroke-linecap="round"/>
        </g>
    </g>
"""


def write_close_icons(dst: pathlib.Path) -> None:
    svg = gzip.open(SRC).read().decode()
    assert 'viewBox="0 0 32 16"' in svg and 'id="window-close"' not in svg
    svg = svg.replace('viewBox="0 0 32 16"', 'viewBox="0 0 48 16"', 1)
    svg = svg.replace("</svg>", CLOSE + "</svg>", 1)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(dst, "wb") as f:
        f.write(svg.encode())
    print("close light in", dst)



# The same light as a plain icon in your user icon theme (one that lives in
# ~/.local/share/icons; a system theme is left alone).
# Plasma 6 widgets resolve `window-close` through the icon theme only
# (libplasma iconFromTheme -> KDE::icon), so this is what notifications show.
# KDE apps (Konsole tabs, dialogs) get it too.
ICON_THEME = pathlib.Path.home() / ".local/share/icons" / (sys.argv[1] if len(sys.argv) > 1 else "shoji-picks")
ICON_DIR = "scalable/actions"
ICON_NAMES = ["window-close", "window-close-symbolic"]

ICON_SVG = (
    # Padded box: the light fills ~61% of the icon (27 of 44 units), so a
    # 24 px notification button shows a ~15 px light, like the title bar's.
    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="-8 -8 44 44">'
    + CLOSE.replace('<g id="window-close" transform="translate(32 0)">', "<g>")
    .replace('<rect width="16" height="16" fill="none" opacity="0"/>', "")
    .replace('<g transform="scale(0.5714286)">', "<g>")
    + "</svg>\n"
)


def write_icon_theme_close() -> None:
    if not (ICON_THEME / "index.theme").exists():
        print("no user icon theme at", ICON_THEME, "(pass its name); nothing written")
        return
    folder = ICON_THEME / ICON_DIR
    folder.mkdir(parents=True, exist_ok=True)
    for name in ICON_NAMES:
        (folder / f"{name}.svg").write_text(ICON_SVG)
    index = ICON_THEME / "index.theme"
    text = index.read_text()
    if f"[{ICON_DIR}]" not in text:
        text = text.replace("Directories=", f"Directories={ICON_DIR},", 1)
        text += f"\n[{ICON_DIR}]\nContext=Actions\nSize=16\nMinSize=8\nMaxSize=512\nType=Scalable\n"
        index.write_text(text)
    print("close light in", folder)


if __name__ == "__main__":
    # close_button.py [icon theme name]: the light for notifications and apps.
    write_icon_theme_close()
