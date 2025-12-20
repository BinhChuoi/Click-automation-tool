import os
import json
from .AbstractToolDataStore import AbstractToolDataStore

class FileToolDataStore(AbstractToolDataStore):
    def __init__(self, storage_path=None):
        if storage_path is None:
            # Use the persistant/data folder as default
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.storage_path = os.path.join(base_dir, 'data')
        else:
            self.storage_path = storage_path
        # Ensure the storage directory exists
        os.makedirs(self.storage_path, exist_ok=True)

    def get_tool_filepath(self, tool_id):
        return os.path.join(self.storage_path, f"{tool_id}.json")

    def save_tool_data(self, tool_id, data):
        filepath = self.get_tool_filepath(tool_id)
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"Error saving tool data for '{tool_id}': {e}")

    def load_tool_data(self, tool_id):
        filepath = self.get_tool_filepath(tool_id)
        if not os.path.exists(filepath):
            return None
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading tool data for '{tool_id}': {e}")
            return None

    def delete_tool_data(self, tool_id):
        filepath = self.get_tool_filepath(tool_id)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"Tool data for '{tool_id}' deleted.")
                return True
            except OSError as e:
                print(f"Error deleting tool data file for '{tool_id}': {e}")
        return False

    def get_all_tool_data(self):
        """Returns a dict of all tool data loaded from storage."""
        all_data = {}
        if not os.path.exists(self.storage_path):
            return all_data
        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                tool_id = filename[:-5]
                try:
                    with open(os.path.join(self.storage_path, filename), 'r') as f:
                        all_data[tool_id] = json.load(f)
                except (json.JSONDecodeError, IOError):
                    pass
        return all_data
