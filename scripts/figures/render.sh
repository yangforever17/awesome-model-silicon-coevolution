#!/usr/bin/env bash
# Render the figure sources to PNG with headless Chrome (fonts and logos load from CDNs).
#   overview.html → assets/overview.png  (Figure 1)
#   tower.html    → assets/tower.png     (Figure 2)
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
chrome="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
shot() {  # html, out, width, height
  "$chrome" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
    --window-size="$3,$4" --virtual-time-budget=8000 \
    --screenshot="$here/../../assets/$2" "file://$here/$1" 2>/dev/null
  echo "wrote assets/$2"
}
shot overview.html overview.png 2040 1030
shot tower.html tower.png 1400 880
