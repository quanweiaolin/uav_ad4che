from .local import LocalStorage
from .s3 import S3Storage

def create_storage(storage_type, config):
    """
    usage example: 
    storage = create_storage(job_context.storage_type, job_context.storage_config)
    storage.put_dir
    (
        local_folder=job_context.local_output_dir,
        remote_dir=f"{job_context.video_name}/frames"
    )
    """
    if storage_type == "local":
        return LocalStorage()
    elif storage_type == "s3":
        return S3Storage(
            endpoint_url=config["s3_endpoint"],
            access_key=config["s3_access_key"],
            secret_key=config["s3_secret_key"],
            bucket_name=config["s3_bucket"],
            region=config.get("s3_region", "us-east-1"),
        )
    else:
        raise ValueError(f"Unsupported storage type: {storage_type}")
    
