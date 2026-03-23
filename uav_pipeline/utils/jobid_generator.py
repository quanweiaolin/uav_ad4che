from datetime import datetime
import uuid
from pathlib import Path

def generate_job_id(video_path: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d")
    video_name = Path(video_path).stem
    unique_id = str(uuid.uuid4())[:8]
    return f"{video_name}_{timestamp}_{unique_id}"