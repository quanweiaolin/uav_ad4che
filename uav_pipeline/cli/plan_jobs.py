# cli/plan_jobs.py
import json
from pathlib import Path
from uav_pipeline.utils.jobid_generator import generate_job_id
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Plan UAV video jobs (generate jobs.json)")
    parser.add_argument(
        "--video-list",
        required=True,
        help="Path to txt file, one video path per line",
    )
    return parser.parse_args()

def plan_jobs(video_list_file: Path):
    jobs = []
    output_json = video_list_file.parent / (video_list_file.stem +  '_jobs.json')
    with open(video_list_file) as f:
        for line in f:
            video = line.strip()
            if not video:
                continue

            job_id = generate_job_id(video)

            jobs.append({
                "job_id": job_id,
                "video_path": video,
            })

    output_json.parent.mkdir(parents=True, exist_ok=True)

    with open(output_json, "w") as f:
        json.dump(
            {
                "source": str(video_list_file),
                "job_count": len(jobs),
                "jobs": jobs,
            },
            f,
            indent=2,
        )

    print(f"Planned {len(jobs)} jobs → {output_json}")
args = parse_args()

plan_jobs(
    video_list_file=Path(args.video_list)
)