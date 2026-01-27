from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime
import json
import sys
sys.path.append("/opt/airflow")
from uav_pipeline.cli.run_single_video import run_single_video

WORKDIR = "/opt/airflow/uav_pipeline/workdir"
VIDEO_LIST_JSON = f"{WORKDIR}/manifest/video_list_20260120_jobs.json"
BASE_CONFIG = "/opt/airflow/uav_pipeline/config/base_config_yaml"
STAGE_CONFIG_DIR = "/opt/airflow/uav_pipeline/config/stages"
PIPELINE_CONFIG = "/opt/airflow/uav_pipeline/config/pipeline/perception.yaml"
ENV_CONFIG = "/opt/airflow/uav_pipeline/config/environments/local.yaml"
STORAGE = "local"
# "video_list_json": "/opt/airflow/uav_pipeline/workdir/manifest/video_list_20260120_jobs_airflow.json"



default_args = {"owner": "uav"}

with DAG(
    dag_id="uav_pipeline_distributed",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    default_args=default_args,
) as dag:
    def load_jobs(**context):
        conf = context["dag_run"].conf
        
        with open(conf["video_list_json"]) as f:
            jobs = json.load(f)["jobs"]
        return jobs

    from airflow.operators.python import PythonOperator

    load = PythonOperator(
        task_id="load_jobs",
        python_callable=load_jobs,
    )

    # 动态展开任务（Airflow 2.3+）
    from airflow.decorators import task

    @task
    def run_one_job(job):
        import subprocess
        cmd = [
            "python", "-m","uav_pipeline.cli.run_pipeline",
            "--video-path", job["video_path"],
            "--job-id", job["job_id"],
            "--workdir", WORKDIR
        ]
        subprocess.run(cmd, check=True)

    run_one_job.expand(job=load.output)