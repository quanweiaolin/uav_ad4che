from dataclasses import dataclass
from pathlib import Path

@dataclass
class Artifact:
    stage: str # extract_frames, stabilization, inference, tracking, state_estimation, scenario_extraction
    name: str
    local_path: Path
    meta: dict
    persistent: bool

    
