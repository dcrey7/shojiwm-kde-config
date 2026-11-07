"""Give the panel's workspace numbers (cachyos.workspace-indicator) a dark
Aero glass look, as a setting.

The plasmoid sits on both the Aero and the Mac panel. A new config key,
General/glass (default false), picks the look:

  glass = false  the original plain circles (Mac, as before)
  glass = true   round macOS glass lights in blue, like the title bar
                 traffic lights (images from make-workspace-lights.py): the
                 current workspace is blue glass, the others grey glass;
                 hover grows the light 1.2x and fades in the blue tint
                 (both 200 ms, soft start and stop; the number sits
                 inside the light, centred on the light, and scales
                 with it as one unit),
                 a press works like the start orb: the light dips to
                 0.9x in full blue, then springs back up

The Aero layout (make-global-themes.py) writes glass = true. Clicking still
switches the workspace, and the count still follows the workspaces.

Run: uv run python patch-workspace-indicator.py   (safe to run again)
The first run keeps the original in
~/.local/state/shojiwm-themes/backups/workspace-indicator-original/.
"""
import pathlib
import shutil

HOME = pathlib.Path.home()
pkg = HOME / ".local/share/plasma/plasmoids/cachyos.workspace-indicator"
backup = HOME / ".local/state/shojiwm-themes/backups/workspace-indicator-original"
if not backup.exists():
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(pkg, backup)

# The setting: one bool, off by default.
(pkg / "contents/config").mkdir(parents=True, exist_ok=True)
(pkg / "contents/config/main.xml").write_text("""<?xml version="1.0" encoding="UTF-8"?>
<kcfg xmlns="http://www.kde.org/standards/kcfg/1.0"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.kde.org/standards/kcfg/1.0
      http://www.kde.org/standards/kcfg/1.0/kcfg.xsd">
  <kcfgfile name=""/>
  <group name="General">
    <entry name="glass" type="Bool">
      <default>false</default>
    </entry>
  </group>
</kcfg>
""")

# Start from the original QML each time, so the patch can run again.
qml = (backup / "contents/ui/main.qml").read_text()

OLD_BACKGROUND = qml[qml.index("                background: Rectangle {"):qml.index("                contentItem: PC3.Label {")]
NEW_BACKGROUND = """                background: Item {
                    anchors.fill: parent

                    // Mac: the original plain circle.
                    Rectangle {
                        visible: !root.glass
                        anchors.fill: parent
                        radius: width / 2
                        color: pill.isCurrent
                            ? Kirigami.Theme.highlightColor
                            : (pill.hovered ? Qt.rgba(Kirigami.Theme.textColor.r,
                                                      Kirigami.Theme.textColor.g,
                                                      Kirigami.Theme.textColor.b,
                                                      0.15)
                                            : "transparent")
                        border.width: pill.isCurrent ? 0 : 1
                        border.color: Qt.rgba(Kirigami.Theme.textColor.r,
                                              Kirigami.Theme.textColor.g,
                                              Kirigami.Theme.textColor.b,
                                              0.4)

                        Behavior on color {
                            ColorAnimation {
                                duration: 160
                                easing.type: Easing.OutCubic
                            }
                        }
                    }

                    // Aero: a macOS glass light in blue (make-workspace-lights.py).
                    // Grey glass for other workspaces; the blue tint fades in
                    // under the pointer.
                    Item {
                        visible: root.glass
                        anchors.centerIn: parent
                        width: root.lightSize
                        height: root.lightSize
                        scale: pill.grow

                        Image {
                            anchors.fill: parent
                            source: Qt.resolvedUrl("../images/ws-light-inactive.svg")
                            sourceSize: Qt.size(width * 2, height * 2)
                            smooth: true
                        }
                        Image {
                            anchors.fill: parent
                            source: Qt.resolvedUrl("../images/ws-light-active.svg")
                            sourceSize: Qt.size(width * 2, height * 2)
                            smooth: true
                            // Full blue at once on a press; fades otherwise.
                            opacity: pill.isCurrent || pill.pressedLook ? 1 : (pill.hovered ? 0.55 : 0)
                            Behavior on opacity { enabled: !pill.tintSnap; NumberAnimation { duration: 200; easing.type: Easing.InOutCubic } }
                        }
                        // The number, in the light so the two scale as one.
                        // Noto Sans digits are all 0.572 em wide, and each
                        // one is drawn visually centred in that width. So
                        // place the text from the font design, not from the
                        // laid-out width: plasmashell rounds that to whole
                        // pixels, which pushed the digit right.
                        // Digits stand 0.714 em tall on the baseline, so the
                        // baseline sits 0.357 em below the light's centre.
                        // No hinting and no pixel snapping, so the digit
                        // lands exactly there.
                        Text {
                            id: number
                            x: parent.width / 2 - 0.286 * font.pixelSize * text.length
                            y: parent.height / 2 + 0.357 * font.pixelSize - baselineOffset
                            text: (index + 1).toString()
                            renderType: Text.CurveRendering
                            color: pill.isCurrent || pill.hovered || pill.pressedLook ? "#ffffff" : "#c4ccd8"
                            font.family: "Noto Sans"
                            font.pixelSize: root.lightSize * 0.6
                            font.hintingPreference: Font.PreferNoHinting
                            font.bold: pill.isCurrent
                        }
                    }
                }

"""
qml = qml.replace(OLD_BACKGROUND, NEW_BACKGROUND)

