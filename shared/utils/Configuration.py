


import os
from dynaconf import Dynaconf
from .PathResolver import get_project_root
import importlib.util

def load_configuration(filename='configuration.yaml'):
    spec = importlib.util.find_spec("shared.utils")
    folder_path = spec.submodule_search_locations[0]

    """
    Returns the shared Dynaconf settings object.
    """
    return Dynaconf(
        settings_files=[
            os.path.join(folder_path, filename),
            os.path.join(get_project_root(), '.env')
        ]
    )

