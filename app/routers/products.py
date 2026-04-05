from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import app.models as models
from app.core.deps import get_db, get_current_admin


router = APIRouter()


# 消費税
def add_tax(price: int):
    return int(price * 1.1)

      
## 店側     
# 商品登録(管理者)
@router.post("/admin/products")
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
@router.get("/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    
    return[
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "price_with_tax": add_tax(p.price),
            "stock": p.stock
        }
        for p in products
    ]
    
    
# 商品詳細
@router.get("/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="商品が存在しません")
    
    return {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "price_with_tax": add_tax(product.price),
        "stock": product.stock
    }
    
    
# 商品削除（管理者)
@router.delete("/admin/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="商品が存在しません")
    
    db.delete(product)
    db.commit()
    return {"message": "削除しました"}