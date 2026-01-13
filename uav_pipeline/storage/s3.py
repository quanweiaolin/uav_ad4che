import os
import boto3
from .base import BaseStorage

class S3Storage(BaseStorage):
    def __init__(self, endpoint_url, access_key, secret_key, bucket_name, region="us-east-1"):
        '''init cloud storage'''
        self.bucket = bucket_name
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

    def put_file(self, local_path: str, remote_path: str):
        self.s3_client.upload_file(local_path, self.bucket, remote_path)

    
    def get_file(self, remote_path:str, local_path:str):
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        self.s3_client.download_file(self.bucket, remote_path, local_path)

    def put_dir(self, local_dir: str, remote_dir: str):
        for root, _, files in os.walk(local_dir):
            for file in files:
                local_file = os.path.join(root, file)
                rel = os.path.relpath(local_file, local_dir)
                remote_path = os.path.join(remote_dir, rel).replace("\\", "/")
                self.put_file(local_file, remote_path)

    def get_dir(self, remote_dir: str, local_dir: str):
        paginator = self.s3_client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket, Prefix=remote_dir):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                rel = os.path.relpath(key, remote_dir)
                local_file = os.path.join(local_dir, rel)
                os.makedirs(os.path.dirname(local_file), exist_ok=True)
                self.get_file(key, local_file)