#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "🚀 Starting deployment of Polling Project to Ubuntu VPS..."

# 1. Update System
echo "Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y

# 2. Install Python and basic dependencies
echo "Installing Python 3, pip, and venv..."
sudo apt-get install -y python3 python3-pip python3-venv curl git

# 3. Install Google Chrome
echo "Installing Google Chrome..."
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt-get install -y ./google-chrome-stable_current_amd64.deb
rm google-chrome-stable_current_amd64.deb

# 4. Setup Virtual Environment
echo "Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# 5. Install Python Dependencies
echo "Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# 6. Environment File Setup
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  PLEASE EDIT the .env file with your actual credentials before starting the bot."
else
    echo ".env file already exists. Skipping creation."
fi

# 7. Systemd Service Setup
echo "Setting up systemd service for background execution..."
PROJECT_DIR=$(pwd)
USER_NAME=$(whoami)
SERVICE_NAME="polling-bot"

# Create the systemd service file
sudo bash -c "cat > /etc/systemd/system/$SERVICE_NAME.service <<EOF
[Unit]
Description=Polling Bot Service
After=network.target

[Service]
User=$USER_NAME
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/poll.py
Restart=always
RestartSec=5
EnvironmentFile=$PROJECT_DIR/.env

[Install]
WantedBy=multi-user.target
EOF"

# Reload systemd and enable the service
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME

echo "------------------------------------------------------------------"
echo "✅ Deployment setup complete!"
echo "------------------------------------------------------------------"
echo "Next steps:"
echo "1. Edit the .env file: nano .env"
echo "2. Start the bot: sudo systemctl start $SERVICE_NAME"
echo "3. Check status: sudo systemctl status $SERVICE_NAME"
echo "4. View logs: journalctl -u $SERVICE_NAME -f"
echo "------------------------------------------------------------------"
