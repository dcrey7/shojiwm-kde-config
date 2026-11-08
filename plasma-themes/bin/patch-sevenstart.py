"""Make SevenStart run without its C++ part (ShojiWM starts plasmashell without
a user plugin path). Each call into the missing C++ applet becomes a no-op;
those calls only shape the X11 floating orb, which stays off on Wayland."""
import pathlib
import re
import shutil
import sys

# Usage: patch-sevenstart.py [aerothemeplasma checkout]. Installs a fresh copy
# of SevenStart from the checkout, then patches it (safe to run again).
src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent.parent / "third_party/aerothemeplasma"
pkg = pathlib.Path.home() / ".local/share/plasma/plasmoids/io.gitgud.wackyideas.SevenStart"
shutil.rmtree(pkg, ignore_errors=True)
shutil.copytree(src / "plasma/plasmoids/io.gitgud.wackyideas.SevenStart", pkg)
ui = pkg / "contents/ui"
# The orb window: a layer-shell strip above the panel. Our StartOrb.qml is a
# rewrite of SevenStart's own (AGPL-3.0), so this GPL repo does not ship it;
# put it next to this script to use it (see docs/aero-and-mac-themes.md).
start_orb = pathlib.Path(__file__).with_name("StartOrb.qml")
if start_orb.exists():
    shutil.copy(start_orb, ui / "StartOrb.qml")
else:
    print("note: no StartOrb.qml next to this script; the orb stays inside the panel")
# The orb click's helper: sends "launcher.toggle" to ShojiWM (see the file).
TOGGLE = pathlib.Path.home() / ".local/bin/shoji-launcher-toggle"
TOGGLE.parent.mkdir(parents=True, exist_ok=True)
shutil.copy(pathlib.Path(__file__).with_name("shoji-launcher-toggle"), TOGGLE)
TOGGLE.chmod(0o755)
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from darken_svg import darken_file  # noqa: E402

