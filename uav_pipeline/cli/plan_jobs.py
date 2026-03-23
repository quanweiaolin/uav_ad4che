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

def get_airflow_path(path : str = None,base_dir: str = "/opt/airflow/uav_pipeline/input") -> str:
    if base_dir:
        # 替换原来的根路径
        path = str(Path(base_dir) / Path(path).name)
    return str(path)

def plan_jobs(video_list_file: Path):
    jobs = []
    jobs_airflow = []
    output_json = video_list_file.parent / (video_list_file.stem +  '_jobs.json')
    output_json_airflow = video_list_file.parent / (video_list_file.stem +  '_jobs_airflow.json')
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
            jobs_airflow.append({
                "job_id": job_id,
                "video_path": get_airflow_path(video),
            })

    output_json.parent.mkdir(parents=True, exist_ok=True)

    with open(output_json, "w") as f:
        json.dump(
            {
                "source": str(video_list_file),
                "usage": "Linux",
                "job_count": len(jobs),
                "jobs": jobs,
            },
            f,
            indent=2,
        )
    with open(output_json_airflow,"w") as f:
        json.dump(
            {
                "source": str(video_list_file),
                "usage":"airflow",
                "job_count": len(jobs_airflow),
                "jobs": jobs_airflow,
            },
            f,
            indent=2,
        )

    print(f"Planned {len(jobs)} jobs → {output_json} and {output_json_airflow}")

args = parse_args()

plan_jobs(
    video_list_file=Path(args.video_list)
)