
import secrets
import hmac
import hashlib
import os
from datetime import datetime, timedelta, timezone


# 必須設定固定且保密的伺服器金鑰
# 正式環境與本地端應使用不同金鑰
SECRET_KEY = os.environ.get("EMAIL_VERIFICATION_SECRET")

if not SECRET_KEY:
    raise RuntimeError(
        "尚未設定 EMAIL_VERIFICATION_SECRET"
    )


# 驗證碼有效期限：10 分鐘
CODE_EXPIRE_MINUTES = 10

# 最多允許輸入錯誤 5 次
MAX_VERIFY_ATTEMPTS = 5

# 重新寄送冷卻時間：60 秒
RESEND_COOLDOWN_SECONDS = 60


def generate_verification_code():
    """
    產生安全的六位數驗證碼
    """
    return f"{secrets.randbelow(1000000):06d}"


def hash_verification_code(user_id, code):
    """
    使用 HMAC-SHA256 保護驗證碼
    """
    message = f"{user_id}:{code}".encode("utf-8")

    return hmac.new(
        SECRET_KEY.encode("utf-8"),
        message,
        hashlib.sha256
    ).hexdigest()


def verify_code_hash(user_id, code, stored_hash):
    """
    比較使用者輸入的驗證碼是否正確
    """
    expected_hash = hash_verification_code(user_id, code)

    return hmac.compare_digest(
        expected_hash,
        stored_hash
    )


def get_expiration_time():
    """
    取得驗證碼的到期時間（UTC）
    """
    return (
        datetime.now(timezone.utc)
        + timedelta(minutes=CODE_EXPIRE_MINUTES)
    ).replace(tzinfo=None)
