# API作成
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from jose import jwt
from app.auth import hash_password, verify_password, create_access_token
from app import models


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

SECRET_KEY = "secret"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# DBセッション取得
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

# 消費税
def add_tax(price: int):
    return int(price * 1.1)


# 認証系
@app.post("/register")
def register(email: str, password: str, is_admin: bool = False, db: Session = Depends(get_db)):
    user = models.User(
        email=email, 
        password=hash_password(password),
        is_admin=is_admin
    )
    db.add(user)
    db.commit()
    return {"message": "登録完了"}


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="ログイン失敗")
    
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


# ユーザー取得
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except:
        raise HTTPException(status_code=401, detail="認証エラー")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return user


# 管理者
def get_current_admin(user: models.User = Depends(get_current_user)):
    
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="管理者のみ操作可能")
    return user


## 店側     
# 商品登録(管理者)
@app.post("/admin/products")
def create_product(
    name: str, 
    price: int, 
    stock: int, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    product = models.Product(name=name, price=price, stock=stock)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


# 商品一覧
@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    
    result = []
    for p in products:
        result.append({
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "price_with_tax": add_tax(p.price),
            "stock": p.stock
        })
        
    return result


# 商品詳細
@app.get("/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    return db.query(models.Product).filter(models.Product.id == product_id).first()


# 商品削除
@app.delete("/admin/products/{product_id}")
def delete_product(product_id: int, token: str, db: Session = Depends(get_db)):
    get_current_admin(token, db)
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    db.delete(product)
    db.commit()
    return {"message": "削除しました"}


## 顧客側
# 購入
@app.post("/buy")
def buy_product(
    product_id: int, 
    quantity: int, 
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="商品なし")
    if product.stock < quantity:
        raise HTTPException(status_code=400, detail="在庫不足")
    
    # 在庫減少
    product.stock -= quantity
    
    # 注文作成
    order = models.Order(user_id=user.id)
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # 注文詳細作成
    order_item = models.OrderItem(
        order_id=order.id,
        product_id=product.id,
        quantity=quantity,
        price=product.price
    )
    
    db.add(order_item)
    db.commit()
    
    return {
        "message": "購入完了",
        "order_id": order.id,
        "total_price": add_tax(product.price * quantity)
    }