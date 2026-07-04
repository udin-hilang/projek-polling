#!/usr/bin/env python3
"""
Launch Chrome via Selenium using an existing Chrome user profile.

Update the `USER_DATA_DIR` and `PROFILE_DIR` constants to match the
paths on your system (see the table in the previous answer).
"""

import sys
from pathlib import Path

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# ---------------------------------------------------------
# ★★ UPDATE THESE TWO VALUES TO MATCH YOUR MACHINE ★★
# ---------------------------------------------------------
# Base Chrome user‑data directory (e.g. Linux: ~/.config/google-chrome)
USER_DATA_DIR = Path.home() / ".config" / "google-chrome"

# Specific profile folder inside the user‑data directory.
# Common names: "Default", "Profile 1", "Profile 2", …
PROFILE_DIR = "Default"
# ---------------------------------------------------------

def build_options() -> Options:
    """Create Chrome options that point to an existing profile."""
    options = Options()
    # Point to the top‑level user‑data folder.
    options.add_argument(f"user-data-dir={USER_DATA_DIR}")

    # Point to the exact profile within the user‑data folder.
    options.add_argument(f"profile-directory={PROFILE_DIR}")

    # Keep the browser open after the script exits (optional).
    options.add_experimental_option("detach", True)

    # Hide the “Chrome is being controlled by automated test software” banner.
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Additional options for running in container environments.
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Optional: disable GPU acceleration if needed.
    # options.add_argument("--disable-gpu")

    return options


def main() -> None:
    if not USER_DATA_DIR.is_dir():
        sys.exit(f"Error: user‑data directory not found: {USER_DATA_DIR}")

    chrome_options = build_options()

    # Path to chromedriver executable.
    # If chromedriver is on your PATH you can leave it as simply "chromedriver".
    driver_path = ChromeDriverManager().install()  # auto‑downloaded driver

    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Example navigation – replace with whatever you need.
    driver.get("https://www.google.com")

    # The script ends here; the browser stays open because of the
    # `detach` option. Uncomment the line below if you prefer it to close
    # automatically when the script finishes.
    # driver.quit()


if __name__ == "__main__":
    main()
