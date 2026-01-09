import boto3
import os
from abc import ABC, abstractmethod
import shutil

class Storage(ABC):

    @abstractmethod
    def put_file(self, local_path: str, remote_path: str):
        pass

    @abstractmethod
    def put_dir(self, local_dir: str, remote_dir: str):
        pass



class LocalStorage(Storage):

    def put_file(self, local_path, remote_path):
        os.makedirs(os.path.dirname(remote_path), exist_ok=True)
        shutil.copy2(local_path, remote_path)

    def put_dir(self, local_dir, remote_dir):
        shutil.copytree(local_dir, remote_dir, dirs_exist_ok=True)



class S3Storage:
    
    def __init__(self, endpoint_url, access_key, secret_key, bucket_name, region="us-east-1"):
        self.bucket = bucket_name
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

    def put_file(self, local_path: str, remote_path: str):
        """
        remote_path == s3_key
        """
        self.s3_client.upload_file(
            local_path,
            self.bucket,
            remote_path
        )

    def put_dir(self, local_folder: str, remote_dir: str):
        for root, _, files in os.walk(local_folder):
            for file in files:
                local_file = os.path.join(root, file)
                relative_path = os.path.relpath(local_file, local_folder)

                s3_key = os.path.join(remote_dir, relative_path).replace("\\", "/")
                self.put_file(local_file, s3_key)