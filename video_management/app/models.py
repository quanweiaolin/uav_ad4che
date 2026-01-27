from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os
# DB_Path = "/opt/airflow/video_management/Data/video_catalog.db"

DB_Path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"Data"),"video_catalog.db")

engine = create_engine(f"sqlite:///{DB_Path}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Video(Base):
    __tablename__ = "videos"
    id = Column(String, primary_key=True)
    minio_key = Column(String, nullable=False)
    duration = Column(Float)
    width = Column(Integer)
    height = Column(Integer)
    fps = Column(Float)
    size_mb = Column(Float)
    location = Column(String)            # 需要人工填写
    ingest_status = Column(String)       # raw / need_manual / ready
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)