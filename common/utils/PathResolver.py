import sys
import os

def get_project_root():
    """
    Returns the absolute path to the project's root directory.
    It assumes the project root is the first entry in sys.path,
    which should be set by the main application entry point.
    """
    # Return the absolute path to the root of the project (the folder containing 'common')
    current_file = os.path.abspath(__file__)
    common_dir = os.path.dirname(current_file)
    project_root = os.path.dirname(common_dir)
    return project_root
