from typing import Dict, Tuple
from uav_pipeline.core.artifact import Artifact

class ArtifactRegistry:
    def __init__(self):
        self._artifacts: Dict[Tuple[str, str], Artifact] = {}

    def register(self, artifact: Artifact):
        key = (artifact.kind, artifact.name)

        if key in self._artifacts:
            raise ValueError(
                f"Artifact already registered: {artifact.kind}/{artifact.name}"
            )

        self._artifacts[key] = artifact

    def list(self):
        return list(self._artifacts.values())