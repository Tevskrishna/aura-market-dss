"""
Demo + production-ready auth gate.

- Default demo users remain available for mentor walkthroughs.
- Override passwords via env (AURA_ADMIN_PASSWORD / AURA_DEMO_PASSWORD).
- Optional SHA-256 hashes (AURA_*_PASSWORD_HASH + AURA_AUTH_SALT) for Cloud secrets.
- SSO / Azure AD remains the Wave-7 target — slot behind verify_credentials().
"""
from __future__ import annotations

import hashlib
import hmac

from config import settings

SESSION_USER_KEY = "dss_user"
SESSION_AUTH_KEY = "dss_authenticated"


def _sha256(password: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()


def _password_ok(password: str, *, plain: str, hashed: str) -> bool:
    if hashed and settings.AUTH_SALT:
        return hmac.compare_digest(_sha256(password, settings.AUTH_SALT), hashed)
    return hmac.compare_digest(password, plain)


DEMO_USERS = {
    "admin": {
        "name": "Platform Admin",
        "role": "admin",
        "plain": settings.AUTH_ADMIN_PASSWORD,
        "hash": settings.AUTH_ADMIN_PASSWORD_HASH,
    },
    "demo": {
        "name": "Developer Demo",
        "role": "viewer",
        "plain": settings.AUTH_DEMO_PASSWORD,
        "hash": settings.AUTH_DEMO_PASSWORD_HASH,
    },
}


def verify_credentials(username: str, password: str) -> dict | None:
    user = DEMO_USERS.get(username.strip().lower())
    if not user:
        return None
    if not _password_ok(password, plain=user["plain"], hashed=user["hash"]):
        return None
    return {"username": username.strip().lower(), "name": user["name"], "role": user["role"]}


def hash_password(password: str) -> str:
    """Helper for ops — generate hash to paste into Streamlit secrets."""
    salt = settings.AUTH_SALT or "change-me"
    return _sha256(password, salt)