TEXT = "#e6e9ef"  # main text on the dark menu
TEXT_DIM = "#a8b0bd"  # secondary text, breadcrumbs
LINE = "#26ffffff"  # separators: white at 15% (QML #AARRGGBB)
# The whole-menu shade, top to bottom: smoky blue-black at 70% to 77%.
MENU_SHADE = ["#b30a0d12", "#b50a0d12", "#b80a0d12", "#bb0a0d12", "#bf0a0d12", "#c40a0d12"]
# Per file: (upstream text, dark replacement). Each must still match upstream.
DARK_QML = {
    "MenuRepresentation.qml": [
        ('property color leftPanelBackgroundColor: "white"', 'property color leftPanelBackgroundColor: "#b8141922"'),
        ('property color leftPanelSeparatorColor: "#d6e5f5"', f'property color leftPanelSeparatorColor: "{LINE}"'),
        ('property color searchPanelSeparatorColor: "#cddbea"', f'property color searchPanelSeparatorColor: "{LINE}"'),
        ('property color searchPanelBackgroundColor: "#f1f5fb"', 'property color searchPanelBackgroundColor: "#a610141b"'),
        ('property color searchFieldBackgroundColor: "white"', 'property color searchFieldBackgroundColor: "#0d1117"'),
        ('property color searchFieldTextColor: "black"', f'property color searchFieldTextColor: "{TEXT}"'),
        ('property color searchFieldPlaceholderColor: "#707070"', f'property color searchFieldPlaceholderColor: "{TEXT_DIM}"'),
        ('property color shutdownTextColor: "#202020"', f'property color shutdownTextColor: "{TEXT}"'),
        ('GradientStop { position: 0.0; color: "#ccd9ea" }', f'GradientStop {{ position: 0.0; color: "{LINE}" }}'),
        ('GradientStop { position: 1.0; color: "#f0f4fa" }', 'GradientStop { position: 1.0; color: "#0dffffff" }'),
        ('color: "black"\n\t\t\t\tverticalAlignment: TextInput.AlignTop', f'color: "{TEXT}"\n\t\t\t\tverticalAlignment: TextInput.AlignTop'),
        # No user picture tile. Windows 7's framed avatar floats half above
        # the menu in its own window and swaps to the hovered item's icon.
        # There is no avatar here (empty frame), and ShojiWM blurs behind
        # that window like a notification, so it showed a blurred patch of
        # wallpaper. The right column then starts at the top of the menu.
        ("\t\t\t\tvisible: root.visible && !searching && compositingEnabled && !root.isTouchingTopEdge()",
         "\t\t\t\tvisible: false // ShojiWM: no user picture tile"),
        ("\t\t\t\tvisible: !compositingEnabled || root.isTouchingTopEdge()",
         "\t\t\t\tvisible: false // ShojiWM: no user picture tile"),
        ("topMargin: ((compositingEnabled && !root.isTouchingTopEdge()) ? Kirigami.Units.iconSizes.huge / 2 + Kirigami.Units.mediumSpacing : 0) + Kirigami.Units.mediumSpacing",
         "topMargin: Kirigami.Units.mediumSpacing"),
        ("((compositingEnabled && !root.isTouchingTopEdge()) ? Kirigami.Units.iconSizes.huge / 2 + Kirigami.Units.smallSpacing : nonCompositingIcon.height + Kirigami.Units.smallSpacing)",
         "Kirigami.Units.smallSpacing"),
        # Plain QML Text is black unless told otherwise: "All Programs" and
        # "Back" were black on the dark menu.
        ('text: "    All Programs"', f'text: "    All Programs"\n\t\t\t\t\tcolor: "{TEXT}"'),
        ('text: "    Back"', f'text: "    Back"\n\t\t\t\t\tcolor: "{TEXT}"'),
        # The whole-menu shade. Upstream fades from black to clear for KWin's
        # strong blur; ShojiWM's blur is light, so text behind the right
        # column showed through. A steady smoky dark (70-77%) instead.
        ('GradientStop { position: 0.0; color: "#26000000" }', f'GradientStop {{ position: 0.0; color: "{MENU_SHADE[0]}" }}'),
        ('GradientStop { position: 0.11; color: "#53000000" }', f'GradientStop {{ position: 0.11; color: "{MENU_SHADE[1]}" }}'),
        ('GradientStop { position: 0.2775; color: "#82000000" }', f'GradientStop {{ position: 0.2775; color: "{MENU_SHADE[2]}" }}'),
        ('GradientStop { position: 0.445; color: "#99000000" }', f'GradientStop {{ position: 0.445; color: "{MENU_SHADE[3]}" }}'),
        ('GradientStop { position: 0.51; color: "#99000000" }', f'GradientStop {{ position: 0.51; color: "{MENU_SHADE[3]}" }}'),
        ('GradientStop { position: 0.84; color: "#4f000000" }', f'GradientStop {{ position: 0.84; color: "{MENU_SHADE[4]}" }}'),
        ('GradientStop { position: 1.0; color: "#00000000" }', f'GradientStop {{ position: 1.0; color: "{MENU_SHADE[5]}" }}'),
    ],
    # Labels that set no colour follow the Plasma theme, which some popups
    # read from a light colour set: say it outright.
    "SidePanelItemDelegate.qml": [
        ("        id: label\n", f'        id: label\n        color: "{TEXT}"\n'),
        ("        id: label_highlight\n", f'        id: label_highlight\n        color: "{TEXT}"\n'),
    ],
    "ListDelegate.qml": [("        id: label\n", f'        id: label\n        color: "{TEXT}"\n')],
    "GenericItem.qml": [("    id: appname\n", f'    id: appname\n    color: "{TEXT}"\n')],
    "KickoffButton.qml": [("            id: labelElement\n", f'            id: labelElement\n            color: "{TEXT}"\n')],
    "NavGrid.qml": [('    text: "No items match your search."', f'    text: "No items match your search."\n    color: "{TEXT_DIM}"')],
    # The hover tooltip's text (item descriptions): light on the dark tooltip.
    "main.qml": [("        id: toolTipDelegate\n", f'        id: toolTipDelegate\n        color: "{TEXT}"\n')],
    "KickoffItem.qml": [
        ('color: "#ffe599"', 'color: "#4d5c4a1f"'),
        ('color: "#000000"', f'color: "{TEXT}"'),
    ],
    "KickoffItemChild.qml": [
        ('color: "#ffe599"', 'color: "#4d5c4a1f"'),
        ('color: "#000000"', f'color: "{TEXT}"'),
    ],
    "SectionDelegate.qml": [
        ('color: "#1d3287"', 'color: "#9cc3ff"'),
        ('color: "#e5e5e5"', f'color: "{LINE}"'),
    ],
    "Breadcrumb.qml": [('color: "#404040"', f'color: "{TEXT_DIM}"')],
    "FavoritesView.qml": [('color: "#ababab"', 'color: "#80ffffff"')],
}

