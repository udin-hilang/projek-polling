#!/bin/bash

# 1. Kill any existing Chrome or Xvfb processes to start fresh
echo "Cleaning up old processes..."
pkill -f chrome
pkill -f Xvfb

# 2. Start Xvfb (Virtual Frame Buffer) in the background
# This creates a fake monitor so Chrome can run on a headless VPS
echo "Starting Xvfb..."
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99

# 3. Launch Google Chrome with Remote Debugging enabled
echo "Launching Chrome on port 9222..."
google-chrome-stable \
    --remote-debugging-port=9222 \
    --user-data-dir="$HOME/chrome-automation" \
    --profile-directory="Default" \
    --no-first-run \
    --no-default-browser \
    --disable-gpu \
    --disable-dev-shm-usage \
    --window-size=1920,1080 &

echo "Chrome is now running in the background (DISPLAY :99) on port 9222."
echo "You can now run the bot."
