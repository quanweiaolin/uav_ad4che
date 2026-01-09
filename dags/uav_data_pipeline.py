# from airflow.decorators import dag, task
from airflow.sdk import dag, task

# from airflow.utils.dates import days_ago
import pendulum
import os
import sys
sys.path.append(os.path.join(os.environ.get('AIRFLOW_HOME', '/opt/airflow')))
from uav_pipeline.tasks.extract_frames import extract_frames_task



start_date = pendulum.datetime(2025,1,1,tz="UTC")
@dag(
    schedule="@daily",
    start_date=start_date,
    catchup=False,
    tags=["uav"]
)
def uav_daily_pipeline():
    # ======================
    # 基本参数，Docker Volumen
    # ======================
    video_path = "/opt/airflow/data/Video/output.MP4"
    video_name = "output"
    fps = 300

    # 本地工作目录，Docker Volumen
    local_output_dir = "/opt/airflow/data/Data"
    
    extract_task = extract_frames_task(
        video_name=video_name,
        video_path=video_path,
        output_path=local_output_dir,
        fps=fps,
        storage_type="local"
    )


    return extract_task



uav_pipeline = uav_daily_pipeline()


