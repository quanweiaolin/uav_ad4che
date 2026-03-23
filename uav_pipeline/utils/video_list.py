from pathlib import Path
from uav_pipeline.utils.jobid_generator import generate_job_id
import json

def load_video_list(manifest_path: str) -> list[str]:
    videos = []
    with open(manifest_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                videos.append(line)
    return videos

def generate_video_joblist(manifest_path: str):
    video_to_jobid = {}
    manifest_path_p = Path(manifest_path)
    job_manifest_path = str(manifest_path_p.parent / (manifest_path_p.stem + '_jobs.json'))
    with open(manifest_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                job_id = generate_job_id(line)
                video_to_jobid[line] = job_id
    with open(job_manifest_path, "w") as f:
        json.dump(video_to_jobid, f, indent=2)