#!/bin/bash

DISPLAY=:0 chromium-browser  --disable-features=InfiniteSessionRestore --kiosk https://keg.theotterpond.com/view &>/dev/null

