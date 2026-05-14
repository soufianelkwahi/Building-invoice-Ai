import hashlib
import hmac
from app.core.config import settings


def verify_api_key(api_key: str) -> bool:
    return hmac.compare_digest(api_key, settings.api_key)


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()
