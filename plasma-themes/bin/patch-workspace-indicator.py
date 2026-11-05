"""Give the panel's workspace numbers (cachyos.workspace-indicator) a dark
Aero glass look, as a setting.

The plasmoid sits on both the Aero and the Mac panel. A new config key,
General/glass (default false), picks the look:

  glass = false  the original plain circles (Mac, as before)
  glass = true   round macOS glass lights in blue, like the title bar
                 traffic lights (images from make-workspace-lights.py): the
                 current workspace is blue glass, the others grey glass;
                 hover grows the light 1.1x and fades in the blue tint,
                 a press pops it to 1.2x

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
                            opacity: pill.isCurrent || pill.pressed ? 1 : (pill.hovered ? 0.55 : 0)
                            Behavior on opacity { NumberAnimation { duration: 120; easing.type: Easing.OutCubic } }
                        }
                    }
                }

"""
qml = qml.replace(OLD_BACKGROUND, NEW_BACKGROUND)

# Round cells at the original size; in glass mode the light and its number
# grow a little under the pointer and pop when pressed, like the title bar
# traffic lights.
qml = qml.replace(
    "                onClicked: root.switchDesktop(index)\n",
    "                onClicked: root.switchDesktop(index)\n"
    "\n"
    "                // 1.1x under the pointer (ease out), 1.2x pressed (springs back).\n"
    "                property real grow: root.glass ? (pressed ? 1.2 : (hovered ? 1.1 : 1.0)) : 1.0\n"
    "                Behavior on grow {\n"
    "                    NumberAnimation {\n"
    "                        duration: 150\n"
    "                        easing.type: pill.pressed ? Easing.OutBack : Easing.OutCubic\n"
    "                    }\n"
    "                }\n",
)
qml = qml.replace(
    "                    color: pill.isCurrent\n"
    "                           ? Kirigami.Theme.highlightedTextColor\n"
    "                           : Kirigami.Theme.textColor\n",
    "                    scale: pill.grow\n"
    "                    color: root.glass\n"
    "                           ? (pill.isCurrent || pill.hovered ? \"#ffffff\" : \"#c4ccd8\")\n"
    "                           : (pill.isCurrent\n"
    "                              ? Kirigami.Theme.highlightedTextColor\n"
    "                              : Kirigami.Theme.textColor)\n"
    "                    style: root.glass ? Text.Raised : Text.Normal\n"
    "                    styleColor: \"#80000000\"\n",
)
qml = qml.replace(
    "    readonly property var currentDesktop: vdInfo.currentDesktop\n",
    "    readonly property var currentDesktop: vdInfo.currentDesktop\n"
    "    // Aero glass lights (General/glass), else the plain circles.\n"
    "    readonly property bool glass: Plasmoid.configuration.glass\n"
    "    // The glass light's diameter: a little inside the round cell.\n"
    "    readonly property real lightSize: Math.round(Kirigami.Units.gridUnit * 1.3)\n",
)
for needle in ["property real grow", "readonly property real lightSize", "macOS glass light in blue", "scale: pill.grow"]:
    if needle not in qml:
        raise SystemExit(f"patch failed: {needle!r} missing (original changed?)")
(pkg / "contents/ui/main.qml").write_text(qml)
print("patched", pkg / "contents/ui/main.qml")

# The glass light images live next to the QML.
import subprocess  # noqa: E402
subprocess.run(["python3", str(pathlib.Path(__file__).with_name("make-workspace-lights.py"))], check=True)
