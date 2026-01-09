from uav_pipeline.core.stage import Stage
from uav_pipeline.core.artifact import Artifact

class ExtractFramesStage(Stage):
    def run(self, context, inputs):
        return 0