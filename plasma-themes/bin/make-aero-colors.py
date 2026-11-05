"""Build the dark Aero colour scheme "ShojiWM Aero Dark" from Breeze Dark.

Breeze Dark is flat grey with a bright solid blue. On the Aero look that made
every Qt menu (SevenStart's shut down menu, panel right-click menus) read as
"old KDE". This keeps Breeze Dark's structure and swaps its colours for the
Aero glass palette: smoky blue-grey surfaces and a muted glass-blue highlight.

    python3 make-aero-colors.py
"""

import pathlib
import re

SRC = pathlib.Path("/usr/share/color-schemes/BreezeDark.colors")
DST = pathlib.Path.home() / ".local/share/color-schemes/ShojiWMAeroDark.colors"
SCHEME_ID = "ShojiWMAeroDark"

# Breeze Dark colour -> Aero colour, everywhere it appears.
COLOURS = {
    "20,22,24": "20,24,33",  # view: lists, text fields, Darkly menus
    "29,31,34": "25,29,38",  # view, alternate rows
    "32,35,38": "24,28,36",  # window
    "41,44,48": "33,39,50",  # buttons, headers, tooltips
    "39,44,49": "28,33,42",  # title bar (WM)
    "32,36,40": "24,28,36",  # title bar, inactive (WM)
    "30,87,116": "38,66,97",  # alternate accent
    "61,174,233": "64,116,170",  # accent: Darkly menu highlight, focus lines; muted glass blue
}
# The selection fill (menu and list highlight): muted glass blue, not neon.
SELECTION_FILL = "47,92,138"


def build() -> str:
    text = SRC.read_text()
    for old, new in COLOURS.items():
        text = re.sub(rf"(?<=[=,]){re.escape(old)}(?=\s)", new, text)
        text = text.replace(f"={old}\n", f"={new}\n")
    # Selection fill, only inside [Colors:Selection].
    text = re.sub(
        r"(\[Colors:Selection\]\n(?:.*\n)*?BackgroundNormal=)[0-9,]+",
        rf"\g<1>{SELECTION_FILL}",
        text,
        count=1,
    )
    # Name and id; drop Breeze Dark's translated names.
    text = re.sub(r"^Name\[.*\n", "", text, flags=re.M)
    text = text.replace("ColorScheme=BreezeDark", f"ColorScheme={SCHEME_ID}")
    text = text.replace("Name=Breeze Dark", "Name=ShojiWM Aero Dark")
    return text


def main() -> None:
    DST.parent.mkdir(parents=True, exist_ok=True)
    DST.write_text(build())
    print("wrote", DST)


if __name__ == "__main__":
    main()
