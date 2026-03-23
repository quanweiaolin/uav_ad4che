from uav_training.mmdet_backend.detector import MMRotateDetector
from uav_pipeline.core.artifact import Artifact
from uav_pipeline.core.context import JobContext
from uav_pipeline.core.stage import Stage
from uav_pipeline.core.schema import Obj, FrameDatauav_training
import torch
import cv2 as cv


class DetectionStage(Stage):
    stage_name = "detection"
    
    def run(self, ctx: JobContext):
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.detector = MMRotateDetector(device=device)
        # stage_dir = ctx.get_stage_dir(self.stage_name)
        stabilization_path = ctx.resolve_input('stabilization','harris')
        cap = cv.VideoCapture(stabilization_path)
        res = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_id = int(cap.get(cv.CAP_PROP_POS_FRAMES)) - 1
            timestamp_ms = cap.get(cv.CAP_PROP_POS_MSEC)
            timestamp_s = timestamp_ms / 1000.0
            frame_data = FrameData(frame_id, timestamp_s)
            raw_detections = self.detector.infer(frame)
            for raw in raw_detections:
                obj = Obj(**raw, state='det')
                frame_data.objects.append(obj)
            res.append(frame_data)
            
        parquet_path, json_path = self.save_results(res = res, stage_dir = ctx.get_stage_dir(self.stage_name), base_name = "det_res")
        
        artifact = Artifact(
            stage=self.stage_name,
            name="oriented_rcnn_r50_fpn_1x_dota_le90-6d2b2ce0",
            local_path=str(parquet_path),
            kind ="detection_results",
            meta={
                
            },
            persistent=True  # frames 是否持久化: No
        )
        ctx.artifacts_register.register(artifact)
        ctx.logger.info(f"[{self.stage_name}] Artifact registered: {artifact.name}")
        
        