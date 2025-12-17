import os

def get_project_root(marker="core"):
    """
    Returns the absolute path to the project's root directory by searching for a marker directory.
    This works no matter where it's called from in the project.
    """
    current_dir = os.path.abspath(os.path.dirname(__file__))
    while True:
        if marker in os.listdir(current_dir):
            return current_dir
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            # Reached filesystem root, marker not found
            raise RuntimeError(f"Project root marker '{marker}' not found.")
        current_dir = parent_dir
