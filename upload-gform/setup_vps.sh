#!/bin/bash

# ==============================================================================
# VPS SETUP SCRIPT for GForm Upload Bot
# Target OS: Ubuntu 20.04 / 22.04 / 24.04
# ==============================================================================

set -e

echo "🚀 Starting VPS Setup..."

# 1. Update System
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# 2. Install Core Dependencies
echo "Installing core dependencies..."
sudo apt install -y wget curl unzip python3 python3-pip python3-venv xvfb

# 3. Install Google Chrome Stable
echo "Installing Google Chrome..."
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb
rm google-chrome-stable_current_amd64.deb

# 4. Setup Python Virtual Environment
echo "Setting up Python Virtual Environment..."
python3 -m venv venv
source venv/bin/activate

# 5. Install Python Requirements
echo "Installing Python libraries..."
pip install --upgrade pip
pip install -r requirements.txt

# 6. Set Permissions for helper scripts
chmod +x start_chrome.sh run_bot.sh

echo "=============================================================================="
echo "✅ SETUP COMPLETE!"
echo "=============================================================================="
echo "Follow these steps to run your bot:"
echo "1. Upload your project folder to the VPS."
echo "2. Run: bash start_chrome.sh"
echo "3. Run: bash run_bot.sh (or bash run_bot.sh -l 10 for 10 loops)"
echo "=============================================================================="
