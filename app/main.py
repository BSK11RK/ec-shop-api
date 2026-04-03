# API作成
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


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


## 店側     
# 商品登録
@app.post("/products")
def create_product(name: str, price: int, stock: int, db: Session = Depends(get_db)):
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
@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    db.delete(product)
    db.commit()
    return {"message": "削除しました"}


## 顧客側
# 購入
@app.post("/buy")
def buy_product(product_id: int, quantity: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    if not product:
        return {"error": "商品が存在しません"}
    if product.stock < quantity:
        return {"error": "在庫不足"}
    
    # 在庫減少
    product.stock -= quantity
    
    # 注文作成
    order = models.Order()
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
        "message": "注文完了",
        "order_id": order.id,
        "total_price": add_tax(product.price * quantity)
    }