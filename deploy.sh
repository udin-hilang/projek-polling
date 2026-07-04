#!/bin/bash

# ==============================================================================
# ONE-CLICK DEPLOYMENT SCRIPT FOR POLLING BOT (GUI MODE VIA Xvfb)
# Target OS: Ubuntu 20.04 / 22.04 / 24.04
# ==============================================================================

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 Starting One-Click Setup for Polling Bot (GUI Mode)...${NC}"

# 1. Ensure we are running as root
if [ "$EUID" -ne 0 ]; then 
  echo -e "${RED}Please run as root (use sudo bash deploy.sh)${NC}"
  exit 1
fi

# 2. System Dependencies (Adding Xvfb and X11 libraries for virtual monitor)
echo -e "${YELLOW}Updating system and installing dependencies...${NC}"
apt-get update -y
apt-get install -y wget curl unzip python3-venv python3-pip xvfb xauth x11-xserver-utils libxrender1 libxtst6 libxi6

# 3. Install Google Chrome Stable
echo -e "${YELLOW}Installing Google Chrome...${NC}"
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get install -y ./google-chrome-stable_current_amd64.deb
rm google-chrome-stable_current_amd64.deb

# 4. Project Directory Setup
PROJECT_DIR="/root/projek-polling"

if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}Error: Project directory $PROJECT_DIR not found!${NC}"
    exit 1
fi

cd "$PROJECT_DIR"

# 5. Initialize Virtual Environment and Requirements
echo -e "${YELLOW}Setting up Python environment...${NC}"
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt
./venv/bin/pip install packaging setuptools

# 6. Apply undetected-chromedriver Patch (Python 3.14 fix)
PYTHON_VERSION=$(./venv/bin/python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PATCH_FILE="$PROJECT_DIR/venv/lib/python$PYTHON_VERSION/site-packages/undetected_chromedriver/patcher.py"

if [ -f "$PATCH_FILE" ]; then
    # Fix original distutils import
    sed -i 's/from distutils.version import LooseVersion/from setuptools._distutils.version import LooseVersion/g' "$PATCH_FILE"
    # Fix incorrect packaging import (from previous broken version of deploy.sh)
    sed -i 's/from packaging.version import Version as LooseVersion/from setuptools._distutils.version import LooseVersion/g' "$PATCH_FILE"
    echo -e "${GREEN}✅ Patch applied for Python $PYTHON_VERSION.${NC}"
fi

# 7. Setup .env file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env from .env.example...${NC}"
    cp .env.example .env
    echo -e "${RED}!!! IMPORTANT !!!${NC}"
    echo -e "Please edit the .env file and set your IMAP_EMAIL and IMAP_PASSWORD."
    echo -e "Then run 'bash deploy.sh' again to start the service."
    exit 0
fi

# 8. Systemd Service Setup (Updating to use xvfb-run)
echo -e "${YELLOW}Configuring systemd service...${NC}"
if [ -f "polling-bot.service" ]; then
    # We replace the ExecStart line to use xvfb-run
    # xvfb-run provides the virtual monitor
    sed -i 's|ExecStart=.*|ExecStart=/usr/bin/xvfb-run -a /root/projek-polling/venv/bin/python /root/projek-polling/poll.py|' polling-bot.service
    
    cp polling-bot.service /etc/systemd/system/polling-bot.service
    systemctl daemon-reload
    systemctl enable polling-bot.service
    systemctl restart polling-bot.service
    echo -e "${GREEN}✅ Service installed and started with Virtual Monitor (Xvfb)!${NC}"
else
    echo -e "${RED}Error: polling-bot.service file not found in project root!${NC}"
    exit 1
fi

echo -e "\n${GREEN}================================================================${NC}"
echo -e "${GREEN}🎉 SETUP COMPLETE (GUI MODE)!${NC}"
echo -e "Bot is now running in a virtual monitor using Xvfb."
echo -e "Check logs with: ${YELLOW}tail -f $PROJECT_DIR/bot.log${NC}"
echo -e "Check status with: ${YELLOW}systemctl status polling-bot${NC}"
echo -e "${GREEN}================================================================${NC}"
