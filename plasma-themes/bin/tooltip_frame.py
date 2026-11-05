"""A solid dark tooltip frame for the ShojiWM Aero Plasma theme.

Seven-Black's tooltip body is nearly clear: KWin blurs behind it. ShojiWM
gives tooltips no blur (they come and go too fast; a blur made the taskbar
flicker), so on a clear body the light text could not be read. This frame is
dark smoky glass at 92%, a light 1 px rim and 5 px round corners.

Plasma's FrameSvg reads it as nine named pieces (topleft ... bottomright,
center) plus "hint-*-margin" rects that set the text padding.
"""
import pathlib

B = 6  # border piece size, px
C = 12  # centre piece size, px
R = 5  # corner radius, px
FILL = 'fill="#181c24" fill-opacity="0.92"'
RIM = 'fill="none" stroke="#ffffff" stroke-opacity="0.18" stroke-width="1"'


def corner(name: str, flip_x: bool, flip_y: bool) -> str:
    """One round corner: the body quarter and its rim arc, mirrored into place."""
    ox = B + C if flip_x else 0
    oy = B + C if flip_y else 0

    def p(x: float, y: float) -> str:
        # Points are drawn for the top-left corner, then mirrored.
        px = ox + (B - x if flip_x else x)
        py = oy + (B - y if flip_y else y)
        return f"{px:g},{py:g}"

    sweep = 1 if flip_x == flip_y else 0
    body = f"M{p(B, 0)} L{p(B, B)} L{p(0, B)} L{p(0, R)} A{R},{R} 0 0 {sweep} {p(R, 0)} Z"
    h = 0.5
    rim = f"M{p(h, B)} L{p(h, R)} A{R - h},{R - h} 0 0 {sweep} {p(R, h)} L{p(B, h)}"
    return (
        f'<g id="{name}"><rect x="{ox}" y="{oy}" width="{B}" height="{B}" fill-opacity="0"/>'
        f'<path d="{body}" {FILL}/><path d="{rim}" {RIM}/></g>'
    )


def edge(name: str, x: int, y: int, w: int, h: int, rim: str) -> str:
    return f'<g id="{name}"><rect x="{x}" y="{y}" width="{w}" height="{h}" {FILL}/>{rim}</g>'


def tooltip_svg() -> str:
    end = B + C  # where the far border pieces start
    rim = 'fill="#ffffff" fill-opacity="0.18"'
    parts = [
        corner("topleft", False, False),
        corner("topright", True, False),
        corner("bottomleft", False, True),
        corner("bottomright", True, True),
        edge("top", B, 0, C, B, f'<rect x="{B}" y="0" width="{C}" height="1" {rim}/>'),
        edge("bottom", B, end, C, B, f'<rect x="{B}" y="{end + B - 1}" width="{C}" height="1" {rim}/>'),
        edge("left", 0, B, B, C, f'<rect x="0" y="{B}" width="1" height="{C}" {rim}/>'),
        edge("right", end, B, B, C, f'<rect x="{end + B - 1}" y="{B}" width="1" height="{C}" {rim}/>'),
        f'<rect id="center" x="{B}" y="{B}" width="{C}" height="{C}" {FILL}/>',
        # Text padding: 6 px on each side (outside the drawn frame).
        '<rect id="hint-top-margin" x="40" y="0" width="1" height="6" fill-opacity="0"/>',
        '<rect id="hint-bottom-margin" x="42" y="0" width="1" height="6" fill-opacity="0"/>',
        '<rect id="hint-left-margin" x="44" y="0" width="6" height="1" fill-opacity="0"/>',
        '<rect id="hint-right-margin" x="44" y="2" width="6" height="1" fill-opacity="0"/>',
    ]
    size = 2 * B + C
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="60" height="{size}" viewBox="0 0 60 {size}">' + "".join(parts) + "</svg>\n"
    )


def write_tooltip(path: pathlib.Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(tooltip_svg())
