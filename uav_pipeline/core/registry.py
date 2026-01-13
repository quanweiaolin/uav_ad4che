from typing import Dict, Tuple
from uav_pipeline.core.artifact import Artifact
from uav_pipeline.core.artifact_manager import ArtifactManager
import json

class ArtifactRegistry:
    def __init__(self):
        self._artifacts: Dict[Tuple[str, str], Artifact] = {}

    def register(self, artifact: Artifact):
        key = (artifact.stage, artifact.name)

        if key in self._artifacts:
            raise ValueError(
                f"Artifact already registered: {artifact.kind}/{artifact.name}"
            )

        self._artifacts[key] = artifact

    def list(self):
        return list(self._artifacts.values())
    
    
    # def finalize(self, artifact_manager:ArtifactManager):
    #     """完成 job 的最终收尾操作"""

    #     # 1. 写 manifest.json
    #     manifest = {
    #         "job_id": self.job_id,
    #         "params": self.params,
    #         "output_dir": str(self.workdir),
    #     }

    #     manifest_path = self.workdir / "manifest.json"
    #     with open(manifest_path, "w") as f:
    #         json.dump(manifest, f, indent=2)

    #     # 2. 导出产物（复制到最终位置）
    #     artifact_manager.export_job(self)

    #     print(f"[Context] Finalized job {self.job_id}")
    
