from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

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


# 商品一覧 + 検索 + ページネーション
@router.get("/products")
def get_products(
    keyword: str = None, 
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    query = db.query(models.Product)
    
    # 検索
    if keyword:
        query = query.filter(models.Product.name.contains(keyword))
        
    # 総件数
    total = query.count()
        
    # ページネーション
    offset = (page - 1) * limit
    products = query.offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": [
            {
                "id": p.id,
                "name": p.name,
                "price": p.price,
                "price_with_tax": add_tax(p.price),
                "stock": p.stock
            }
            for p in products
        ]
    }
    
    
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


# 商品更新（管理者)
@router.put("/admin/products/{product_id}")
def update_product(
    product_id: int,
    name: str = None,
    price: int = None,
    stock: int = None,
    db: Session = Depends(get_db),
    admmin: models.User = Depends(get_current_admin)
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="商品が存在しません")
    
    # 更新
    if name is not None:
        product.name = name
    if price is not None:
        product.price = price
    if stock is not None:
        product.stock = stock
        
    db.commit()
    db.refresh(product)
    return product
    

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