from pathlib import Path
import cv2 as cv
import tempfile
import shutil
from uav_pipeline.core.artifact import Artifact
import os

class JobInput:
    def __init__(self, video_path: str, manual_ref: str = None, mask_path: str = None):
        self.video_path = Path(video_path)
        self.manual_ref = Path(manual_ref) if manual_ref else None
        self.mask_path = Path(mask_path) if mask_path else None
        # self.extra_inputs = extra_inputs or {}

        self.ref_frame_path: Path = None  # 最终 reference frame 路径

    def prepare_reference_frame(self, workdir: str):
        workdir = Path(workdir)
        workdir.mkdir(parents=True, exist_ok=True)
        if self.manual_ref:
            if not self.manual_ref.exists():
                raise FileNotFoundError(f"Manual reference not found: {self.manual_ref}")
            if self.manual_ref.suffix.lower() in [".jpg", ".png", ".jpeg"]:
                # 图像直接使用
                temp_ref = workdir /f"{Path(self.manual_ref).stem}_ref.jpg"
                shutil.copy2(self.manual_ref, temp_ref)
                self.ref_frame_path = temp_ref
            else:
                # 视频，提取第一帧
                cap = cv.VideoCapture(str(self.manual_ref))
                ret, frame = cap.read()
                cap.release()
                if not ret:
                    raise RuntimeError(f"Cannot read first frame from {self.manual_ref}")
                temp_ref = workdir / f"{Path(self.manual_ref).stem}_ref.jpg"
                cv.imwrite(str(temp_ref), frame)
                self.ref_frame_path = temp_ref
        else:
            # 默认自己视频第一帧
            cap = cv.VideoCapture(str(self.video_path))
            ret, frame = cap.read()
            cap.release()
            if not ret:
                raise RuntimeError(f"Cannot read first frame from {self.video_path}")
            temp_ref = workdir / f"{self.video_path.stem}_ref.jpg"
            cv.imwrite(str(temp_ref), frame)
            self.ref_frame_path = temp_ref
    def register_to(self, ctx):
        """注册 artifacts"""
        if self.ref_frame_path:
            ref_art = Artifact(
                stage="input",   # 或者 "job_input"，看你设计
                name="reference_frame",
                kind="reference pic input",              # 也可以根据实际文件类型自动判断
                local_path=self.ref_frame_path,
                meta={
                    "reference_frame": self.manual_ref if self.manual_ref else f"default fisrt frame"
                },
                persistent=False,        # 暂时不持久化
            )
            ctx.artifacts_register.register(ref_art)

        if self.mask_path:
            mask_art = Artifact(
                stage="input",
                name="mask",
                kind="mask pic input",
                local_path=self.mask_path,
                meta={},
                persistent=False,
            )
            ctx.artifacts_register.register(mask_art)