from sqlalchemy import Column, String, DateTime, Float, Integer, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Video(Base):
    __tablename__ = 'videos'
    
    path = Column(String, primary_key=True, index=True)
    width = Column(Integer)
    height = Column(Integer)
    fps = Column(Float)
    duration = Column(Float)
    size_mb = Column(Float)
    
    # info 存储非业务元数据：{"thumb": "xxx.jpg", "codec": "h264"}
    info = Column(JSONB, default={}, server_default='{}')
    # labels 存储业务标注：{"location": "黑龙江", "scene": "highway"}
    labels = Column(JSONB, default={}, server_default='{}')
    
    created_at = Column(DateTime, server_default=func.now())