# 🚀 VPS Migration & Setup Guide

This guide explains how to move the GForm Upload Bot from a local machine to an Ubuntu VPS.

## 📁 Package Overview

The following helper files have been provided to automate the setup:

| File | Description |
| :--- | :--- |
| `setup_vps.sh` | Installs Chrome, Python, Xvfb, and all system dependencies. |
| `start_chrome.sh` | Launches a virtual display and Chrome in remote debugging mode (port 9222). |
| `run_bot.sh` | Shortcut to activate the virtual environment and run the bot. |
| `requirements.txt` | Python dependencies for the project. |

---

## 🛠️ Step-by-Step Migration

### 1. Upload the Project
Upload the entire project folder to your VPS using your preferred method (SCP, FileZilla, Git, etc.).

### 2. Run the System Setup
Connect to your VPS via SSH, navigate to the project folder, and run the setup script:
```bash
chmod +x setup_vps.sh
./setup_vps.sh
```

### 3. Update Paths in `code.py` (CRITICAL) ⚠️
The original code uses absolute paths (e.g., `/home/pnyx/...`), which will not work on the VPS. You **MUST** change them to relative paths.

Open `code.py` and modify the path section:

**Change this:**
```python
photos_dir = "/home/pnyx/projek-polling/upload-gform/bukti-PLN/"
done_dir = "/home/pnyx/projek-polling/upload-gform/done/"
result_file = "/home/pnyx/projek-polling/upload-gform/result.txt"
```

**To this:**
```python
import os
# Get the directory where code.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

photos_dir = os.path.join(BASE_DIR, "bukti-PLN/")
done_dir = os.path.join(BASE_DIR, "done/")
result_file = os.path.join(BASE_DIR, "result.txt")
```

---

## 🏃 How to Run the Bot

Since the VPS has no monitor, we use a virtual display (`Xvfb`) to trick Chrome into thinking it has a screen.

### Normal Workflow:
1. **Launch Chrome in the background:**
   ```bash
   bash start_chrome.sh
   ```
2. **Run the Bot:**
   ```bash
   bash run_bot.sh
   # OR run for a specific number of loops:
   bash run_bot.sh -l 50
   ```

### 💡 Persistent Execution (Background)
To keep the bot running after you disconnect from SSH, use `screen`:

1. **Create a session:**
   ```bash
   screen -S gform_bot
   ```
2. **Run the commands inside the session:**
   ```bash
   bash start_chrome.sh
   bash run_bot.sh
   ```
3. **Detach from session:**
   Press `Ctrl + A`, then `D`.
4. **Re-attach later to check progress:**
   ```bash
   screen -r gform_bot
   ```
