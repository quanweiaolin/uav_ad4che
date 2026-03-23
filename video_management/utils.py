import cv2
import hashlib
import os
import boto3
from video_management.database import THUMB_DIR
from pathlib import Path



s3_client = boto3.client(
    's3',
    endpoint_url=os.getenv("MINIO_ENDPOINT"),
    aws_access_key_id=os.getenv("MINIO_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("MINIO_SECRET_KEY")
)

def get_video_meta(path: str):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened(): return None
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    meta = {
        "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "fps": round(fps, 2),
        "duration": round(cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps, 2) if fps > 0 else 0,
        "size_mb": round(os.path.getsize(path) / (1024*1024), 2)
    }
    
    # 抽取第一帧作为缩略图
    thumb_name = f"{abs(hash(path))}.jpg"
    thumb_path = THUMB_DIR / thumb_name
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(str(thumb_path), cv2.resize(frame, (320, 180)))
    cap.release()
    
    return meta, thumb_name

def list_local_videos(root_path):
    valid_exts = ['.mp4', '.mov', '.avi', '.mkv']
    return [str(p) for p in Path(root_path).rglob("*") if p.suffix.lower() in valid_exts]