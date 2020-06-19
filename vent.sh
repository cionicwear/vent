#!/bin/bash

DISPLAY=:0 xset s noblank
DISPLAY=:0 xset s off
DISPLAY=:0 xset -dpms
DISPLAY=:0 xrandr --output DSI-1 --rotate inverted
DISPLAY=:0 chromium-browser http://localhost:3000 --kiosk --noerrdialogs --disable-infobars --disk-cache-dir=/dev/null
