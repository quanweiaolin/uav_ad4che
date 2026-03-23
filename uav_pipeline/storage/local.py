import os
import shutil
from .base import BaseStorage

class LocalStorage(BaseStorage):
    def put_file(self, local_path:str, remote_path:str):
        # local shall be file, not dir
        if not os.path.isfile(local_path):
            raise ValueError(f"local_path '{local_path}' is not a file")
        # ext shall be same
        if os.path.splitext(local_path)[1] != os.path.splitext(remote_path)[1]:
            raise ValueError(
            f"Extension mismatch: local '{os.path.splitext(local_path)[1]}' vs remote '{os.path.splitext(remote_path)[1]}'. "
            f"remote_path must include the same file extension."
            )

        """Upload a single file to remote storage"""
        os.makedirs(os.path.dirname(remote_path),exist_ok=True)
        shutil.copy2(local_path,remote_path)

    def get_file(self, remote_path:str, local_path:str):
        # remote shall be file, not dir
        if not os.path.isfile(remote_path):
            raise ValueError(f"remote_path '{remote_path}' is not a file")
        # ext shall be same
        if os.path.splitext(local_path)[1] != os.path.splitext(remote_path)[1]:
            raise ValueError(
                f"Extension mismatch: remote '{os.path.splitext(remote_path)[1]}' vs local '{os.path.splitext(local_path)[1]}'. "
                f"remote_path must include the same file extension."
            )
        """Download a single file from remote storage"""
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        shutil.copy2(remote_path, local_path)
        
    def put_dir(self, local_dir:str, remote_dir:str):
        # local shall be dir, not file
        if not os.path.isdir(local_dir):
            raise ValueError(f"local_path '{local_dir}' is not a dir")
        # # ext shall be same
        # if os.path.splitext(local_dir)[1] != os.path.splitext(remote_dir)[1]:
        #     raise ValueError(
        #     f"Extension mismatch: local '{os.path.splitext(local_dir)[1]}' vs remote '{os.path.splitext(remote_dir)[1]}'. "
        #     f"remote_path must include the same file extension."
        #     )
        
        """Upload a dir to remote storage"""
        os.makedirs(remote_dir, exist_ok=True)
        shutil.copytree(local_dir,remote_dir,dirs_exist_ok=True)

    def get_dir(self, remote_dir:str, local_dir:str):
        # remote shall be dir, not file
        if not os.path.isdir(remote_dir):
            raise ValueError(f"remote_path '{remote_dir}' is not a dir")
        # # ext shall be same
        # if os.path.splitext(local_dir)[1] != os.path.splitext(remote_dir)[1]:
        #     raise ValueError(
        #         f"Extension mismatch: remote '{os.path.splitext(remote_dir)[1]}' vs local '{os.path.splitext(local_dir)[1]}'. "
        #         f"remote_path must include the same file extension."
        #     )
        os.makedirs(local_dir, exist_ok=True)
        shutil.copytree(remote_dir,local_dir,dirs_exist_ok=True)

        