import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 获取工作目录
WORK_DIR = Path(os.getenv("WORK_DIR", "./data"))
THUMB_DIR = WORK_DIR / "thumbnails"

# 自动创建物理目录
THUMB_DIR.mkdir(parents=True, exist_ok=True)


SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()