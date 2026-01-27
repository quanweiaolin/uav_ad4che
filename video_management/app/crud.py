from video_management.app.models import Video, engine
from video_management.app.utils import extract_video_meta, s3_client
from video_management.app.models import Video, SessionLocal
# from sqlalchemy.orm import sessionmaker
import uuid, tempfile
from datetime import datetime



def register_video(minio_key, bucket="ad4che"):
    """注册 MinIO 上的视频到 SQLite"""
    session = SessionLocal()
    try:
        # 避免重复注册
        existing = session.query(Video).filter(Video.minio_key==minio_key).first()
        if existing:
            return existing.id

        # 下载临时文件
        with tempfile.NamedTemporaryFile(suffix=".mp4") as tmp:
            s3_client.download_file(bucket, minio_key, tmp.name)
            meta = extract_video_meta(tmp.name)

        # 写入 SQLite
        video = Video(
            id=str(uuid.uuid4()),
            minio_key=minio_key,
            duration=meta["duration"],
            width=meta["width"],
            height=meta["height"],
            fps=meta["fps"],
            size_mb=meta["size_mb"],
            ingest_status="need_manual",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(video)
        session.commit()
        return video.id
    finally:
        session.close()

def get_pending_videos():
    session = SessionLocal()
    try:
        return session.query(Video).filter(Video.location==None).all()
    finally:
        session.close()

def get_video_by_id(video_id):
    session = SessionLocal()
    try:
        return session.query(Video).filter(Video.id == video_id).first()
    finally:
        session.close()

def update_location(video_id, location):
    session = SessionLocal()
    try:
        video = session.query(Video).filter(Video.id == video_id).first()
        if not video:
            return False
        video.location = location
        video.ingest_status = "ready"
        video.updated_at = datetime.utcnow()
        session.commit()
        return True
    finally:
        session.close()