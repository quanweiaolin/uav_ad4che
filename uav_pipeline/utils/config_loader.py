from pathlib import Path
import yaml

def load_yaml(path):
    if not Path(path).exists():
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}

class ConfigLoader:
    def __init__(self, base_config_path, stage_config_dir, env_config_path=None, pipeline_config_path=None):
        self.base_config = load_yaml(base_config_path)
        self.stage_dir = Path(stage_config_dir)
        if env_config_path:
            self.env_config = load_yaml(env_config_path)
        if pipeline_config_path:
            self.pipeline_config = load_yaml(env_config_path)
    def load_stage_config(self, stage_name):
        stage_file = self.stage_dir / f"{stage_name}.yaml"
        config = load_yaml(stage_file)
        return config


    