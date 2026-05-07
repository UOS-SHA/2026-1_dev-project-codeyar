from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings

# ─── 비밀번호 해싱 ────────────────────────────────────────

def hash_password(plain: str) -> str:
    """평문 비밀번호 → bcrypt 해시 문자열"""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """평문 비밀번호와 bcrypt 해시를 비교"""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# ─── JWT 토큰 ─────────────────────────────────────────────

ACCESS_TOKEN_EXPIRE_MINUTES = 120  # 2시간


def create_access_token(user_id: str) -> str:
    """user_id를 sub 클레임에 담은 JWT 발급"""
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def decode_access_token(token: str) -> dict:
    """JWT를 디코딩하여 payload dict 반환. 실패 시 예외 발생."""
    return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
