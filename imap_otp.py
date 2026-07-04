import imaplib
import email
import re
import time
import socket
import logging
from email.header import decode_header
from typing import Optional
from email.message import EmailMessage
from typing import List, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from config import IMAP_CONFIG


def decode_mime_header(header: str) -> str:
    """Decode MIME encoded headers."""
    if not header:
        return ""
    decoded_parts = decode_header(header)
    decoded_parts = []
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            decoded_parts.append(part.decode(encoding or 'utf-8', errors='ignore'))
        else:
            decoded_parts.append(part)
    return ''.join(decoded_parts)


def extract_otp_from_email(body: str, patterns: List[str] = None) -> Optional[str]:
    """Extract OTP code from email body using regex patterns."""
    if patterns is None:
        patterns = [
            r'\b(\d{6})\b',
            r'\b(\d{4})\b',
            r'OTP[:\s]*(\d{4,6})',
            r'verification code[:\s]*(\d{4,6})',
            r'kode\s+verifikasi[:\s]*(\d{4,6})',
            r'kode\s+otp[:\s]*(\d{4,6})',
            r'kode\s+verifikasi[:\s]*(\d{4,6})',
        ]
    
    for pattern in patterns:
        matches = re.findall(pattern, body, re.IGNORECASE)
        if matches:
            return matches[-1]
    return None


def get_email_body(msg: EmailMessage) -> str:
    """Extract plain text body from email message."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))
            
            if content_type == "text/plain" and "attachment" not in content_disposition:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or 'utf-8'
                    body += payload.decode(charset, errors='ignore')
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or 'utf-8'
            body = payload.decode(charset, errors='ignore')
    return body


def connect_imap() -> imaplib.IMAP4_SSL:
    """Connect to IMAP server."""
    mail = imaplib.IMAP4_SSL(IMAP_CONFIG['host'], IMAP_CONFIG['port'])
    mail.login(IMAP_CONFIG['email'], IMAP_CONFIG['password'])
    return mail


def select_folder(mail: imaplib.IMAP4_SSL, folder: str = "INBOX") -> None:
    """Select IMAP folder."""
    mail.select(folder)


def delete_email(mail: imaplib.IMAP4_SSL, email_id: bytes) -> None:
    """Mark email as deleted and expunge."""
    mail.store(email_id, '+FLAGS', '\\Deleted')
    mail.expunge()


def search_emails(mail: imaplib.IMAP4_SSL, sender: str = None,
                  since_days: int = 1, unseen_only: bool = True) -> List[bytes]:
    """Search for emails from specific sender within last N days."""
    criteria = []
    if unseen_only:
        criteria.append('UNSEEN')
    if sender:
        criteria.append(f'FROM "{sender}"')
    if since_days > 0:
        from datetime import datetime, timedelta
        date = (datetime.now() - timedelta(days=since_days)).strftime("%d-%b-%Y")
        criteria.append(f'SINCE "{date}"')

    criteria_str = ' '.join(criteria) or 'ALL'
    status, messages = mail.search(None, criteria_str)
    return messages[0].split() if status == 'OK' else []


def fetch_latest_otp(mail: imaplib.IMAP4_SSL, sender: str = None,
                       otp_patterns: List[str] = None,
                       max_wait: int = 60,
                       poll_interval: int = 5) -> Optional[str]:
    """
    Fetch latest OTP from email.

    Args:
        mail: IMAP connection
        sender: Email sender to filter (e.g., "noreply@example.com")
        otp_patterns: Custom regex patterns for OTP extraction
        max_wait: Maximum seconds to wait for email
        poll_interval: Seconds between polling attempts

    Returns:
        OTP code string or None if not found
    """
    start_time = time.time()

    while time.time() - start_time < max_wait:
        email_ids = search_emails(mail, sender, since_days=1, unseen_only=False)

        if email_ids:
            latest_id = email_ids[-1]
            status, msg_data = mail.fetch(latest_id, '(RFC822)')

            if status == 'OK':
                msg = email.message_from_bytes(msg_data[0][1])
                body = get_email_body(msg)
                otp = extract_otp_from_email(body, otp_patterns)

                if otp:
                    delete_email(mail, latest_id)
                    return otp

        time.sleep(poll_interval)

    return None


def fetch_otp_once(mail: imaplib.IMAP4_SSL, sender: str = None,
                    otp_patterns: List[str] = None) -> Optional[str]:
    """Fetch OTP from latest email once (no polling)."""
    email_ids = search_emails(mail, sender, since_days=1, unseen_only=False)

    if not email_ids:
        return None

    latest_id = email_ids[-1]
    status, msg_data = mail.fetch(latest_id, '(RFC822)')

    if status == 'OK':
        msg = email.message_from_bytes(msg_data[0][1])
        body = get_email_body(msg)
        otp = extract_otp_from_email(body, otp_patterns)
        if otp:
            delete_email(mail, latest_id)
            return otp

    return None


def close_connection(mail: imaplib.IMAP4_SSL) -> None:
    """Close IMAP connection."""
    try:
        mail.close()
        mail.logout()
    except Exception:
        pass


def get_latest_otp(sender: str = None,
                    otp_patterns: List[str] = None,
                    max_wait: int = 60,
                    poll_interval: int = 5) -> Optional[str]:
    """
    Convenience function to get latest OTP with auto-connect.

    Args:
        sender: Email sender to filter (e.g., "noreply@example.com")
        otp_patterns: Custom regex patterns for OTP extraction
        max_wait: Max seconds to wait for email
        poll_interval: Seconds between polling

    Returns:
        OTP code string or None
    """
    mail = connect_imap()
    try:
        select_folder(mail)
        return fetch_latest_otp(mail, sender, otp_patterns, max_wait, poll_interval)
    finally:
        close_connection(mail)
def mark_sender_emails_seen(sender: str = None) -> None:
    """Mark all emails from sender as seen so only new ones appear as UNSEEN."""
    mail = connect_imap()
    try:
        select_folder(mail)
        email_ids = search_emails(mail, sender, since_days=1, unseen_only=False)
        if email_ids:
            for eid in email_ids:
                mail.store(eid, '+FLAGS', '\\Seen')
    finally:
        close_connection(mail)


def delete_sender_emails(sender: str = None, timeout: int = 30) -> None:
    """Delete all emails from specific sender with a timeout."""
    original_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout)
    try:
        mail = connect_imap()
        try:
            select_folder(mail)
            email_ids = search_emails(mail, sender, since_days=1, unseen_only=False)
            if email_ids:
                for eid in email_ids:
                    delete_email(mail, eid)
        finally:
            close_connection(mail)
    except socket.timeout:
        logger.warning(f"Timeout occurred while deleting emails from {sender}")
    except Exception as e:
        logger.error(f"Error deleting emails from {sender}: {e}")
    finally:
        socket.setdefaulttimeout(original_timeout)


if __name__ == "__main__":
    import sys
    sender = sys.argv[1] if len(sys.argv) > 1 else None
    otp = get_latest_otp(sender=sender)
    if otp:
        print(otp)
    else:
        print("OTP not found", file=sys.stderr)
        sys.exit(1)
