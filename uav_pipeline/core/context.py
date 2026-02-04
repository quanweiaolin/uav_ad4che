from pathlib import Path
from typing import Optional
from uav_pipeline.core.registry import ArtifactRegistry
from uav_pipeline.utils.logger import PipelineLogger
from uav_pipeline.core.artifact import Artifact
from uav_pipeline.utils.config_loader import ConfigLoader
from uav_pipeline.config.adapters.stabilization_adapter import StabilizationConfigAdapter

class JobContext:
    def __init__(
        self,
        job_id: str,
        video_path: Path,
        workdir: Path,
        # artifacts_register:ArtifactRegistry,
        logger:PipelineLogger,
        base_config: str,
        stage_config_dir: str, 
        env_config: str,
        pipeline_config:str,
        debug_mode:bool
    ):
        self.job_id = job_id
        self.video_path = Path(video_path)
        self.workdir = Path(workdir) / "jobs" / job_id
        self.config = ConfigLoader(base_config, stage_config_dir, env_config, pipeline_config)
        self.artifacts_register = ArtifactRegistry(self)
        self.logger = logger(job_id)
        self.debug_mode = debug_mode
    
    def get_stage_dir(self, stage_name: str) -> Path:
        """deliver dir to each stage"""
        path = self.workdir / stage_name
        path.mkdir(exist_ok=True,parents=True)
        return path
    
    def get_artifact(self, stage: str, name: Optional[str] = None) -> Artifact:
        """
        Get artifact of a stage.
        If name=None, return the last registered artifact of the stage.
        """
        candidates = [
            a for a in self.artifacts_register.list()
            if a.stage == stage and (name is None or a.name == name)
        ]
        if not candidates:
            raise KeyError(f"No artifact found for stage '{stage}'")

        # 默认返回最新注册的
        return candidates[-1]

    # ----------------------
    # Input resolution
    # ----------------------
    

    def resolve_input(self, stage: str, name: Optional[str] = None) -> Path:
        """
        返回上游 stage 的 artifact.local_path 用于作为输入目录
        """
        art = self.get_artifact(stage, name)
        return art.local_path
    
    def get_adapter(self, stage_name: str):
        """Return adapter instance based on stage_name."""
        if stage_name == "stabilization":
            return StabilizationConfigAdapter(self.config.load_stage_config(stage_name))
        else:
            raise NotImplementedError(f"Adapter for stage '{stage_name}' is not implemented")