from pathlib import Path
from typing import List
from uav_pipeline.core.stage import Stage
from uav_pipeline.core.context import JobContext
from uav_pipeline.core.artifact import Artifact

import cv2

class ExtractFramesStage(Stage):
    """
    Stage: Extract frames from video.
    工程化要点：
        - 自动使用 JobContext 分配的 stage 目录
        - 拆帧时记录帧路径
        - 生成 Artifact 并注册
        - 支持日志输出
        - 可配置 fps / max_frames
    """

    def __init__(self, fps: int = 300, max_frames: int = None):
        self.fps = fps
        self.max_frames = max_frames

    def run(self, ctx: JobContext):
        stage_name = "extract_frames"
        stage_dir = ctx.get_stage_dir(stage_name)
        video_path = ctx.video_path

        ctx.logger.info(f"[{stage_name}] Start extracting frames from {video_path}")

        cap = cv2.VideoCapture(str(video_path))
        frame_count = 0
        

        success, frame = cap.read()
        while success:
            if self.max_frames and frame_count >= self.max_frames:
                break

            if frame_count % max(1, int(cap.get(cv2.CAP_PROP_FPS) / self.fps)) == 0:
                frame_filename = f"frame_{frame_count:06d}.jpg"
                frame_path = stage_dir / frame_filename
                cv2.imwrite(str(frame_path), frame)
                

            frame_count += 1
            success, frame = cap.read()

        cap.release()
        ctx.logger.info(f"[{stage_name}] Extracted {frame_count} frames")



        artifact = Artifact(
            stage=stage_name,
            name="extract_frames",
            local_path=stage_dir,
            meta={
                "num_frames": frame_count,
                "fps": self.fps,
                "video": str(video_path)
            },
            persistent=False  # frames 是否持久化: No
        )

        ctx.artifacts_register.register(artifact)
        ctx.logger.info(f"[{stage_name}] Artifact registered: {artifact.name}")

        


