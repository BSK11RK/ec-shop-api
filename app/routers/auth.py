# ログイン・登録
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import app.models as models
from app.core.security import hash_password, verify_password, create_access_token
from app.core.deps import get_db


router = APIRouter()
        
        
@router.post("/register")
def register(email: str, password: str, is_admin: bool = False, db: Session = Depends(get_db)):
    user = models.User(
        email=email,
        password=hash_password(password),
        is_admin=is_admin
    )
    db.add(user)
    db.commit()
    return {"message": "登録完了"}


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="ログイン失敗")
    
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}