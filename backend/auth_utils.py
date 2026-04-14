from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def validate_target(target: str) -> bool:
    import re
    blocked = ["localhost", "127.", "192.168.", "10.", "0.0.0.0", "::1", "172.16.", "172.17.", "172.18.", "172.19.", "172.2", "172.30.", "172.31."]
    target_lower = target.lower()
    for b in blocked:
        if target_lower.startswith(b):
            return False
    ip_regex = r"^(\d{1,3}\.){3}\d{1,3}$"
    domain_regex = r"^[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]?(\.[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]?)*$"
    return bool(re.match(ip_regex, target) or re.match(domain_regex, target))