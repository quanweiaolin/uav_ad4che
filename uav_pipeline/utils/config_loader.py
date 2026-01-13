import yaml
from pathlib import Path

def load_config(user_config_path: str = None) -> dict:
    with open(user_config_path, 'r') as f:
        config = yaml.safe_load(f) or {}
    return config

