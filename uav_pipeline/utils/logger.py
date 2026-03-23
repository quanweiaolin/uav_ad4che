
import logging
import sys
from pathlib import Path

class PipelineLogger:
    """
    Unified logger for pipeline runs, preventing duplicated handlers,
    supporting console + file logging, and adding job_id prefix automatically.
    """

    def __init__(self, job_id: str, log_dir: Path = None):
        self.job_id = job_id
        self.logger = logging.getLogger(f"pipeline.{job_id}")
        self.logger.setLevel(logging.INFO)

        # 防止重复添加 handler
        if not self.logger.handlers:
            self._setup_handlers(log_dir)

    def _setup_handlers(self, log_dir):
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter(
                fmt="[%(asctime)s] [%(levelname)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
        )
        self.logger.addHandler(console_handler)

        if log_dir:
            log_dir.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_dir / f"{self.job_id}.log")
            file_handler.setFormatter(
                logging.Formatter(
                    fmt="[%(asctime)s] [%(levelname)s] %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S"
                )
            )
            self.logger.addHandler(file_handler)

    def info(self, msg: str):
        self.logger.info(f"[{self.job_id}] {msg}")

    def warn(self, msg: str):
        self.logger.warning(f"[{self.job_id}] {msg}")

    def error(self, msg: str):
        self.logger.error(f"[{self.job_id}] {msg}")