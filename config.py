import os
from dotenv import load_dotenv

load_dotenv()

def get_env_int(key, default):
    value = os.getenv(key, str(default))
    # Remove inline comments and strip whitespace
    clean_value = value.split('#')[0].strip()
    try:
        return int(clean_value)
    except ValueError:
        return default

IMAP_CONFIG = {
    "host": os.getenv("IMAP_HOST", "imap.gmail.com"),
    "port": get_env_int("IMAP_PORT", 993),
    "email": os.getenv("IMAP_EMAIL", ""),
    "password": os.getenv("IMAP_PASSWORD", ""),
}

OTP_SENDER = os.getenv("OTP_SENDER", "noreply@danantaraindonesiacx100.com")

OTP_PATTERNS = [
    r'\b(\d{6})\b',
    r'\b(\d{4})\b',
    r'OTP[:\s]*(\d{4,6})',
    r'verification code[:\s]*(\d{4,6})',
    r'kode\s+verifikasi[:\s]*(\d{4,6})',
    r'kode\s+otp[:\s]*(\d{4,6})',
]

# Polling settings
EMAIL_DOMAIN = os.getenv("EMAIL_DOMAIN", "")  # Custom domain, empty = use IMAP_EMAIL domain
MAX_VOTES = get_env_int("MAX_VOTES", 0)
CLOUDFLARE_WAIT = get_env_int("CLOUDFLARE_WAIT", 60)
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
