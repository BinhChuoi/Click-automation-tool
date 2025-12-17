import os
import json
from .AbstractToolDataStore import AbstractToolDataStore

class FileToolDataStore(AbstractToolDataStore):
    def __init__(self, storage_path):
        self.storage_path = storage_path

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
