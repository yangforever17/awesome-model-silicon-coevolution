#!/usr/bin/env bash
# Render the figure sources to PNG with headless Chrome (fonts and logos load from CDNs).
#   overview.html     → assets/overview.png                    (README Figure 1)
#   tower.html        → assets/tower.png                       (README Figure 3)
#   trajectories.html → assets/trajectories.png / .pdf         (README Figure 2; paper figure)
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
shot trajectories.html trajectories.png 1400 1060
"$chrome" --headless=new --disable-gpu --no-pdf-header-footer --virtual-time-budget=8000 \
  --print-to-pdf="$here/../../assets/trajectories.pdf" "file://$here/trajectories.html" 2>/dev/null
echo "wrote assets/trajectories.pdf"
