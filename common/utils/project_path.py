import sys
import os

def get_project_root():
    """
    Returns the absolute path to the project's root directory.
    It assumes the project root is the first entry in sys.path,
    which should be set by the main application entry point.
    """
    # sys.path[0] is the directory of the script being run.
    return sys.path[0]
