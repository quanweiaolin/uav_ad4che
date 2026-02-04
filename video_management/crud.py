from sqlalchemy.orm import Session
from video_management.models import Video
from video_management.utils import extract_basic_info, generate_temp_thumbnail

def sync_disk_to_db(db: Session, found_paths: list):
    for p in found_paths:
        # 1. 检查数据库是否已记录
        db_video = db.query(Video).filter(Video.path == p).first()
        
        if not db_video:
            # 2. 自动扫视频元数据
            v_meta = extract_basic_info(p)
            if not v_meta: continue
            
            # 3. 自动生成临时预览图
            thumb_path = generate_temp_thumbnail(p)
            
            # 4. 插入数据库
            new_video = Video(
                path=p,
                width=v_meta['width'],
                height=v_meta['height'],
                fps=v_meta['fps'],
                duration=v_meta['duration'],
                size_mb=v_meta['size_mb'],
                info={"thumbnail": thumb_path}, # 预览图存 JSON
                labels={} # 初始标注为空
            )
            db.add(new_video)
    db.commit()


def update_video_labels(db: Session, path: str, new_labels: dict):
    db_video = db.query(Video).filter(Video.path == path).first()
    if db_video:
        # 获取旧标签，并用新标签合并（防止覆盖掉原有的 location 或 scene）
        current_labels = dict(db_video.labels) if db_video.labels else {}
        current_labels.update(new_labels)
        db_video.labels = current_labels
        db.commit()
    return db_video

def bulk_update_video_labels(db: Session, paths: list, label_data: dict):
    for path in paths:
        # 逐个合并更新，确保不覆盖每个视频特有的 location
        update_video_labels(db, path, label_data)