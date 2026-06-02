import datetime
from typing import Optional

import bcrypt

# Patch passlib bcrypt incompatibility with newer bcrypt versions (>=4.0.0)
if not hasattr(bcrypt, "__about__"):

    class BcryptAbout:
        __version__ = bcrypt.__version__

    bcrypt.__about__ = BcryptAbout()

# Patch bcrypt.hashpw and checkpw to avoid 72-byte limit ValueErrors in newer bcrypt versions
original_hashpw = bcrypt.hashpw


def patched_hashpw(password, salt):
    password_bytes = password.encode("utf-8") if isinstance(password, str) else password
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    return original_hashpw(password_bytes, salt)


bcrypt.hashpw = patched_hashpw

if hasattr(bcrypt, "checkpw"):
    original_checkpw = bcrypt.checkpw

    def patched_checkpw(password, hashed):
        password_bytes = password.encode("utf-8") if isinstance(password, str) else password
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        return original_checkpw(password_bytes, hashed)

    bcrypt.checkpw = patched_checkpw

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User
from app.schemas import TokenData

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme definition
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str: str = payload.get("sub")
        role: str = payload.get("role")
        if user_id_str is None:
            raise credentials_exception
        user_id = int(user_id_str)
        token_data = TokenData(user_id=user_id, role=role)
    except (JWTError, ValueError):
        raise credentials_exception

    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="The user does not have enough privileges")
    return current_user
