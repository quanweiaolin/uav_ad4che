import os
import cv2 as cv
from pathlib import Path
from uav_pipeline.core.algo_registry import algo_registry
from uav_pipeline.core.artifact import Artifact
from uav_pipeline.core.context import JobContext
from uav_pipeline.core.stage import Stage
import numpy as np
from uav_pipeline.stages.stabilization.algorithms.video_stabilizer import VideoStabilizerV3 




class Stabilization_Stage(Stage):
    stage_name = "stabilization"

    def run(self, ctx: JobContext):
        input_video = ctx.video_path
        stage_dir = ctx.get_stage_dir(self.stage_name)
        output_video = stage_dir / (ctx.video_path.stem + "_stabi" + ctx.video_path.suffix)
        # mask_path = ctx.get_artifact("input","mask").local_path
        global_ref = ctx.get_artifact("input","reference_frame").local_path
        # stage_cfg = ctx.config.load_stage_config(self.stage_name)
        config_adapter = ctx.get_adapter(self.stage_name)
        params = config_adapter.get_algorithm_params()
        
        stabilizer = VideoStabilizerV3(
            input_video_path=str(input_video),
            output_video_path=str(output_video),
            # mask_img_path=str(mask_path),
            reference_frame_path=str(global_ref),
            params=params
        )
        stabilizer.stabilize()

        artifact = Artifact(
            stage=self.stage_name,
            name="harris",
            local_path=stage_dir,
            kind ="video",
            meta={
                "algorithms": ctx.config.load_stage_config(self.stage_name)['algorithm'],
                "params": params
            },
            persistent=False  # frames 是否持久化: No
        )
        ctx.artifacts_register.register(artifact)
        ctx.logger.info(f"[{self.stage_name}] Artifact registered: {artifact.name}")


