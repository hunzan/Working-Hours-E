import secrets
import os
from datetime import date
from cryptography.fernet import Fernet
import requests

def generate_query_code(length: int = 8) -> str:
    """
    產生好輸入的英數查詢碼（預設 8 位）。
    """
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # 排除易混淆 I, O, 0, 1
    return "".join(secrets.choice(alphabet) for _ in range(length))

def today_after_jan10(d: date) -> bool:
    """
    是否已經超過當年 1/10（含 1/11 起）。
    """
    jan10 = date(d.year, 1, 10)
    return d > jan10

def service_label(service_type: str) -> str:
    return {"orientation": "定向", "life": "生活"}.get(service_type, service_type)

def get_fernet() -> Fernet:
    """
    用環境變數 QUERY_CODE_KEY 當加密金鑰（Fernet key）。
    第一次可以先產生一把 key 放進環境變數。
    """
    key = os.environ.get("QUERY_CODE_KEY", "").strip()
    if not key:
        raise RuntimeError("缺少環境變數 QUERY_CODE_KEY（Fernet key）。")
    return Fernet(key.encode("utf-8"))

def encrypt_code(code_plain: str) -> str:
    f = get_fernet()
    return f.encrypt(code_plain.encode("utf-8")).decode("utf-8")

def decrypt_code(code_enc: str) -> str:
    f = get_fernet()
    return f.decrypt(code_enc.encode("utf-8")).decode("utf-8")

def send_reset_email(to_email: str, subject: str, body: str):
    api_key = os.environ.get("SENDGRID_API_KEY")
    sender = os.environ.get("MAIL_FROM")

    if not api_key or not sender:
        raise RuntimeError("缺少 SENDGRID_API_KEY 或 MAIL_FROM")

    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "personalizations": [{
            "to": [{"email": to_email}]
        }],
        "from": {"email": sender},
        "subject": subject,
        "content": [{
            "type": "text/plain",
            "value": body
        }]
    }

    r = requests.post(url, headers=headers, json=payload)
    if r.status_code >= 400:
        raise RuntimeError(f"SendGrid error {r.status_code}: {r.text}")