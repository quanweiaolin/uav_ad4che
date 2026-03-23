from abc import ABC,abstractmethod

class BaseStorage(ABC):
    
    @abstractmethod
    def put_file(local_path:str,remote_path:str):
        """Upload a single file to remote storage"""
        raise NotImplementedError
    
    @abstractmethod
    def get_file(remote_path:str,local_path:str):
        """Download a single file to local"""
        raise NotImplementedError
    
    @abstractmethod
    def put_dir(local_path:str,remote_path:str):
        """Upload a directory to remote storage"""
        raise NotImplementedError
    
    @abstractmethod
    def get_dir(remote_path:str,local_path:str):
        """Download a directory"""
        raise NotImplementedError
    

