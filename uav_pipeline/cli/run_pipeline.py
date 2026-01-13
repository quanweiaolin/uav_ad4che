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

from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description="Run UAV Perception Pipeline")
    parser.add_argument("--job-id", required=True, help="Unique job identifier")
    parser.add_argument("--video-path", required=True, help="Input video file")
    parser.add_argument("--workdir", required=True, help="Working directory")
    parser.add_argument("--storage", default="local", choices=["local", "s3"], help="Storage backend")
    parser.add_argument("--config", default=None, help="Optional config YAML")
    return parser.parse_args()


def main():
    args = parse_args()
    registry = ArtifactRegistry()
    
    ctx = JobContext(
        job_id=args.job_id,
        video_path=Path(args.video_path),
        workdir=Path(args.workdir),
        config=load_config(args.config),
        artifacts_register=registry,
        logger=PipelineLogger
    )

    

    # try:
    for stage in PIPELINE:
        ctx.logger.info(f"Starting stage: {stage.__class__.__name__}")
        stage.run(ctx)
    # except Exception as e:
    #     ctx.logger.error(f"Pipeline failed at stage {stage}: {str(e)}")
    #     sys.exit(1)

    storage = create_storage(args.storage,ctx.config)
    manager = ArtifactManager(storage)
    manager.finalize_job(ctx)

    ctx.logger.info("Job completed successfully.")

if __name__ == "__main__":
    main()