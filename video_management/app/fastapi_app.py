import sys
sys.path.append('/mnt/DataBackup/Workspace/Docker/UAV')
from fastapi import FastAPI, Request
from video_management.app.crud import get_pending_videos, update_location, get_video_by_id
from video_management.app.utils import s3_client
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI()
BUCKET = "ad4che"

templates = Jinja2Templates(directory="templates")

class LocationUpdate(BaseModel):
    location: str

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    videos = get_pending_videos()
    return templates.TemplateResponse("index.html", {"request": request, "videos": videos})


@app.get("/video_url/{video_id}")
def video_url(video_id: str):
    video = get_video_by_id(video_id)
    url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET, "Key": video.minio_key},
        ExpiresIn=3600
    )
    return {"url": url}



@app.post("/update_location/{video_id}")
def update_loc(video_id: str, data: LocationUpdate):
    return {"success": update_location(video_id, data.location)}