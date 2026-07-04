import undetected_chromedriver as uc
import time
import random
import os
import logging
import argparse
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

from config import IMAP_CONFIG, OTP_SENDER, OTP_PATTERNS
from imap_otp import get_latest_otp, delete_sender_emails


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


URL = "https://danantaraindonesiacx100.com/polls/cx100-danantara?ref=-rwwjmdvhc0lg9zep6odb"


def load_names(filepath: str) -> list:
    with open(filepath, 'r') as f:
        return [line.strip() for line in f if line.strip()]


def generate_email(names: list, domain: str) -> tuple:
    name1 = random.choice(names)
    name2 = random.choice(names)
    email = f"{name1.lower()}{name2.lower()}@{domain}"
    return email, name1, name2


def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=390,844")
    options.add_argument("--disable-gpu")
    # options.add_argument("--headless")

#   ==============arguments-arguments ini dinonaktifkan karena membuat web ter deteksi robot oleh cloudflare================

#    options.add_argument("--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1")
    
    # Additional options to avoid detection
    #options.add_argument("--disable-blink-features=AutomationControlled")
    #options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    #options.add_argument("--disable-site-isolation-trials")
    #options.add_argument("--no-first-run")
    #options.add_argument("--no-default-browser-check")
    #options.add_argument("--disable-infobars")
    #options.add_argument("--disable-notifications")
    #options.add_argument("--disable-popup-blocking")
    #options.add_argument("--ignore-certificate-errors")
    #options.add_argument("--ignore-ssl-errors")
    #options.add_argument("--allow-running-insecure-content")
    
    driver = uc.Chrome(options=options, version_main=149)
    driver.set_window_size(390, 844)
    
    # Additional stealth settings
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = {runtime: {}};
            Object.defineProperty(navigator, 'permissions', {get: () => ({query: () => Promise.resolve({state: 'granted'})})});
        """
    })
    
    return driver


def wait_and_click(driver, by, value, timeout=10, description=""):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.1)
        element.click()
        logger.info(f"Clicked: {description or value}")
        return element
    except TimeoutException:
        logger.error(f"Timeout clicking: {description or value}")
        raise


def wait_and_send_keys(driver, by, value, keys, timeout=10, description=""):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.1)
        element.clear()
        element.send_keys(keys)
        logger.info(f"Input: {description or value} = {keys}")
        return element
    except TimeoutException:
        logger.error(f"Timeout input: {description or value}")
        raise


def scroll_to_bottom(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)


def find_element_safe(driver, by, value, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    except TimeoutException:
        return None


def click_by_text(driver, text, tag="button", timeout=10):
    xpath = f"//{tag}[contains(text(), '{text}')]"
    return wait_and_click(driver, By.XPATH, xpath, timeout, f"{tag}:{text}")


def click_label_by_text(driver, text, timeout=10):
    xpath = f"//label[contains(., '{text}')]"
    return wait_and_click(driver, By.XPATH, xpath, timeout, f"label:{text}")


def input_otp_digits(driver, otp: str):
    """
    Find all OTP input fields on the page, then fill them in order with the OTP digits.
    """
    # Common selectors for OTP inputs
    otp_selectors = [
        "input[data-index]",
        "input[name^='otp']",
        "input[id*='otp']",
        "div.otp-input input",
        "input.otp-digit",
        "input[type='text'][maxlength='1']",
        "input[type='tel'][maxlength='1']",
        "input[inputmode='numeric'][maxlength='1']",
    ]

    inputs = []
    for sel in otp_selectors:
        inputs = driver.find_elements(By.CSS_SELECTOR, sel)
        if inputs:
            # Filter only visible & enabled
            inputs = [el for el in inputs if el.is_displayed() and el.is_enabled()]
            if len(inputs) >= len(otp):
                logger.info(f"Found {len(inputs)} OTP fields using selector: {sel}")
                break
        inputs = []

    # Fallback: any small numeric inputs
    if not inputs:
        inputs = driver.find_elements(By.CSS_SELECTOR,
            "input[type='text'], input[type='tel'], input[inputmode='numeric']")
        inputs = [el for el in inputs if el.is_displayed() and el.is_enabled()
                  and el.get_attribute("maxlength") == "1"]
        logger.warning(f"Fallback: found {len(inputs)} generic OTP-like fields")

    if not inputs or len(inputs) < len(otp):
        logger.error(f"Not enough OTP fields ({len(inputs)}) for OTP length {len(otp)}")
        return

    for i, digit in enumerate(otp):
        if i >= len(inputs):
            break
        try:
            inputs[i].clear()
            inputs[i].send_keys(digit)
            logger.info(f"OTP digit {i+1}: {digit}")
        except Exception as e:
            logger.warning(f"Failed to input digit {i+1}: {e}")
        time.sleep(0.1)


def click_cloudflare_checkbox(driver):
    """Attempts to click the Cloudflare checkbox if the iframe is present."""
    try:
        iframe = driver.find_elements(By.CSS_SELECTOR, "iframe[title='Widget containing a Cloudflare security challenge']")
        if iframe:
            driver.switch_to.frame(iframe[0])
            try:
                # Using the provided CSS selector for the Cloudflare checkbox
                captcha_checkbox = driver.find_element(By.CSS_SELECTOR, '#ncOB5 > div > label > input[type=checkbox]')
                if captcha_checkbox.is_displayed() and captcha_checkbox.is_enabled():
                    if not captcha_checkbox.get_attribute('checked'):
                        captcha_checkbox.click()
                        logger.info("Clicked Cloudflare checkbox using CSS selector.")
            except Exception:
                pass
            driver.switch_to.default_content()
    except Exception as e:
        logger.debug(f"Cloudflare checkbox not found or not clickable: {e}")


def take_screenshot(driver, folder: str, filename: str):
    Path(folder).mkdir(parents=True, exist_ok=True)
    filepath = Path(folder) / filename
    driver.save_screenshot(str(filepath))
    logger.info(f"Screenshot saved: {filepath}")


def wait_for_page_load(driver, timeout=10):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def wait_for_cloudflare(driver, timeout=10):
    """Wait until Cloudflare challenge (including reCAPTCHA) is no longer present.
    Returns True when the target page appears (detected by presence of a known element
    such as the email input field) or when the challenge iframe disappears.
    """
    logger.info("Waiting for Cloudflare challenge to clear...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # 1️⃣ Classic challenge forms – keep waiting if they exist
            if driver.find_elements(By.CSS_SELECTOR, "#challenge-form, .cf-challenge-form, [data-ray], .challenge-page"):
                logger.debug("Classic Cloudflare challenge detected, sleeping 2s")
                time.sleep(2)
                continue
            # 2️⃣ reCAPTCHA iframe – wait for it to disappear or be solved
            iframe = driver.find_element(By.CSS_SELECTOR, "iframe[title='Widget containing a Cloudflare security challenge']")
            # If we find the iframe, check whether the checkbox is already checked
            driver.switch_to.frame(iframe)
            try:
                # Try clicking the specific user-provided XPath first
                try:
                    captcha_checkbox = driver.find_element(By.XPATH, '//*[@id="ncOB5"]/div/label/input')
                    if captcha_checkbox.is_displayed() and captcha_checkbox.is_enabled():
                        if not captcha_checkbox.get_attribute('checked'):
                            captcha_checkbox.click()
                            logger.info("Clicked Cloudflare checkbox using custom XPath.")
                except Exception:
                    pass

                checkbox = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                # When solved, the checkbox gets the 'checked' attribute or aria-checked='true'
                if checkbox.get_attribute('checked') or checkbox.get_attribute('aria-checked') == 'true':
                    logger.info("reCAPTCHA checkbox solved.")
                    driver.switch_to.default_content()
                    return True
            except Exception:
                # No checkbox yet – maybe still loading
                pass
            driver.switch_to.default_content()
            # If iframe still present but not solved, wait a bit
            logger.debug("reCAPTCHA still unsolved, sleeping 2s")
            time.sleep(2)
            continue
        except Exception:
            # No iframe found – assume challenge gone. Verify page loaded by checking a known element.
            try:
                if driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[name='email']"):
                    logger.info("Target page loaded, Cloudflare cleared.")
                    return True
            except Exception:
                pass
        time.sleep(2)
    logger.warning("Timeout waiting for Cloudflare challenge.")
    return False


def run_polling_loop(driver, names: list, domain: str, max_votes: int = 0):
    vote_count = 0
    
    while True:
        if max_votes > 0 and vote_count >= max_votes:
            logger.info(f"Reached max votes ({max_votes}), stopping")
            break
            
        vote_count += 1
        email, name1, name2 = generate_email(names, domain)
        logger.info(f"\n{'='*50}")
        logger.info(f"VOTE #{vote_count} - Starting with: {email}")
        logger.info(f"{'='*50}")
        
        try:
            driver.get(URL)
            # Wait for Cloudflare challenge to be solved before proceeding
            wait_for_cloudflare(driver)
            wait_for_page_load(driver)
            time.sleep(0.5)
            scroll_to_bottom(driver)

            wait_and_send_keys(driver, By.CSS_SELECTOR, "input[type='email'], input[name='email']", email, description="email")
            # Click the label that wraps the consent checkbox
            wait_and_click(
                driver,
                By.XPATH,
                "//label[.//input[@type='checkbox']]",
                description="email consent checkbox (label wrapper)"
            )
            
            # Explicitly try to solve Cloudflare before clicking "Next"
            click_cloudflare_checkbox(driver)
            wait_for_cloudflare(driver)
            # Click the “Selanjutnya” button
            wait_and_click(
                driver,
                By.XPATH,
                "//footer//button[contains(., 'Selanjutnya')]",
                description="next button (xpath text)"
            )
            time.sleep(0.5)
            wait_for_page_load(driver)
            scroll_to_bottom(driver)
            time.sleep(0.5)
            # Click the label wrapper for the terms acceptance checkbox
            wait_and_click(
                driver,
                By.XPATH,
                "//div[contains(@class,'TermsAcceptance_agreementSection')]//label[.//input[@type='checkbox']]",
                description="terms acceptance checkbox (label wrapper)"
            )
            
            # Explicitly try to solve Cloudflare before clicking "Next" (terms page)
            click_cloudflare_checkbox(driver)
            wait_for_cloudflare(driver)
            # Click the “Selanjutnya” button (terms page)
            wait_and_click(
                driver,
                By.XPATH,
                "//footer//button[contains(., 'Selanjutnya')]",
                description="next button (xpath text)"
            )
            time.sleep(0.5)
            wait_for_page_load(driver)
            # Click "Masukkan Kode" button using robust XPath contains
            wait_and_click(
                driver,
                By.XPATH,
                "//button[contains(., 'Masukkan Kode')]",
                description="masukkan kode button"
            )

            # Delete all existing OTP emails so we only get the new one

            delete_sender_emails(sender=OTP_SENDER, timeout=30)
            time.sleep(6)
            logger.info("Waiting for OTP email...")
            otp = get_latest_otp(sender=OTP_SENDER, otp_patterns=OTP_PATTERNS, max_wait=30, poll_interval=5)

            if not otp:
                logger.error("Failed to get OTP after waiting, restarting loop")
                continue

            logger.info(f"OTP received: {otp}")
            input_otp_digits(driver, otp)


            # time.sleep(0.5)
            wait_for_page_load(driver)
            wait_and_click(
                driver,
                By.XPATH,
                "//button[contains(., 'Energi & Telekomunikasi')]",
                description="Energi & Telekomunikasi"
            )

            wait_for_page_load(driver)
            wait_and_click(
                driver,
                By.XPATH,
                "//button[contains(., 'Energy')]",
                description="Energy"
            )



            checkboxes = driver.find_elements(By.XPATH, "//label[.//input[@type='checkbox']]")
            visible_checkboxes = [cb for cb in checkboxes if cb.is_displayed() and cb.is_enabled()]
            if len(visible_checkboxes) >= 3:
                random_checks = random.sample(visible_checkboxes, 3)
            else:
                random_checks = visible_checkboxes
            for cb in random_checks:
                driver.execute_script("arguments[0].click();", cb)
                time.sleep(0.1)
            logger.info(f"Selected {len(random_checks)} checkboxes for Energy")
            scroll_to_bottom(driver)
            time.sleep(0.5)
            wait_for_page_load(driver)
            wait_and_click(
                driver,
                By.XPATH,
                "//button[contains(., 'Lanjut')]",
                description="Lanjut"
            )



            wait_for_page_load(driver)
            wait_and_click(
                driver,
                By.XPATH,
                "//div[contains(., 'PLN')]",
                description="PLN"
            )
            time.sleep(0.5)
            wait_and_click(
                driver,
                By.XPATH,
                "//button[contains(., 'Lanjut')]",
                description="Lanjut"
            )



            time.sleep(0.5)
            wait_for_page_load(driver)
            take_screenshot(driver, "upload-gform/bukti-PLN", f"{name1} {name2}_{email.split('@')[0]}.jpg")

            logger.info(f"Vote #{vote_count} completed successfully for {email}")
            time.sleep(60)

        except Exception as e:
            logger.error(f"Error in vote #{vote_count}: {type(e).__name__}: {e}")
            # Take a debug screenshot on error to see what's happening (especially for Captchas)
            take_screenshot(driver, "debug-errors", f"error_vote_{vote_count}_{email.split('@')[0]}.jpg")
            logger.info("Debug screenshot saved to debug-errors/")
            logger.info("Restarting loop in 1 second...")
            time.sleep(1)
            continue

        time.sleep(0.5)

def main():
    from dotenv import load_dotenv
    import argparse
    
    parser = argparse.ArgumentParser(description="Polling automation with IMAP OTP")
    parser.add_argument("-n", "--max-votes", type=int, default=0, 
                        help="Maximum number of votes (0 = unlimited)")
    parser.add_argument("--email-domain", type=str, 
                        help="Override email domain from IMAP_EMAIL")
    args = parser.parse_args()
    
    load_dotenv()
    
    if not IMAP_CONFIG["email"] or not IMAP_CONFIG["password"]:
        logger.error("ERROR: Please set IMAP_EMAIL and IMAP_PASSWORD environment variables")
        logger.info("Create .env file from .env.example template")
        return
    
    domain = "uplcid.space"
    names = load_names("nama-indonesia.txt")
    logger.info(f"Loaded {len(names)} names, domain: {domain}, max_votes: {args.max_votes or 'unlimited'}")
    
    driver = setup_driver()
    try:
        run_polling_loop(driver, names, domain, max_votes=args.max_votes)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
