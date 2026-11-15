import base64
import binascii
import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AuthSession, UserAccount

ACCESS_TTL = timedelta(minutes=30)
PBKDF2_ROUNDS = 600_000
bearer = HTTPBearer(auto_error=False)

def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")

def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ROUNDS)
    return f"pbkdf2_sha256${PBKDF2_ROUNDS}${_b64(salt)}${_b64(digest)}"

def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, rounds, salt, expected = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256": return False
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), _unb64(salt), int(rounds))
        return hmac.compare_digest(actual, _unb64(expected))
    except (ValueError, TypeError):
        return False

def _secret() -> bytes:
    value = os.getenv("SECRET_KEY", "")
    if len(value) < 32:
        raise HTTPException(status_code=503, detail="Authentication is not configured: SECRET_KEY must contain at least 32 characters")
    return value.encode()

def issue_token(user: UserAccount, db: Session) -> str:
    now = datetime.now(timezone.utc)
    session_id = secrets.token_urlsafe(24)
    expiry = now + ACCESS_TTL
    db.add(AuthSession(id=session_id, user_id=user.id, expires_at=expiry))
    db.commit()
    payload = {"sub": user.id, "sid": session_id, "exp": int(expiry.timestamp())}
    body = _b64(json.dumps(payload, separators=(",", ":")).encode())
    signature = _b64(hmac.new(_secret(), body.encode(), hashlib.sha256).digest())
    return f"{body}.{signature}"

def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> UserAccount:
    unauthorized = HTTPException(status_code=401, detail="Valid bearer token required", headers={"WWW-Authenticate": "Bearer"})
    if credentials is None: raise unauthorized
    try:
        body, signature = credentials.credentials.split(".", 1)
        expected = _b64(hmac.new(_secret(), body.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected): raise unauthorized
        payload = json.loads(_unb64(body))
        if int(payload["exp"]) <= int(datetime.now(timezone.utc).timestamp()): raise unauthorized
    except HTTPException:
        raise
    except (ValueError, TypeError, KeyError, UnicodeDecodeError, binascii.Error, json.JSONDecodeError):
        raise unauthorized
    session = db.get(AuthSession, payload["sid"])
    user = db.get(UserAccount, int(payload["sub"]))
    if session is None or user is None or session.user_id != user.id or session.revoked_at is not None or not user.active:
        raise unauthorized
    return user

def require_roles(*roles: str):
    def dependency(user: UserAccount = Depends(get_current_user)) -> UserAccount:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Your role is not permitted to perform this action")
        return user
    return dependency

def revoke_session(user: UserAccount, token: str, db: Session) -> None:
    body, _ = token.split(".", 1)
    payload = json.loads(_unb64(body))
    session = db.get(AuthSession, payload["sid"])
    if session and session.user_id == user.id:
        session.revoked_at = datetime.now(timezone.utc)
        db.commit()
