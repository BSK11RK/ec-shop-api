from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import app.models as models
from app.core.deps import get_db, get_current_user


router = APIRouter()

        
# 消費税
def add_tax(price: int):
    return int(price * 1.1)

        
## 顧客側
# 購入
@router.post("/buy")
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
    
    
# 注文履歴
@router.get("/orders")
def get_orders(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    orders = db.query(models.Order).filter(models.Order.user_id == user.id).all()
    
    result = []
    
    for order in orders:
        items = db.query(models.OrderItem).filter(models.OrderItem.order_id == order.id).all()
        
        order_items = []
        total = 0
        
        for item in items:
            product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
            
            subtotal = item.price * item.quantity
            total += subtotal
            
            order_items.append({
                "product_name": product.name,
                "quantity": item.quantity,
                "price": item.price,
                "subtotal": subtotal,
                "subtotal_with_tax": add_tax(subtotal)
            })
            
        result.append({
            "order_id": order.id,
            "created_at": order.created_at,
            "total_price": total,
            "total_price_with_tax": add_tax(total),
            "items": order_items
        })

    return result