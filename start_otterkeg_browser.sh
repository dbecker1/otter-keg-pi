#!/bin/bash

rm -rf ~/.cache/chromium
DISPLAY=:0 chromium-browser  --disable-features=InfiniteSessionRestore --kiosk https://keg.theotterpond.com/view &>/dev/null

