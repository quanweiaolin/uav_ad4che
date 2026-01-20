# 所有入口（本地 / batch / airflow）
import sys 
sys.path.append("/mnt/DataBackup/Workspace/Docker/UAV")

from pathlib import Path

from uav_pipeline.pipeline.perception_pipeline import PIPELINE
from uav_pipeline.core.context import JobContext
from uav_pipeline.core.artifact_manager import ArtifactManager
from uav_pipeline.storage.storage_factory import create_storage
from uav_pipeline.core.registry import ArtifactRegistry
from uav_pipeline.utils.logger import PipelineLogger
from uav_pipeline.utils.config_loader import load_config
from uav_pipeline.utils.jobid_generator import generate_job_id


def run_single_video(video_path, workdir, job_id=None, storage="local", config=None):
    if not job_id:
        raise ValueError("job_id must be provided")

    registry = ArtifactRegistry()
    ctx = JobContext(
        job_id=job_id,
        video_path=Path(video_path),
        workdir=Path(workdir),
        config=load_config(config),
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
    storage = create_storage(storage,ctx.config)
    manager = ArtifactManager(storage)
    manager.finalize_job(ctx)

    ctx.logger.info("Job {} completed successfully.".format(ctx.job_id))