import os
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt  # Import PyJWT
from app.models.user import Customer as User
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.services.token_blacklist_service import is_token_blacklisted

# Configuration (override via environment variables in production)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_ME_SUPER_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    data should include a 'sub' (subject) claim identifying the user.
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = now + expires_delta
    to_encode.update({
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token.
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT access token.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print('Decoded payload:', payload)
        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Access token has expired")
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError("Invalid access token")

def decode_refresh_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT refresh token.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Refresh token has expired")
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError("Invalid refresh token")

# Backward compatibility wrapper
def create_jwt_token(user_id: int) -> str:
    return create_access_token({"sub": str(user_id)})

# Optional helper to extract user id (assuming 'sub' holds it)
def get_user_id_from_token(token: str) -> Optional[int]:
    try:
        payload = decode_access_token(token)
        sub = payload.get("sub")
        return int(sub) if sub is not None else None
    except Exception:
        return None

def verify_jwt_token(token: str, db: Session) -> User | None:
    if is_token_blacklisted(db, token):
        return None
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            return None
        user = db.query(User).filter(User.id == int(user_id)).first()
        return user
    except jwt.InvalidTokenError:
        return None