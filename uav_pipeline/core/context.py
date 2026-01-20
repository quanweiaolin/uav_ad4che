from pathlib import Path
from typing import Optional
from uav_pipeline.core.registry import ArtifactRegistry
from uav_pipeline.utils.logger import PipelineLogger
from uav_pipeline.core.artifact import Artifact

class JobContext:
    def __init__(
        self,
        job_id: str,
        video_path: Path,
        workdir: Path,
        config: dict,
        artifacts_register:ArtifactRegistry,
        logger:PipelineLogger,
    ):
        self.job_id = job_id
        self.video_path = Path(video_path)
        self.workdir = Path(workdir) / "jobs" / job_id
        self.config = config

        self.artifacts_register = artifacts_register
        self.logger = logger(job_id)
    
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