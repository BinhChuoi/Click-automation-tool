import yaml
import os
from common.utils.PathResolver import get_project_root

def load_settings(filename='setting.yaml'):
    """
    Loads the settings YAML file from the project root/common directory.
    """
    path = os.path.join(get_project_root(), filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Settings file not found: {path}")
    with open(path, 'r') as f:
        return yaml.safe_load(f)
