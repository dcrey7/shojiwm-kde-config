"""Draw the dark Aero glass start orb around the current Kickoff icon.

Plasma draws icons with QtSvg (SVG Tiny 1.2): gradients and opacity work,
filters (blur) do not. So every glow here is a radial gradient.

Writes, next to this script:
  start-orb.svg          the orb at rest (the Kickoff icon)
  start-orb-hover.svg    brighter glow (hover frame)
  start-orb-pressed.svg  darker (pressed frame)
  start-orb-sheet.png    the three frames stacked, for launchers that take an
                         orb sheet (normal, hover, pressed; see the doc)

Run: uv run python make_orb.py   (needs rsvg-convert and magick for the sheet)
"""

import pathlib
import subprocess

HERE = pathlib.Path(__file__).parent

# The Kickoff icon in the middle: a 3x3 grid of coloured dots on a 38x38
# canvas. Change ICON_DOTS to draw your own.
ICON_DOTS = [
    (8, 8, "#FF4D4D"), (19, 8, "#F8A63A"), (30, 8, "white"),
    (8, 19, "white"), (19, 19, "#F4E72F"), (30, 19, "#FFFDFD"),
    (8, 30, "#59A6FF"), (19, 30, "white"), (30, 30, "#2AD13D"),
]

# Per state: inner glow colour and strength, outer halo strength.
STATES = {
    "": {"glow": "#3fb6ff", "glow_a": 0.55, "halo_a": 0.25, "body_mid": "#16263a"},
    "-hover": {"glow": "#6fd0ff", "glow_a": 0.95, "halo_a": 0.65, "body_mid": "#1d3552"},
    "-pressed": {"glow": "#2a8fd0", "glow_a": 0.45, "halo_a": 0.15, "body_mid": "#0e1a28"},
}


def orb_svg(glow: str, glow_a: float, halo_a: float, body_mid: str) -> str:
    # 64x64 canvas, sphere radius 27 at the centre; the halo uses the rest.
    icon = "\n".join(
        f'    <circle cx="{x}" cy="{y}" r="3" fill="{c}"/>' for x, y, c in ICON_DOTS
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">
  <defs>
    <radialGradient id="halo" cx="32" cy="32" r="32" gradientUnits="userSpaceOnUse">
      <stop offset="0.78" stop-color="{glow}" stop-opacity="{halo_a}"/>
      <stop offset="1" stop-color="{glow}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="body" cx="32" cy="26" r="30" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{body_mid}"/>
      <stop offset="0.7" stop-color="#0a121c"/>
      <stop offset="1" stop-color="#03060a"/>
    </radialGradient>
    <radialGradient id="glow" cx="32" cy="56" r="26" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{glow}" stop-opacity="{glow_a}"/>
      <stop offset="0.55" stop-color="{glow}" stop-opacity="{glow_a * 0.35:.3f}"/>
      <stop offset="1" stop-color="{glow}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="gloss" x1="0" y1="6" x2="0" y2="32" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#ffffff" stop-opacity="0.62"/>
      <stop offset="1" stop-color="#ffffff" stop-opacity="0.04"/>
    </linearGradient>
    <linearGradient id="rim" x1="0" y1="5" x2="0" y2="59" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#ffffff" stop-opacity="0.55"/>
      <stop offset="0.5" stop-color="#ffffff" stop-opacity="0.12"/>
      <stop offset="1" stop-color="{glow}" stop-opacity="0.7"/>
    </linearGradient>
  </defs>
  <circle cx="32" cy="32" r="32" fill="url(#halo)"/>
  <circle cx="32" cy="32" r="27" fill="#000000" fill-opacity="0.6"/>
  <circle cx="32" cy="32" r="26" fill="url(#body)"/>
  <circle cx="32" cy="32" r="26" fill="url(#glow)"/>
  <g transform="translate(16.42 16.42) scale(0.82)">
{icon}
  </g>
  <ellipse cx="32" cy="19.5" rx="20" ry="13" fill="url(#gloss)"/>
  <circle cx="32" cy="32" r="25.6" fill="none" stroke="url(#rim)" stroke-width="0.9"/>
  <circle cx="32" cy="32" r="26.6" fill="none" stroke="#000000" stroke-opacity="0.75" stroke-width="0.9"/>
</svg>
"""


def main() -> None:
    pngs = []
    for suffix, s in STATES.items():
        svg = HERE / f"start-orb{suffix}.svg"
        svg.write_text(orb_svg(**s))
        png = HERE / f"start-orb{suffix}.png"
        subprocess.run(["rsvg-convert", "-w", "128", "-h", "128", str(svg), "-o", str(png)], check=True)
        pngs.append(str(png))
    # Normal, hover, pressed stacked top to bottom: the ClassicShell orb sheet.
    subprocess.run(
        ["magick", *pngs, "-append", "+repage", str(HERE / "start-orb-sheet.png")], check=True
    )
    for png in pngs:
        pathlib.Path(png).unlink()


if __name__ == "__main__":
    main()
