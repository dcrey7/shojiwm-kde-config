# shojiwm-kde-config

My [ShojiWM](https://github.com/bea4dev/ShojiWM) config. It runs the KDE Plasma
desktop (taskbar, Kickoff, tray, calendar, notifications, Pager) on ShojiWM
instead of KWin, and adds Mac and KDE style effects on top.

![The desktop](https://raw.githubusercontent.com/dcrey7/ShojiWM/pr-screenshots/screenshots/desktop.png)

[Watch the tour (video)](https://raw.githubusercontent.com/dcrey7/ShojiWM/pr-screenshots/screenshots/tour-github.mp4)

## What you get

| | |
| --- | --- |
| **KDE Plasma shell** | Your KDE taskbar, Kickoff on the Super key, the tray, the calendar, notifications and the Pager, all on ShojiWM. |
| **Coverflow Alt+Tab** | A port of the GNOME extension Coverflow Alt-Tab. `Q` closes the selected window. |
| **Window grid** | `Super+Tab` shows every window in a grid. A click on a grouped taskbar icon shows that group the same way. |
| **Magic Lamp** | Minimize pours the window into its taskbar icon (a port of KWin's effect). |
| **Wobbly windows** | Windows wobble while you drag them (a port of KWin's effect). |
| **Sliding popups** | Panel popups slide in from the panel (a port of KWin's effect). |
| **Traffic lights** | Mac style close, minimize and maximize buttons in the title bar. |
| **Tiling or floating** | Each workspace tiles or floats. `Super+S` switches. |
| **Cheat sheet** | `Super+/` shows every key on screen. `shoji-keys` prints them in a terminal. |
| **Screenshots** | Spectacle works (Print Screen), through a small stand-in for KWin's screenshot service. |

| Coverflow | Grid | Magic Lamp |
| --- | --- | --- |
| ![Coverflow](https://raw.githubusercontent.com/dcrey7/ShojiWM/pr-screenshots/screenshots/coverflow.gif) | ![Grid](https://raw.githubusercontent.com/dcrey7/ShojiWM/pr-screenshots/screenshots/grid.gif) | ![Magic Lamp](https://raw.githubusercontent.com/dcrey7/ShojiWM/pr-screenshots/screenshots/magic-lamp.gif) |

| Window View | Tiling | Wobbly |
| --- | --- | --- |
| ![Window View](https://raw.githubusercontent.com/dcrey7/ShojiWM/pr-screenshots/screenshots/window-view.gif) | ![Tiling](https://raw.githubusercontent.com/dcrey7/ShojiWM/pr-screenshots/screenshots/tiling.gif) | ![Wobbly](https://raw.githubusercontent.com/dcrey7/ShojiWM/pr-screenshots/screenshots/wobbly.gif) |

| Kickoff | Calendar | Cheat sheet |
| --- | --- | --- |
| ![Kickoff](https://raw.githubusercontent.com/dcrey7/ShojiWM/pr-screenshots/screenshots/kickoff.gif) | ![Calendar](https://raw.githubusercontent.com/dcrey7/ShojiWM/pr-screenshots/screenshots/calendar.gif) | ![Cheat sheet](https://raw.githubusercontent.com/dcrey7/ShojiWM/pr-screenshots/screenshots/cheat-sheet.gif) |

## Requirements

- **ShojiWM with the KDE Plasma protocols.** These come from the
  `kde-plasma-protocols` pull request on bea4dev/ShojiWM. Until it merges,
  build ShojiWM from that branch (see Install).
- **KDE Plasma 6:** `plasmashell`, `kglobalacceld`, `qdbus6`, the polkit KDE
  agent and Spectacle.
- **Python helpers:** `python3` with `python-gobject` (PyGObject) and `grim`.
- **The rest of the session:** `hyprlock` and `swayidle` (lock),
  `wl-clipboard` and `cliphist` (clipboard history), `playerctl` (media keys).
- **Apps the keys start** (change them in `src/keymap.ts`): Konsole, Dolphin,
  Chrome, Discord, System Settings, `hyprshot` and `swappy`.

On Arch Linux:

```sh
sudo pacman -S plasma-desktop kglobalacceld qt6-tools polkit-kde-agent spectacle \
  python-gobject grim hyprlock swayidle wl-clipboard cliphist playerctl \
  konsole dolphin
```

## Install

1. Build and install ShojiWM with the KDE Plasma protocols:

   ```sh
   git clone https://github.com/bea4dev/ShojiWM
   cd ShojiWM
   git fetch https://github.com/dcrey7/ShojiWM kde-plasma-protocols
   git checkout FETCH_HEAD
   ./dist/install.sh
   ```

2. Move your current config out of the way and clone this one in its place:

   ```sh
   mv ~/.config/shojiwm ~/.config/shojiwm.bak
   git clone https://github.com/dcrey7/shojiwm-kde-config ~/.config/shojiwm
   ```

3. Link the ShojiWM SDK, so the config finds `shoji_wm`:

   ```sh
   mkdir -p ~/.config/shojiwm/node_modules
   ln -s /usr/lib/shojiwm/packages/shoji_wm ~/.config/shojiwm/node_modules/shoji_wm
   ```

4. Log out and pick **ShojiWM** on the login screen.

After you edit a file, run `shoji_wm --reload` to load the change.

## Settings

| Where | What |
| --- | --- |
| `src/keymap.ts` | Every key, and the apps the keys start. |
| `src/index.tsx`, `PREVIEW_WALLPAPER` and `PREVIEW_SWAYBG` | The wallpaper for the preview (ShojiWM nested inside KDE). A real ShojiWM login shows your KDE wallpaper and does not use them. |
| `src/index.tsx`, `LOCK_COMMAND` | The screen locker (`hyprlock`). |

## Keys

Press `Super+/` for the full list on screen, or run `shoji-keys` in a
terminal (`shoji-keys tiling` prints one group). To put `shoji-keys` on your
PATH:

```sh
ln -s ~/.config/shojiwm/src/helpers/shoji-keys.py ~/.local/bin/shoji-keys
```

The main ones:

| Key | Action |
| --- | --- |
| `Super` | Start menu (Kickoff) |
| `Super+T` / `Super+E` / `Super+B` | Terminal / Files / Browser |
| `Super+Q` | Close the window |
| `Super+H` / `Super+M` / `Super+F` | Minimize / Maximize / Full screen |
| `Super+S` | Tiling on or off for this workspace |
| `Super+Arrows` | Focus or snap, by mode |
| `Super+1..9` | Go to workspace N |
| `Alt+Tab` | Coverflow |
| `Super+Tab` | All windows in a grid |
| `Print` / `Super+Shift+S` | Spectacle / A region |
| `Super+L` | Lock the screen |
| `Ctrl+Alt+Delete` | Log out |

## License

GPL-3.0-or-later, see [LICENSE](LICENSE). Some files are ports of KWin
effects and of Coverflow Alt-Tab, and the config started from ShojiWM's
default config. [NOTICE](NOTICE) credits each one.
