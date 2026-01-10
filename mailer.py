import os
import requests

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
MAIL_FROM = os.environ.get("MAIL_FROM")

# mailer.py
import os
import requests

def send_reset_email(to_email: str, subject: str, body: str) -> None:
    api_key = (os.environ.get("SENDGRID_API_KEY") or "").strip()
    mail_from = (os.environ.get("MAIL_FROM") or "").strip()

    if not api_key or not mail_from:
        raise RuntimeError("Missing SENDGRID_API_KEY or MAIL_FROM")

    payload = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": mail_from},
        "subject": subject,
        "content": [{"type": "text/plain", "value": body}],
    }

    r = requests.post(
        "https://api.sendgrid.com/v3/mail/send",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=10,
    )

    if r.status_code >= 400:
        raise RuntimeError(f"SendGrid error {r.status_code}: {r.text[:200]}")

