#!/bin/bash

# Warna untuk output
GREEN='\033[0;32m'
NC='\033[0m'

# Get the absolute path of the current directory
PROJECT_DIR="$(pwd)"
echo -e "${GREEN}Starting Setup for Polling Bot in $PROJECT_DIR...${NC}"

# 1. Create Virtual Environment
echo -e "${GREEN}Creating Virtual Environment...${NC}"
python3 -m venv venv

# 2. Install Requirements
echo -e "${GREEN}Installing requirements...${NC}"
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt
./venv/bin/pip install packaging

# 3. Patch undetected-chromedriver for Python 3.14
# We find the path dynamically based on the python version in venv
PYTHON_VERSION=$(./venv/bin/python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PATCH_FILE="$PROJECT_DIR/venv/lib/python$PYTHON_VERSION/site-packages/undetected_chromedriver/patcher.py"

echo -e "${GREEN}Checking for patch file at: $PATCH_FILE${NC}"
if [ -f "$PATCH_FILE" ]; then
    sed -i 's/from distutils.version import LooseVersion/from packaging.version import Version as LooseVersion/g' "$PATCH_FILE"
    echo -e "${GREEN}Patch applied successfully for Python $PYTHON_VERSION.${NC}"
else
    echo "Warning: Patch file not found. Skipping patch."
fi

echo -e "${GREEN}Setup complete! You can now start the bot.${NC}"