calls = ["setOrb", "setMask", "setTransparentWindow", "setActiveWin"]
for f in ui.glob("*.qml"):
    s = f.read_text()
    orig = s
    for c in calls:
        # Plasmoid.setX(args);  ->  if (typeof Plasmoid.setX === "function") Plasmoid.setX(args);
        s = re.sub(
            rf"Plasmoid\.{c}\(([^;]*)\);",
            rf'{{ if (typeof Plasmoid.{c} === "function") Plasmoid.{c}(\1); }}',
            s,
        )
    s = s.replace(
        "!Plasmoid.fileExists(url)",
        '(typeof Plasmoid.fileExists === "function" && !Plasmoid.fileExists(url))',
    )
    # AeroShell's patched libplasma adds this Dialog property; stock Plasma
    # has none, so the menu takes the Plasma theme's own dialog background.
    s = re.sub(
        r"^(\s*)(shadowBordersSync|shadowEnabled|marginsEnabled|customImagePath)\s*:.*$",
        r"\1// \2: needs AeroShell's libplasma (not on stock Plasma)",
        s,
        flags=re.M,
    )
    if f.name == "CompactRepresentation.qml":
        # The orb sticks out of a Windows 7 sized (40 px) panel too; upstream
        # only allows it on panels up to 30 px.
        s = s.replace("kicker.height <= 30", "kicker.height <= 48")
        # Bottom of the orb on the bottom of the panel, so it overflows above.
        s = s.replace(
            "pos.y -= 5;",
            "pos.y += kicker.height - floatingOrbPanel.scaledHeight / 3; // ShojiWM: bottom-aligned",
        )
    if f.name == "CompactRepresentation.qml":
        # A left click on the orb opens ShojiWM's own launcher, not this menu:
        # it runs shoji-launcher-toggle (one IPC line, no wait). The orb's
        # press pulse stays (FloatingOrb.qml). useShojiLauncher=false brings
        # back SevenStart's menu. Plasmashell's PATH has no ~/.local/bin, so
        # the script goes by its full path.
        old = "            if(mouse.button === Qt.LeftButton)\n                showMenu();\n"
        if s.count(old) != 1:
            sys.exit("CompactRepresentation.qml: the orb's showMenu() click not found once (upstream changed?)")
        s = s.replace(old, (
            "            if(mouse.button === Qt.LeftButton) {\n"
            "                if (Plasmoid.configuration.useShojiLauncher)\n"
            f"                    menu_executable.exec(\"'{TOGGLE}' orb\"); // ShojiWM launcher\n"
            "                else\n"
            "                    showMenu();\n"
            "            }\n"
        ))
    if f.name == "CompactRepresentation.qml":
        # The orb window (our StartOrb.qml) spans the screen width; its orb
        # size and place are orbWidth/orbHeight/orbX/orbY.
        for prop in ["width", "height", "x", "y"]:
            s = re.sub(rf"\borb\.{prop}\b", f"orb.orb{prop[0].upper()}{prop[1:]}", s)
    if f.name == "FloatingOrb.qml":
        # A quick glow: 130 ms in, 250 ms out (upstream: 300 ms linear both ways).
        s = s.replace(
            'NumberAnimation { properties: "opacity"; easing.type: Easing.Linear; duration: floatingOrb.opacityDuration  }',
            'NumberAnimation { properties: "opacity"; easing.type: Easing.OutCubic; '
            "duration: mouseAreaCompositingOff.containsMouse ? 130 : 250 }",
        )
        # A physical press. The menu opens on the mouse PRESS, so the orb
        # cannot wait for the release: each left press (and each Super key
        # press, open or close) plays a short pulse. The pushed-in frame shows
        # at 94% size for 100 ms, then the orb springs back up with a slight
        # overshoot. While the menu stays open, the orb shows its normal (or
        # hover) look, not the pushed-in frame (upstream kept it pressed).
        for frame in ["buttonIcon", "buttonIconPressed", "buttonIconHovered"]:
            s, n = re.subn(rf"^(\s*)id: {frame}$", rf"\1id: {frame}\n\1scale: floatingOrb.pressScale", s, flags=re.M)
            if n != 1:
                sys.exit(f"FloatingOrb.qml: id: {frame} not found (upstream changed?)")
        for old, new in [
            ("visible: dashWindow.visible\n", "visible: floatingOrb.pressedLook\n"),
            ("visible:  !dashWindow.visible\n", "visible: !floatingOrb.pressedLook\n"),
        ]:
            if s.count(old) != 1:
                sys.exit(f"FloatingOrb.qml: {old!r} not found once (upstream changed?)")
            s = s.replace(old, new)
        spring = """    clip: false

    // ShojiWM: the press pulse (see patch-sevenstart.py).
    property bool pressedLook: false
    property real pressScale: 1
    // One pulse per press: a second ask within 150 ms is the same press.
    property real lastPulse: 0
    function pulse() {
        var now = Date.now();
        if (now - lastPulse < 150) return;
        lastPulse = now;
        pressPulse.restart();
    }
    Connections {
        target: mouseAreaCompositingOff
        function onPressed(mouse) { if (mouse.button === Qt.LeftButton) floatingOrb.pulse(); }
    }
    Connections {
        target: Plasmoid
        // The Super key: ShojiWM fires the widget's global shortcut, which
        // toggles the menu. Every press pulses, open and close alike. Esc
        // and a click outside close the menu without a pulse.
        function onActivated() { floatingOrb.pulse(); }
    }
    Connections {
        target: Plasmoid.configuration
        // ShojiWM's launcher: on each open or close, ShojiWM's config writes
        // a new value (a time stamp) to General/orbPulse through Plasma
        // scripting. Each new value plays one pulse.
        function onOrbPulseChanged() { floatingOrb.pulse(); }
    }
    SequentialAnimation {
        id: pressPulse
        PropertyAction { target: floatingOrb; property: "pressedLook"; value: true }
        PropertyAction { target: floatingOrb; property: "pressScale"; value: 0.94 }
        PauseAnimation { duration: 100 }
        PropertyAction { target: floatingOrb; property: "pressedLook"; value: false }
        NumberAnimation { target: floatingOrb; property: "pressScale"; to: 1; duration: 180; easing.type: Easing.OutBack; easing.overshoot: 2.5 }
    }
"""
        if "    clip: false\n" not in s:
            sys.exit("FloatingOrb.qml: clip: false not found (upstream changed?)")
        s = s.replace("    clip: false\n", spring, 1)
    # Dark Aero: no white anywhere. Upstream is the light Windows 7 menu with
    # hard-coded colours; these become light text on dark smoky glass.
    for old, new in DARK_QML.get(f.name, []):
        if old not in s:
            sys.exit(f"{f.name}: {old!r} not found (upstream changed?)")
        s = s.replace(old, new)
    if s != orig:
        f.write_text(s)
        print("patched", f.name)

# Two settings for ShojiWM's launcher (see CompactRepresentation.qml and
# FloatingOrb.qml above): useShojiLauncher (the orb click opens it) and
# orbPulse (ShojiWM writes it to make the orb pulse).
main_xml = pkg / "contents/config/main.xml"
x = main_xml.read_text()
anchor = '  <group name="General">\n'
if x.count(anchor) != 1:
    sys.exit("main.xml: General group not found once (upstream changed?)")
x = x.replace(anchor, anchor + (
    '    <entry name="useShojiLauncher" type="Bool">\n'
    "      <default>true</default>\n"
    "    </entry>\n"
    '    <entry name="orbPulse" type="String">\n'
    "      <default></default>\n"
    "    </entry>\n"
))
main_xml.write_text(x)
print("patched main.xml")

# The menu's own pictures: the left pane and search field ("surface"), the
# hover and selection boxes ("highlight"). See darken_svg.py.
for name, mode in [
    ("background.svg", "surface"),
    ("lineedit.svg", "surface"),
    ("menuitem.svg", "highlight"),
    ("sidebaritem.svg", "highlight"),
]:
    darken_file(ui / "svgs" / name, mode)
