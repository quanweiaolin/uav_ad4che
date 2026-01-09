from airflow.sdk import task
from uav_pipeline.core.frames import FrameExtractor
from uav_pipeline.core.job_context import JobContext
from uav_pipeline.core.storage import S3Storage

@task()
def extract_frames_task(video_name: str, video_path: str, output_path: str, fps: int = 30, storage_type: str = "s3") -> int:
    """
    Airflow Task Wrapper
    """
    job_context = JobContext(
        video_name=video_name,
        video_path=video_path,
        output_path=output_path,
        storage_type=storage_type,
        fps=fps
    )
    extractor = FrameExtractor(fps=fps)
    saved_count = extractor.extract(job_context)
    print(f"总共保存 {saved_count} 帧到 {job_context.output_path}")

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


    return saved_count