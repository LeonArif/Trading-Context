from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "supersecretjwtkeygantilah"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Argon2 password hasher
ph = PasswordHasher()

# Pre-hashed password untuk "password123"
# Hash: $argon2id$v=19$m=65536,t=3,p=4$...
fake_users_db = {
    "LeonArif": {
        "username": "LeonArif",
        # Hash untuk password: password123
        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$zwWjjyzAm4tCUyeeXRCIFw$WvzW2LGByKzgEGiF9dmCPOOu4r/BpYffWUr7kfoc2kk"
    }
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify password using Argon2"""
    try:
        ph.verify(hashed, plain)
        return True
    except VerifyMismatchError:
        return False


def authenticate_user(username: str, password: str):
    """Authenticate user with username and password"""
    user = fake_users_db.get(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = fake_users_db.get(username)
    if user is None:
        raise credentials_exception
    return user