import sys
sys.path.append("/mnt/DataBackup/Workspace/Docker/UAV/")
# from uav_pipeline.tasks.extract_frames import extract_frames_task
from uav_pipeline.core.frames import FrameExtractor
from uav_pipeline.core.job_context import JobContext
from uav_pipeline.core.storage import S3Storage

# ======================Video/
# 基本参数
# ======================
video_path = "/mnt/DataBackup/Workspace/DataEngineering/data/Video/output.MP4"
video_name = "output"
fps = 300

# 本地工作目录
local_output_dir = "/mnt/DataBackup/Workspace/DataEngineering/data/Data"

# ======================
# JobContext（只描述任务）
# ======================
job_context = JobContext(
    video_name=video_name,
    video_path=video_path,
    output_path=local_output_dir,
    storage_type="local",   # Extract 阶段不关心 S3
    fps=fps
)

# ======================
# 1. 本地跑帧提取
# ======================
extractor = FrameExtractor(fps=fps)
saved_count = extractor.extract(job_context)

print(f"总共保存 {saved_count} 帧到本地 {job_context.output_path}")

# ======================
# 2. S3 上传（pipeline 负责）
# ======================
storage = S3Storage(
    endpoint_url="http://192.168.50.125:9000",   # 按你的环境改
    access_key="n0O2iZ2O0Vg5CXkvC9Dg",
    secret_key="TMZseFokKYpSyVabBByTXWbE12PCX8gQLKtuNaz6",
    bucket_name="ad4che"
)

storage.put_dir(
    local_folder=job_context.output_path,
    remote_dir=f"frames/{video_name}"
)

print("✅ 已上传到 S3")
