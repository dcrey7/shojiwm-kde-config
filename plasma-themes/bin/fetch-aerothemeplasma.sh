#!/bin/sh
# Download AeroThemePlasma into plasma-themes/third_party/aerothemeplasma.
#
# AeroThemePlasma is AGPL-3.0, so this repo does not ship its files. The
# build scripts (make-aero-plasma-theme.py, patch-sevenstart.py) read the
# Seven-Black Plasma theme and the SevenStart menu from this checkout and
# patch copies of them in your home folder.
#
# Pinned to the commit the patches were made against (branch Plasma/6.7,
# for Plasma 6.7). Other commits may need the patches updated.
set -eu

REPO="https://github.com/aeroshell-desktop/aerothemeplasma.git"
BRANCH="Plasma/6.7"
COMMIT="e4cca91b12dd9419485c19bece76534972324f6a"

DEST="$(cd "$(dirname "$0")/.." && pwd)/third_party/aerothemeplasma"
if [ -d "$DEST/.git" ]; then
  git -C "$DEST" fetch --quiet origin "$BRANCH"
else
  mkdir -p "$(dirname "$DEST")"
  git clone --quiet --branch "$BRANCH" "$REPO" "$DEST"
fi
git -C "$DEST" checkout --quiet "$COMMIT"
echo "AeroThemePlasma at $COMMIT in $DEST"
