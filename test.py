import undetected_chromedriver as uc
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

URL = "https://danantaraindonesiacx100.com/polls/cx100-danantara"
EMAIL = "your-email@example.com"

options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")

driver = uc.Chrome(options=options, version_main=149)
driver.set_window_size(390, 844)

driver.get(URL)
driver.implicitly_wait(10)

print("Page title:", driver.title)

time.sleep(1)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
print("Scrolled to bottom")

time.sleep(2)

try:
    email_input = driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[name='email'], input[id*='email']")
    email_input.clear()
    email_input.send_keys(EMAIL)
    print(f"Email filled: {EMAIL}")
except Exception as e:
    print(f"Email input not found: {e}")

time.sleep(15)
driver.quit()