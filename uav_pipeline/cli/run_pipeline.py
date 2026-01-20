# 所有入口（本地 / batch / airflow）
import sys 
sys.path.append("/mnt/DataBackup/Workspace/Docker/UAV")

import argparse
from uav_pipeline.pipeline.perception_pipeline import PIPELINE
from uav_pipeline.core.context import JobContext
from uav_pipeline.core.artifact_manager import ArtifactManager
from uav_pipeline.storage.storage_factory import create_storage
from uav_pipeline.core.registry import ArtifactRegistry
from uav_pipeline.utils.logger import PipelineLogger
from uav_pipeline.utils.config_loader import load_config
from uav_pipeline.utils.jobid_generator import generate_job_id


from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description="Run UAV Perception Pipeline")
    # Single Video
    parser.add_argument("--video-path", default=None, help="Input video file")
    parser.add_argument("--job-id", default=None, help="Optional job_id for single video")
    # Multi Videos
    parser.add_argument("--video-list", default=None, help="Text file with list of videos for batch mode")
    parser.add_argument("--max-workers", type=int, default=4, help="Max concurrent processes for batch mode")
    # General Settings
    parser.add_argument("--workdir", required=True, help="Working directory")
    parser.add_argument("--storage", default="local", choices=["local", "s3"], help="Storage backend")
    parser.add_argument("--config", default=None, help="Optional config YAML")

    args = parser.parse_args()
    if args.video_path and args.video_list:
        parser.error("Cannot specify both --video-path and --video-list")
    if not args.video_path and not args.video_list:
        parser.error("Must specify either --video-path or --video-list")

    return args




def main():
    args = parse_args()
    if args.video_path:
        # 单视频模式
        from uav_pipeline.cli.run_single_video import run_single_video
        if args.job_id is None:
            job_id = generate_job_id(args.video_path)
        else:
            job_id = args.job_id
        run_single_video(
            video_path=args.video_path,
            workdir=args.workdir,
            job_id=job_id,
            storage=args.storage,
            config=args.config
        )
    else:
        # 批量多视频模式
        from concurrent.futures import ProcessPoolExecutor,as_completed
        from uav_pipeline.cli.run_single_video import run_single_video
        import json
        with open(args.video_list, "r") as f:
            jobs_spec = json.load(f)
        jobs = jobs_spec["jobs"]
        results = []
        with ProcessPoolExecutor(max_workers=args.max_workers) as executor:
            future_to_job = {
                executor.submit(
                run_single_video,
                video_path=job["video_path"],
                workdir=args.workdir,
                job_id=job["job_id"],
                storage=args.storage,
                config=args.config,
                ): job
                for job in jobs
            }
            for future in as_completed(future_to_job):
                job = future_to_job[future]
                try:
                    result = future.result()
                    results.append(
                        {
                            "job_id": job["job_id"],
                            "status": "success",
                        }
                    )
                except Exception as e:
                    results.append(
                        {
                            "job_id": job["job_id"],
                            "status": "failed",
                            "error": str(e),
                        }
                    )



if __name__ == "__main__":
    main()