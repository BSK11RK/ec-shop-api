import os
from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta


SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# パスワードハッシュ化
def hash_password(password: str):
    return pwd_context.hash(password)


# パスワード検証
def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


# JWT作成
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)