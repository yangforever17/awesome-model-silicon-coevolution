#!/usr/bin/env bash
# Render overview.html to assets/overview.png with headless Chrome (fonts load from Google Fonts).
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
chrome="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
"$chrome" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
  --window-size=2040,1030 --virtual-time-budget=8000 \
  --screenshot="$here/../../assets/overview.png" "file://$here/overview.html" 2>/dev/null
echo "wrote assets/overview.png"
