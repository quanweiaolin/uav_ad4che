from dataclasses import dataclass
from pathlib import Path

@dataclass
class Artifact:
    stage: str # extract_frames, stabilization, inference, tracking, state_estimation, scenario_extraction
    name: str # {algorithm}_{major.minor.patch}, e.g. yolov8n_v8.2.0, lane_change_v2.3, easy stage such as extract_frames is not required a name 
    kind: str # video,json,jpg
    local_path: Path
    meta: dict
    persistent: bool

    def to_dict(self):
        return {
            "stage": self.stage,
            "name": self.name,
            "local_path": str(self.local_path),   # Path → str
            "meta": self.meta,
            "persistent": self.persistent,
        }
