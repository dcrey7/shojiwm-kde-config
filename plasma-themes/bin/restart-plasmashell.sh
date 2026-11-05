#!/bin/sh
# Restart plasmashell (the panel blinks ~2 s). Clears the theme caches first,
# so a changed Plasma theme shows at once.
#
# The ShojiWM config runs plasmashell as a service that restarts on exit,
# with the session's environment (XDG_CURRENT_DESKTOP=KDE, XDG_CONFIG_DIRS
# with ~/.config/kdedefaults, ...). So only stop it: ShojiWM starts it again.
# Starting it from here would give it this shell's environment instead.
rm -f "$HOME"/.cache/ksvg-elements* "$HOME"/.cache/plasma_theme_*.kcache
pkill -x plasmashell
sleep 1
# Wait until it answers on D-Bus again.
for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  qdbus6 org.kde.plasmashell /PlasmaShell >/dev/null 2>&1 && exit 0
  sleep 0.5
done
echo "plasmashell did not come back on D-Bus" >&2
exit 1
