# Deployment Guide for Polling Project

This guide explains how to deploy the Polling Project to an Ubuntu VPS.

## Prerequisites

- An Ubuntu VPS (20.04 or 22.04 recommended).
- Sudo privileges on the VPS.
- Git installed (if cloning from a repository).

## Deployment Steps

### 1. Upload the Project
Upload your project files to the VPS. You can use `git clone` or SCP/SFTP.

```bash
# Example using git
git clone <your-repo-url>
cd projek-polling
```

### 2. Run the Setup Script
The project includes a `deploy.sh` script that automates the installation of Google Chrome, Python dependencies, and sets up a background service.

```bash
# Make the script executable
chmod +x deploy.sh

# Run the script
./deploy.sh
```

### 3. Configure Environment Variables
After running the script, a `.env` file will be created from `.env.example`. You **must** edit this file with your credentials.

```bash
nano .env
```

Fill in all the required fields (e.g., IMAP settings, credentials, etc.) and save the file.

### 4. Manage the Bot Service
The bot is set up as a `systemd` service called `polling-bot`. This ensures it starts automatically on boot and restarts if it crashes.

**Start the bot:**
```bash
sudo systemctl start polling-bot
```

**Stop the bot:**
```bash
sudo systemctl stop polling-bot
```

**Restart the bot:**
```bash
sudo systemctl restart polling-bot
```

**Check status:**
```bash
sudo systemctl status polling-bot
```

**View logs in real-time:**
```bash
journalctl -u polling-bot -f
```

## Troubleshooting

### Browser Issues
Since this bot uses `undetected-chromedriver`, it requires Google Chrome to be installed. The `deploy.sh` script handles this. If you encounter issues with the browser:
- Ensure the VPS has enough RAM (at least 2GB recommended).
- If running in a very restricted environment, you may need to add `--headless=new` to the Chrome options in the Python code.

### Dependency Errors
If you add new libraries to `requirements.txt`, run the following to update the environment:
```bash
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart polling-bot
```
