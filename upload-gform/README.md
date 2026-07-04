# Google Form Automation Upload

This script automates the process of filling out a Google Form and uploading files from a local directory.

## 📋 Prerequisites

### Dependencies
Ensure you have the following Python libraries installed:
```bash
pip install selenium webdriver-manager
```

### Directory Structure
The script expects the following structure in the project root:
- `bukti-PLN/`: Place all `.jpg` files to be uploaded here.
- `done/`: Successfully uploaded files will be moved here.
- `result.txt`: A log file that stores the name and email of successfully submitted entries.

### File Naming Convention
Files in `bukti-PLN/` must follow this exact format:
`Full Name_Username.jpg`

*Example: `Adi Arman_adiarman.jpg`*
The script will automatically append `@uplcid.space` to the username to form the email.

---

## 🚀 How to Use

### 1. Prepare Chrome Session
The script attaches to an existing Chrome session to maintain cookies and profiles. 

**Important:** You must close all existing Chrome instances first.
```bash
pkill -f chrome
```

Then, launch Chrome with the remote debugging port enabled:
```bash
google-chrome-stable --remote-debugging-port=9222 --user-data-dir=/home/pnyx/chrome-automation --profile-directory="Profile 1"
```

### 2. Run the Automation Script
Once Chrome is open, run the Python script:
```bash
python3 code.py
```

---

## 🛠️ Workflow Detail

1. **Random Selection**: The script picks a random `.jpg` from `bukti-PLN/`.
2. **Data Extraction**: It splits the filename to get the user's full name and email.
3. **Form Filling**: Navigates to the Google Form and fills in the required fields.
4. **File Upload**: 
   - Clicks the upload trigger.
   - Searches for the file input in the main document and then in iframes (to handle Google's picker dialog).
   - Uploads the selected image.
5. **Cleanup & Logging**:
   - Moves the uploaded file to the `done/` folder.
   - Appends the successful entry to `result.txt`.
6. **Repeat**: The process repeats until no more `.jpg` files are left in `bukti-PLN/`.
