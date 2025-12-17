
import os
import time
import queue
import threading
from concurrent.futures import ThreadPoolExecutor
from shared.utils.Signals import CreateTool, StartTool, DestroyTool

class _ToolManager:
    # region Initialization and Core Lifecycle
    def __init__(self):
        """Initializes the ToolManager, setting up paths and default states."""
        self.active_tools = {}
        self.last_event_time = None
        self.event_queue = queue.Queue()
        self._event_worker_thread = None
        self._stop_event_worker = threading.Event()


    def reset(self):
        self.clear_all_tools() 
        self.active_tools = {}
        self.last_event_time = None

    def start(self):
        # Connect signals to enqueue events instead of direct processing
        CreateTool.connect(self._on_create_tool_signal)
        StartTool.connect(self._on_start_tool_signal)
        DestroyTool.connect(self._on_destroy_tool_signal)

        # Run event worker on the current thread (blocking)
        self._event_worker()

    def _on_create_tool_signal(self, sender, data):
        self.enqueue_event('create', sender, data)

    def _on_start_tool_signal(self, sender, data):
        self.enqueue_event('start', sender, data)

    def _on_destroy_tool_signal(self, sender, data):
        self.enqueue_event('destroy', sender, data)
        
    def enqueue_event(self, event_type, sender, data):
        self.event_queue.put((event_type, sender, data))

    def _event_worker(self):
        while not self._stop_event_worker.is_set():
            try:
                event_type, sender, data = self.event_queue.get(timeout=0.2)
            except queue.Empty:
                continue
            if event_type == 'create':
                self.handle_create_tool(sender, data)
            elif event_type == 'start':
                self.handle_start_tool(sender, data)
            elif event_type == 'destroy':
                self.handle_destroy_tool(sender, data)
            self.event_queue.task_done()

    def handle_create_tool(self, sender, data):
        self.last_event_time = time.time()
        # Create new tool based on data but don't start it yet
        tool = self.build(data.get('tool_type'), tool_config=data.get('tool_config', {})) 
        self.register_tool_instance(tool.tool_id, tool)

    def handle_start_tool(self, sender, data):
        self.last_event_time = time.time()
        tool_id = data.get('tool_id')
        tool_type = data.get('tool_type')
        if not tool_id or not tool_type:
            print("Error: 'tool_id' or 'tool_type' not provided in start_tool signal.")
            return
        tool_instance = self.get_tool(tool_id)
        if not tool_instance:
            # Tool does not exist, create it using handle_create_tool
            self.handle_create_tool(sender, data)
            tool_instance = self.get_tool(tool_id)
            if not tool_instance:
                print(f"Error: Could not create tool '{tool_id}' of type '{tool_type}'.")
                return
            print(f"Tool '{tool_id}' created and registered.")
        else:
            print(f"Tool '{tool_id}' already exists. Starting it.")
        # Always call start() on the tool instance
        tool_instance.start()
        print(f"Tool '{tool_id}' started.")
    
    def handle_destroy_tool(self, sender, data):
        self.last_event_time = time.time()
        tool_id = data.get('tool_id')
        if not tool_id:
            print("Error: 'tool_id' not provided in destroy_tool signal.")
            return
        self.destroy_tool_instance(tool_id)

    def clear_all_tools(self):
        """Shuts down all active tools and cleans up resources."""
        print("Clening up all active tools...")
        tools_to_stop = self.get_all_tools()

        def stop_tool(tool):
            tool.stop()
            self.unregister_tool_instance(tool.tool_id)

        if tools_to_stop:
            print(f"Stopping {len(tools_to_stop)} active tool(s)...")
            with ThreadPoolExecutor() as executor:
                executor.map(lambda tool:stop_tool(tool), tools_to_stop)
            print("All tools have been stopped.")
    # endregion

    # region Tool Building and Lifecycle
    def build(self, tool_type, tool_data=None, tool_config=None):
        """
        Builds a tool instance from saved data or a new configuration. Handles area selection and overlay binding to the tool.
        """
        tool_class = None
        if tool_type == 'simple_clicker':
            from core.main.src.impl.tool.SimpleClickerTool import SimpleClicker
            tool_class = SimpleClicker
        
        if not tool_class:
            print(f"Error: Unknown tool type '{tool_type}'")
            return None

        if tool_config:
            final_config = tool_class.get_default_configuration()
            final_config.update(tool_config)
            return tool_class(tool_configuration=final_config)
        else:
            return tool_class(tool_data=tool_data)
    # endregion

    # region Tool Instance Management
    def register_tool_instance(self, tool_id, tool_instance):
        """Registers an active tool instance."""
        self.active_tools[tool_id] = tool_instance
        print(f"Tool instance '{tool_id}' registered.")

    def unregister_tool_instance(self, tool_id):
        """Removes a tool instance from active tracking."""
        if tool_id in self.active_tools:
            del self.active_tools[tool_id]
            print(f"Tool instance '{tool_id}' unregistered.")

    def destroy_tool_instance(self, tool_id):
        """Stops and removes a tool instance."""
        if tool_id in self.active_tools:
            self.get_tool(tool_id).stop()
            self.unregister_tool_instance(tool_id)

    def get_tool(self, tool_id):
        return self.active_tools.get(tool_id)

    def get_all_tools(self):
        """Returns a list of all active tool instances."""
        return list(self.active_tools.values())
    # endregion

ToolManager = _ToolManager()
