


import os
from dynaconf import Dynaconf
from PathResolver import get_project_root

settings = Dynaconf(
    settings_files=[
        os.path.join(get_project_root(), 'configuration.yaml'),
        os.path.join(get_project_root(), '.env')
    ]
)

def load_configuration(filename='configuration.yaml'):
    """
    Returns the shared Dynaconf settings object.
    """
    return settings
