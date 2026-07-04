from config import IMAP_CONFIG, OTP_SENDER, OTP_PATTERNS
from imap_otp import connect_imap, select_folder, fetch_otp_once, close_connection

def test_imap_connection():
    print("Testing IMAP connection...")
    print(f"Host: {IMAP_CONFIG['host']}")
    print(f"Port: {IMAP_CONFIG['port']}")
    print(f"Email: {IMAP_CONFIG['email']}")
    
    if not IMAP_CONFIG['email'] or not IMAP_CONFIG['password']:
        print("ERROR: Please set IMAP_EMAIL and IMAP_PASSWORD in .env")
        return False
    
    try:
        mail = connect_imap()
        print("Connected successfully!")
        select_folder(mail)
        print("Selected INBOX")
        
        otp = fetch_otp_once(mail, sender=OTP_SENDER, otp_patterns=OTP_PATTERNS)
        if otp:
            print(f"Found OTP: {otp}")
        else:
            print("No OTP found in recent emails")
        
        close_connection(mail)
        print("Connection closed")
        return True
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    test_imap_connection()
