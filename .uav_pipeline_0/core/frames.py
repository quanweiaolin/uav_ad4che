import cv2
import os

class FrameExtractor:
    def __init__(self, fps=300):
        self.fps = fps

    def extract(self, job_context):
        """
        job_context: JobContext 对象
        输出：所有帧存储到 job_context.output_path 下
        """
        video_path = job_context.video_path
        output_path = job_context.output_path
        os.makedirs(output_path, exist_ok=True)

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError(f"无法打开视频 {video_path}")

        video_fps = cap.get(cv2.CAP_PROP_FPS)
        step = max(1, int(video_fps / job_context.fps))

        frame_count = 0
        saved_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_count % step == 0:
                filename = f"{job_context.video_name}_frame_{saved_count:05d}.jpg"
                filepath = os.path.join(output_path, filename)
                cv2.imwrite(filepath, frame)
                saved_count += 1
            frame_count += 1

        cap.release()
        return saved_count
    
    