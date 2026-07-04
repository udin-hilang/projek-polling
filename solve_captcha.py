'''solve_captcha.py

Utility script to open the target poll URL behind Cloudflare's reCAPTCHA
challenge using undetected_chromedriver.

Two modes are provided:
1. **Human‑in‑the‑loop** – the browser stays visible, the script pauses
   until the user manually checks the "I’m not a robot" box, then proceeds.
2. **Automated** – (comment‑out the human section and uncomment the
   2Captcha block) to solve the challenge via a third‑party service.

The script is deliberately lightweight and does not depend on any project
code, so you can run it directly:

    python solve_captcha.py

Make sure `undetected_chromedriver` is installed (``pip install -U undetected_chromedriver``)
and, for the automated mode, supply a valid 2Captcha API key.
'''"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import undetected_chromedriver as uc

# ---------------------------------------------------------------------------
# Configuration – edit as needed
# ---------------------------------------------------------------------------
URL = "https://danantaraindonesiacx100.com/polls/cx100-danantara?ref=-rwwjmdvhc0lg9zep6odb"
USE_AUTOMATED = False  # Set True to use 2Captcha (requires API key)
CAPTCHA_API_KEY = "YOUR_2CAPTCHA_API_KEY"  # <-- fill when using automated mode
# ---------------------------------------------------------------------------

options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
# Keep window visible for manual solving; remove for true headless runs
options.add_argument("--start-maximized")
# Hide Selenium detection banner (optional but helpful)
options.add_argument("--disable-blink-features=AutomationControlled")

# For headless automation, uncomment the next line:
# options.add_argument("--headless=new")

def solve_human():
    """Open the page, wait for the user to solve the Cloudflare captcha, then continue.
    """
    driver = uc.Chrome(options=options, version_main=149)
    try:
        driver.get(URL)
        wait = WebDriverWait(driver, 120)  # up to 2 min for a human to act
        # Cloudflare loads its widget inside a known‑title iframe
        iframe = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "iframe[title='Widget containing a Cloudflare security challenge']")
            )
        )
        print("[+] Cloudflare widget detected – please solve the captcha manually.")
        driver.switch_to.frame(iframe)
        # Wait until the checkbox becomes selected (checked attribute)
        wait.until(
            EC.element_located_to_be_selected(
                (By.CSS_SELECTOR, "input[type='checkbox']")
            )
        )
        print("[+] Captcha solved – proceeding.")
        driver.switch_to.default_content()
        # Example continuation – scroll to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print("[+] Scrolled to bottom of the page.")
        time.sleep(3)
    finally:
        driver.quit()

# ---------------------------------------------------------------------------
# Automated solution using 2Captcha (requires a paid API key).
# ---------------------------------------------------------------------------
import requests

def solve_2captcha(site_key: str, page_url: str) -> str:
    """Request a solve from 2Captcha and poll until the token is ready.
    Returns the ``g-recaptcha-response`` token.
    """
    # 1️⃣ Submit solve request
    payload = {
        "key": CAPTCHA_API_KEY,
        "method": "userrecaptcha",
        "googlekey": site_key,
        "pageurl": page_url,
        "json": 1,
    }
    resp = requests.post("http://2captcha.com/in.php", data=payload).json()
    if resp.get("status") != 1:
        raise RuntimeError(f"2Captcha request failed: {resp}")
    captcha_id = resp["request"]
    # 2️⃣ Poll for result
    fetch_url = f"http://2captcha.com/res.php?key={CAPTCHA_API_KEY}&action=get&id={captcha_id}&json=1"
    while True:
        time.sleep(5)
        result = requests.get(fetch_url).json()
        if result.get("status") == 1:
            return result["request"]
        if result.get("request") != "CAPCHA_NOT_READY":
            raise RuntimeError(f"2Captcha error: {result}")

def solve_automated():
    """Fully automated flow – fetch sitekey, solve via 2Captcha, inject token.
    """
    driver = uc.Chrome(options=options, version_main=149)
    try:
        driver.get(URL)
        wait = WebDriverWait(driver, 30)
        iframe = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "iframe[title='Widget containing a Cloudflare security challenge']")
            )
        )
        driver.switch_to.frame(iframe)
        site_key = driver.find_element(By.CSS_SELECTOR, "div[data-sitekey]").get_attribute("data-sitekey")
        print(f"[+] Sitekey extracted: {site_key}")
        driver.switch_to.default_content()
        token = solve_2captcha(site_key, URL)
        print(f"[+] Token obtained (first 20 chars): {token[:20]}")
        # Inject token into the widget's form and submit
        driver.execute_script(f"""
            const iframe = document.querySelector("iframe[title='Widget containing a Cloudflare security challenge']");
            const form = iframe.contentWindow.document.querySelector('form');
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'g-recaptcha-response';
            input.value = '{token}';
            form.appendChild(input);
            form.submit();
        """)
        # Wait for the main page to finish loading (title changes)
        wait.until(EC.title_contains("Poll"))
        print("[+] Page loaded after captcha solved.")
        # Continue with any post‑load actions here
    finally:
        driver.quit()

if __name__ == "__main__":
    if USE_AUTOMATED:
        if CAPTCHA_API_KEY == "YOUR_2CAPTCHA_API_KEY":
            raise RuntimeError("Set CAPTCHA_API_KEY before using automated mode.")
        solve_automated()
    else:
        solve_human()
"""
