import os
from fastapi import FastAPI, Depends, Request, Body
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

from video_management.models import Base, Video
from video_management.utils import get_video_meta, list_local_videos, THUMB_DIR




# 数据库初始化
engine = create_engine(os.getenv("DATABASE_URL"))
SessionLocal = sessionmaker(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
    # if THUMB_DIR.exists():
    #     import shutil
    #     shutil.rmtree(THUMB_DIR)

app = FastAPI(lifespan=lifespan)

app.mount("/thumbs", StaticFiles(directory=str(THUMB_DIR)), name="thumbs")

# 替换为：
BASE_PACKAGE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_PACKAGE_DIR / "templates"

print(f"DEBUG: 模板绝对路径是 {TEMPLATE_PATH}")
if not TEMPLATE_PATH.exists():
    raise RuntimeError(f"致命错误：找不到模板目录 {TEMPLATE_PATH}")

templates = Jinja2Templates(directory=str(TEMPLATE_PATH))

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.get("/")
async def index(request: Request, db: Session = Depends(get_db)):
    # 过滤逻辑：只要 location 或 scene 没填，就显示出来
    # PostgreSQL JSONB 检查 key 是否存在的语法： ? 
    sql = text("NOT (labels ? 'location') OR NOT (labels ? 'scene')")
    videos = db.query(Video).filter(sql).all()
    return templates.TemplateResponse("index.html", {"request": request, "videos": videos})

@app.post("/scan")
async def scan(db: Session = Depends(get_db)):
    root_path = os.getenv("Local_SCAN_PATH")
    paths = list_local_videos(root_path)
    count = 0
    for p in paths:
        if not db.query(Video).filter(Video.path == p).first():
            res = get_video_meta(p)
            if res:
                meta, thumb = res
                new_v = Video(path=p, **meta, info={"thumb": thumb}, labels={})
                db.add(new_v)
                count += 1
    db.commit()
    return {"msg": f"扫盘完成，新增 {count} 条"}

@app.post("/update")
async def update(payload: dict = Body(...), db: Session = Depends(get_db)):
    path = payload.get("path")
    new_labels = payload.get("labels")
    
    video = db.query(Video).filter(Video.path == path).first()
    if video:
        # 核心修复逻辑：
        # 如果前端传来的 labels 是空的 {}，说明是要重置
        if not new_labels:
            video.labels = {}  # 彻底清空 JSONB 字段
            print(f"♻️ 已重置视频状态: {path}")
        else:
            # 否则执行增量合并
            current = dict(video.labels) if video.labels else {}
            current.update(new_labels)
            video.labels = current
            print(f"💾 已更新视频标注: {path}")
            
        db.commit()
        return {"status": "ok"}
    return {"status": "error", "msg": "视频不存在"}, 404

@app.get("/manage")
async def manage_page(request: Request, db: Session = Depends(get_db)):
    # 过滤逻辑：labels 字段中同时包含 location 和 scene 的记录
    sql = text("labels ? 'location' AND labels ? 'scene'")
    videos = db.query(Video).filter(sql).order_by(Video.created_at.desc()).all()
    return templates.TemplateResponse("manage.html", {"request": request, "videos": videos})