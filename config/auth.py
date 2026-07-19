"""
Demo authentication for company walkthroughs.

Production path later: replace verify_credentials() with SSO / Azure AD.
"""
from __future__ import annotations

# Demo only — replace before real deployment
DEMO_USERS = {
    "admin": {"password": "admin123", "name": "Platform Admin", "role": "admin"},
    "demo": {"password": "demo123", "name": "Developer Demo", "role": "viewer"},
}

SESSION_USER_KEY = "dss_user"
SESSION_AUTH_KEY = "dss_authenticated"


def verify_credentials(username: str, password: str) -> dict | None:
    user = DEMO_USERS.get(username.strip().lower())
    if not user:
        return None
    if user["password"] != password:
        return None
    return {"username": username.strip().lower(), "name": user["name"], "role": user["role"]}
