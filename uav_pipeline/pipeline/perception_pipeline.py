# Pipeline (No Algorithmus)


from uav_pipeline.stages.extract_frames.stage import ExtractFramesStage
from uav_pipeline.stages.inference.stage import InferenceStage
from uav_pipeline.stages.tracking.stage import TrackingStage
from uav_pipeline.stages.state_estimation.stage import StateStage
from uav_pipeline.stages.scenario_extraction.stage import ScenarioStage

PIPELINE = [
    ExtractFramesStage(),
    # InferenceStage(),
    # TrackingStage(),
    # StateStage(),
    # ScenarioStage()
]