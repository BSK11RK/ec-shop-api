# API作成
from fastapi import FastAPI

import app.models as models
from app.database import engine
from app.routers import auth, products, orders


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)