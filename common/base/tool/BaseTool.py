import time
import os

class BaseTool:
    """Base class for all tools, providing common functionality."""
    TOOL_NAME = "BaseTool"

    def __init__(self, tool_manager, tool_data=None, tool_configuration=None):
        self.tool_manager = tool_manager
        if tool_data:
            self.tool_id = tool_data.get('tool_id', f"{self.TOOL_NAME}_{int(time.time()*1000)}")
            self.version = tool_data.get('version', '1.0')
            self.last_used = tool_data.get('last_used', time.time())
            self.tool_configuration = tool_data.get('tool_configuration', self.get_default_configuration())
        else:
            self.tool_id = f"{self.TOOL_NAME}_{int(time.time()*1000)}"
            self.version = '1.0'
            self.last_used = time.time()
            self.tool_configuration = tool_configuration or self.get_default_configuration()
        self.mode_tasks = {"main": {}}
        self.mode = "main"
        self.heartbeat_id = None
        self._register_self()

    @staticmethod
    def get_default_configuration():
        config = {
            'base_priority': 10
        }
        return config
    def get_configuration_value(self, key, default=None):
        if self.tool_configuration and key in self.tool_configuration:
            return self.tool_configuration[key]
        return default
