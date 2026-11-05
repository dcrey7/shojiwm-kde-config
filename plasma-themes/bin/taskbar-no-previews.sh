#!/bin/sh
# Turn off the task manager's hover previews and its "highlight windows"
# effect, live, on every panel. Backs up the panel config first.
# Undo: same script with "true true" as arguments.
TIPS=${1:-false}
HIGHLIGHT=${2:-false}
B="$HOME/.local/state/shojiwm-themes/backups"
mkdir -p "$B"
cp "$HOME/.config/plasma-org.kde.plasma.desktop-appletsrc" \
  "$B/plasma-org.kde.plasma.desktop-appletsrc.$(date +%Y-%m-%d-%H%M)-taskbar-previews.bak"
qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
panels().forEach(function (p) {
  p.widgets('org.kde.plasma.icontasks').concat(p.widgets('org.kde.plasma.taskmanager')).forEach(function (w) {
    w.currentConfigGroup = ['General'];
    w.writeConfig('showToolTips', $TIPS);
    w.writeConfig('highlightWindows', $HIGHLIGHT);
    print(w.type + ' ' + w.id + ' set');
  });
});"
