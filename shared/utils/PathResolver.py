import os

def get_project_root(marker_file=".env"):
    """
    Returns the absolute path to the project's root directory by searching for a marker file (default: pyproject.toml).
    This works no matter where it's called from in the project.
    """
    current_dir = os.path.abspath(os.path.dirname(__file__))
    while True:
        if os.path.isfile(os.path.join(current_dir, marker_file)):
            return current_dir
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            # Reached filesystem root, marker not found
            raise RuntimeError(f"Project root marker file '{marker_file}' not found.")
        current_dir = parent_dir
