# 認証チェック
import os
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt

import app.models as models
from app.database import SessionLocal


SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
# ログインユーザー
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except:
        raise HTTPException(status_code=401, detail="認証エラー")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return user


# 管理者
def get_current_admin(
    user: models.User = Depends(get_current_user)
):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="管理者のみ操作可能")
    return user