# Pipeline (No Algorithmus)


# from uav_pipeline.stages.extract_frames.stage import ExtractFramesStage
from uav_pipeline.stages.detection.stage import DetectionStage
# from uav_pipeline.stages.tracking.stage import TrackingStage
# from uav_pipeline.stages.state_estimation.stage import StateStage
# from uav_pipeline.stages.scenario_extraction.stage import ScenarioStage
from uav_pipeline.stages.stabilization.stage import Stabilization_Stage

PIPELINE = [
    Stabilization_Stage(),
    DetectionStage(),
    # TrackingStage(),
    # StateStage(),
    # ScenarioStage()
]