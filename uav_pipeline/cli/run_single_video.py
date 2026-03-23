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
# from uav_pipeline.utils.config_loader import ConfigLoader
from uav_pipeline.utils.jobid_generator import generate_job_id
# from expired.register_algos import register_algos 
from uav_pipeline.core.job_input import JobInput


def run_single_video(video_path, workdir, base_config, stage_config_dir, env_config, pipeline_config, job_id=None, storage="local", manual_ref_frame = None, mask = None, debug_mode = False):
    
    if not job_id:
        raise ValueError("job_id must be provided")
    # registry = ArtifactRegistry()
    # register_algos()
    ctx = JobContext(
        job_id=job_id,
        video_path=Path(video_path),
        workdir=workdir,
        # artifacts_register=registry,
        logger=PipelineLogger,
        base_config = base_config,
        stage_config_dir = stage_config_dir,
        pipeline_config=pipeline_config,
        env_config = env_config,
        debug_mode = debug_mode
    )
    job_input = JobInput(ctx.video_path, manual_ref_frame)
    job_input.prepare_reference_frame(ctx.workdir)
    job_input.register_to(ctx)

    # try:
    for stage in PIPELINE:
        ctx.logger.info(f"Starting stage: {stage.__class__.__name__}")
        if ctx.debug_mode:
            stage.mock(ctx)
        else:
            stage.run(ctx)
        
    # except Exception as e:
    #     ctx.logger.error(f"Pipeline failed at stage {stage}: {str(e)}")
    #     sys.exit(1)
    storage = create_storage(storage,ctx.config)
    manager = ArtifactManager(storage)
    manager.finalize_job(ctx)

    ctx.logger.info("Job {} completed successfully.".format(ctx.job_id))