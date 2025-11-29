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
    def get_tool_data(self):
        data = {
            'tool_id': self.tool_id,
            'version': self.version,
            'last_used': self.last_used,
            'tool_type': self.TOOL_NAME,
            'tool_configuration': self.tool_configuration or {
                'area' : { "x":0, "y":0, "width":0, "height":0}
            },
        }
        return data
    
    def _map_detected_objects(self, task_id, items):
        """Assigns a unique ID to each detected item."""
        for index, item in enumerate(items):
            item['id'] = f"{task_id}_obj_{index}"
        return items
    
    def _register_self(self):
        """Registers the tool instance with the ToolManager."""
        self.tool_manager.register_tool_instance(self.tool_id, self)

    def on_detection(self, task_id, capture_id, items):
        """Callback for when items are detected. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement on_detection")
    
    def change_mode(self, mode="main"):
        # Only create new tasks, loading is not supported without task_manager
        raise NotImplementedError("Subclasses must implement execute")

    def execute(self, capture_id, items):
        """Core execution logic for the tool. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement execute")

    def pause(self):
        """Pauses all tasks associated with this tool for the current mode."""
        for task in self.mode_tasks.get(self.mode, {}).values():
            task.pause()

    def resume(self):
        """Resumes all tasks associated with this tool for the current mode."""
        for task in self.mode_tasks.get(self.mode, {}).values():
            task.resume()

    def stop(self):
        """Stops all tasks for the current mode and removes the tool from the manager if all modes are stopped."""
        print(f"Stopping tool '{self.tool_id}' (mode: {self.mode})...")
        for task in self.mode_tasks.get(self.mode, {}).values():
            task.stop()
        self.mode_tasks[self.mode] = {}
        # If all modes are empty, unregister
        if all(not tasks for tasks in self.mode_tasks.values()):
            self.tool_manager.unregister_tool_instance(self.tool_id)

    def start(self, mode="main"):
        """Starts the detection task for the tool for the given mode, either by loading an existing one or creating new ones."""
        self.change_mode(mode=mode)

        if not self.mode_tasks.get(mode):
            print(f"Failed to start any tasks for tool '{self.tool_id}' (mode: {mode}).")
        else:
            for task_id in self.mode_tasks[mode]:
                print(f"Task '{task_id}' for tool '{self.tool_id}' (mode: {mode}) is running.")

        self.last_used = time.time()
        self.tool_manager.save_tool_data(self.tool_id, self.get_tool_data())
