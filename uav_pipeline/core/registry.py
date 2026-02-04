from typing import Dict, Tuple
from uav_pipeline.core.artifact import Artifact
from uav_pipeline.core.artifact_manager import ArtifactManager
import json
from pathlib import Path

class ArtifactRegistry:
    def __init__(self,context):
        self._artifacts: Dict[Tuple[str, str], Artifact] = {}
        self.context = context


    def register(self, artifact: Artifact, write_mode = True):
        key = (artifact.stage, artifact.name)

        if key in self._artifacts:
            raise ValueError(
                f"Artifact already registered: {artifact.kind}/{artifact.name}"
            )

        self._artifacts[key] = artifact
        if write_mode:
            self._write_manifest(artifact)

    def _write_manifest(self,artifact):
        manifest_path = Path(self.context.workdir) / "manifest.json"

        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text())
        else:
            manifest = {
            "job_id": self.context.job_id,
            "artifacts": []
        }
        artifact_dict = artifact.to_dict()
        updated = False
        for i, existing in enumerate(manifest["artifacts"]):
            if (
            existing.get("stage") == artifact_dict.get("stage")
            and existing.get("name") == artifact_dict.get("name")
            ):

                manifest["artifacts"][i] = artifact_dict
                updated = True
                break

        if not updated:
            manifest["artifacts"].append(artifact_dict)
            manifest_path.write_text(json.dumps(manifest, indent=2))


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
    
