import os
import json
import time
from common.utils.project_path import get_project_root
from common.helper.browser import BrowserManager

class _ProfileManager:
    """Manages user profiles, which are collections of tool configurations."""

    def __init__(self, storage_path=os.path.join('storageData', 'profiles')):
        self.active_profile_name = None
        self.active_profile_data = None

        project_root = get_project_root()
        self.storage_path = os.path.join(project_root, storage_path)

        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
            print(f"Created profile storage directory at: {self.storage_path}")

    def get_profile_filepath(self, profile_name):
        """Constructs the full file path for a given profile's data file."""
        return os.path.join(self.storage_path, f"{profile_name}.json")

    def save_profile_data(self, profile_name, data):
        """Saves a profile's data to a JSON file."""
        filepath = self.get_profile_filepath(profile_name)
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Profile data for '{profile_name}' saved.")
        except IOError as e:
            print(f"Error saving profile data for '{profile_name}': {e}")

    def load_profile_data(self, profile_name):
        """Loads a profile's data from a JSON file."""
        filepath = self.get_profile_filepath(profile_name)
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading profile data for '{profile_name}': {e}")
            return None

    def load_or_create_profile(self, profile_name):
        """Loads profile data, or creates it if it doesn't exist."""
        data = self.load_profile_data(profile_name)
        if data is None:
            print(f"No existing data for profile '{profile_name}'. Creating new profile.")

            data = {
                'profile_name': profile_name,
                'chrome_profile_name': profile_name,
                'tool_ids': [],
                'version': '1.0',
                'last_used': time.time()
            }
            self.save_profile_data(profile_name, data)
        return data

    def load_profile(self, profile_name):
        """Clear old profile tools, Loads a profile, opens the associated browser, and starts tools"""
        print(f"Loading profile: '{profile_name}'...")
        profile_data = self.load_or_create_profile(profile_name)

        if not profile_data:
            print(f"Failed to load or create profile '{profile_name}'.")
            return

        self.active_profile_name = profile_name
        self.active_profile_data = profile_data

        return self.active_profile_data

    def add_tool_to_active_profile(self, tool_id):
        """Adds a tool ID to the currently active profile and saves it."""
        if not self.active_profile_name or not self.active_profile_data:
            print("No active profile to add the tool to.")
            return

        if tool_id not in self.active_profile_data['tool_ids']:
            self.active_profile_data['tool_ids'].append(tool_id)
            self.active_profile_data['last_used'] = time.time()
            self.save_profile_data(self.active_profile_name, self.active_profile_data)
            print(f"Added tool '{tool_id}' to profile '{self.active_profile_name}'.")

    def remove_tool_from_active_profile(self, tool_id):
        """Removes a tool ID from the currently active profile and saves it."""
        if not self.active_profile_name or not self.active_profile_data:
            print("No active profile to remove the tool from.")
            return

        if tool_id in self.active_profile_data['tool_ids']:
            self.active_profile_data['tool_ids'].remove(tool_id)
            self.active_profile_data['last_used'] = time.time()
            self.save_profile_data(self.active_profile_name, self.active_profile_data)
            print(f"Removed tool '{tool_id}' from profile '{self.active_profile_name}'.")

ProfileManager = _ProfileManager()
