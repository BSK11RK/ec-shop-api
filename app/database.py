# DB設定
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


os.makedirs("data", exist_ok=True)

DATABASE_URL = "sqlite:///./data/ec.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()