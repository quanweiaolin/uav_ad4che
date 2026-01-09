class JobContext:
    """
    封装视频处理任务的输入参数
    """
    def __init__(self, video_name, video_path, output_path, storage_type="s3", fps=30):
        self.video_name = video_name      # 视频文件名，不带路径
        self.video_path = video_path      # 视频所在路径
        self.output_path = output_path    # 输出文件夹路径（s3 bucket 或本地目录）
        self.storage_type = storage_type  # "s3" 或 "local"
        self.fps = fps