# The press, like the start orb (patch-sevenstart.py): the light dips to 0.9x
# of its normal size in 50 ms and turns full blue at once. It stays down
# while held, and at least 100 ms even for a fast click, then springs back to
# its hover size in 180 ms with a small overshoot. grow = hover x press, so the
# hover grow keeps its own soft 200 ms animation underneath.
PRESS = """
                // Glass mode: 1.2x under the pointer (soft start and stop).
                property real hoverGrow: root.glass && hovered ? 1.2 : 1.0
                Behavior on hoverGrow {
                    NumberAnimation { duration: 200; easing.type: Easing.InOutCubic }
                }
                // The press (see patch-workspace-indicator.py): dip to 0.9x,
                // hold at least 100 ms, spring back with a small overshoot.
                property real pressFactor: 1
                property bool pressedLook: false
                property bool tintSnap: false
                property real pressStart: 0
                property real grow: root.glass ? hoverGrow * pressFactor : 1.0
                onPressedChanged: {
                    if (!root.glass)
                        return;
                    if (pressed) {
                        releaseWait.stop();
                        pressUp.stop();
                        tintSnap = true;
                        pressedLook = true;
                        pressStart = Date.now();
                        pressDown.to = 0.9 / hoverGrow;
                        pressDown.restart();
                    } else {
                        releaseWait.interval = Math.max(1, 100 - (Date.now() - pressStart));
                        releaseWait.restart();
                    }
                }
                NumberAnimation { id: pressDown; target: pill; property: "pressFactor"; duration: 50; easing.type: Easing.OutCubic }
                NumberAnimation { id: pressUp; target: pill; property: "pressFactor"; to: 1; duration: 180; easing.type: Easing.OutBack }
                Timer {
                    id: releaseWait
                    onTriggered: {
                        pill.tintSnap = false;
                        pill.pressedLook = false;
                        pressDown.stop();
                        pressUp.restart();
                    }
                }
"""

# Round cells at the original size; in glass mode the light and its number
# grow a little under the pointer and dip when pressed.
qml = qml.replace(
    "                onClicked: root.switchDesktop(index)\n",
    "                onClicked: root.switchDesktop(index)\n"
    + PRESS,
)
qml = qml.replace(
    "                contentItem: PC3.Label {\n"
    "                    text: (index + 1).toString()\n",
    "                contentItem: PC3.Label {\n"
    "                    // Glass mode draws its number inside the light.\n"
    "                    visible: !root.glass\n"
    "                    text: (index + 1).toString()\n",
)
qml = qml.replace(
    "    readonly property var currentDesktop: vdInfo.currentDesktop\n",
    "    readonly property var currentDesktop: vdInfo.currentDesktop\n"
    "    // Aero glass lights (General/glass), else the plain circles.\n"
    "    readonly property bool glass: Plasmoid.configuration.glass\n"
    "    // The glass light's diameter: a little inside the round cell.\n"
    "    readonly property real lightSize: Math.round(Kirigami.Units.gridUnit * 1.3)\n",
)
for needle in ["property real grow", "id: pressDown", "pill.tintSnap", "readonly property real lightSize", "macOS glass light in blue", "scale: pill.grow", "visible: !root.glass", "Text.CurveRendering"]:
    if needle not in qml:
        raise SystemExit(f"patch failed: {needle!r} missing (original changed?)")
(pkg / "contents/ui/main.qml").write_text(qml)
print("patched", pkg / "contents/ui/main.qml")

# The glass light images live next to the QML.
import subprocess  # noqa: E402
subprocess.run(["python3", str(pathlib.Path(__file__).with_name("make-workspace-lights.py"))], check=True)
