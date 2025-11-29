import json
import os
import time
import queue
import heapq
import itertools
import threading

# Third-party imports
import tkinter as tk
import pyautogui

# Concurrency
from concurrent.futures import ThreadPoolExecutor

from common.utils.PathResolver import get_project_root
from common.helper.OverlayWindow import OverlayWindow
import common.helper.AreaSelector as capture_working_area


class _ToolManager:
    # region Initialization and Core Lifecycle
    def __init__(self, storage_path=os.path.join('storageData', 'tools')):
        """Initializes the ToolManager, setting up paths and default states."""
        self.tk_root = None
        self.task_manager = None
        self.active_tools = {}
        self.task_queue = queue.PriorityQueue()
        self.tie_breaker = itertools.count()
        self.task_last_heartbeat = {}
        self.quit_event = threading.Event()
        self.idle_timeout = None
        self.last_task_time = None

        project_root = get_project_root()
        self.storage_path = os.path.join(project_root, storage_path)
        
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
            print(f"Created tool storage directory at: {self.storage_path}")

    def reset(self):
        """Resets the manager's state for a new profile run."""
        print("Resetting ToolManager for the next profile...")
        self.tk_root = tk.Tk()
        self.tk_root.withdraw()
        self.active_tools = {}
        self.task_queue = queue.PriorityQueue()
        self.quit_event.clear()
        self.idle_timeout = None
        self.last_task_time = None

    def start_event_loop(self, profile_name, idle_timeout=None):
        """Starts the main application event loop for a given profile."""
        from common.impl.profile.ProfileManager import ProfileManager
        # from common.helper.browser import BrowserManager
        
        self.idle_timeout = idle_timeout
        self.last_task_time = time.time()

        profile_data = ProfileManager.load_profile(profile_name)
        # chrome_profile = profile_data.get('chrome_profile_name', 'Default')
        # BrowserManager.open_chrome_with_profile(profile_name=chrome_profile)

        tool_ids = profile_data.get('tool_ids', [])
        self.load_and_start_tools(tool_ids)
        
        worker_thread = threading.Thread(target=self.event_loop, daemon=True)
        worker_thread.start()

        try:
            self.tk_root.mainloop()
        except (KeyboardInterrupt, SystemExit):
            self.shutdown()

    def shutdown(self):
        """Gracefully shuts down all tools, threads, and the UI."""
        print("Shutting down...")
        self.quit_event.set()

        tools_to_stop = self.get_all_tools()
        if tools_to_stop:
            print(f"Stopping {len(tools_to_stop)} active tool(s)...")
            with ThreadPoolExecutor() as executor:
                executor.map(lambda tool: tool.stop(), tools_to_stop)
            print("All tools have been stopped.")

        if self.tk_root:
            self.tk_root.quit()
            self.tk_root.destroy()

        # from common.helper.browser import BrowserManager
        # BrowserManager.close_browser()
    # endregion

    # region Overlay Management
    def show_tool_overlay(self, tool_id, area, object_names={}):
        """Creates or updates an overlay for a specific area, bound to the tool."""
        if not hasattr(self, 'tool_overlays'):
            self.tool_overlays = {}
        if tool_id in self.tool_overlays:
            self.tool_overlays[tool_id].destroy()
        new_overlay = OverlayWindow(self.tk_root, area, tool_id, object_names, on_close=lambda tool_id: self.remove_and_delete_tool_instance(tool_id))
        self.tool_overlays[tool_id] = new_overlay
        print(f"Overlay shown for tool '{tool_id}'.")

    def hide_tool_overlay(self, tool_id):
        """Hides a specific overlay for a tool."""
        if hasattr(self, 'tool_overlays') and tool_id in self.tool_overlays:
            self.tool_overlays[tool_id].destroy()
            del self.tool_overlays[tool_id]
            print(f"Overlay hidden for tool '{tool_id}'.")

    def hide_all_tool_overlays(self):
        """Hides all active overlays for tools."""
        if hasattr(self, 'tool_overlays'):
            for tool_id in list(self.tool_overlays.keys()):
                self.hide_tool_overlay(tool_id)

    def update_tool_overlay_objects(self, tool_id, objects, show_labels=False):
        """Draws rectangles for found objects on the tool's overlay."""
        if hasattr(self, 'tool_overlays') and tool_id in self.tool_overlays:
            overlay = self.tool_overlays[tool_id]
            overlay.update_boxes(objects, show_labels=show_labels)

    def remove_objects_from_tool_overlay(self, tool_id, objects):
        """Removes specific objects from the overlay by their tags."""
        if hasattr(self, 'tool_overlays') and tool_id in self.tool_overlays:
            overlay = self.tool_overlays[tool_id]
            overlay.remove_boxes([obj['id'] for obj in objects])

    def show_temporary_overlay(self, tool_id, area, object_names={}):
        """Creates a temporary overlay for a specific area, which can be removed after use."""
        if not hasattr(self, 'temporary_overlays'):
            self.temporary_overlays = {}
        temp_overlay = OverlayWindow(self.tk_root, area, tool_id, object_names)
        self.temporary_overlays[tool_id] = temp_overlay
        print(f"Temporary overlay shown for tool '{tool_id}'.")
        return temp_overlay

    def hide_all_temporary_overlays(self):
        """Hides and removes all temporary overlays."""
        if hasattr(self, 'temporary_overlays'):
            for tool_id in list(self.temporary_overlays.keys()):
                self.temporary_overlays[tool_id].destroy()
                del self.temporary_overlays[tool_id]
            print("All temporary overlays hidden.")

    def select_area_for_tool(self, tool_id):
        """Only allows capturing the entire screen. Use 'e' to capture exception regions, 'q' to confirm all captured data. Shows overlay bound to the tool, not the task."""
        print(f"Capturing the entire screen for tool '{tool_id}'.")
        screen_w, screen_h = pyautogui.size()
        area = {'x': 0, 'y': 0, 'width': screen_w, 'height': screen_h}
        print(f"Using entire screen: {area}")

        self.show_temporary_overlay(tool_id, area, {})
        # Prompt for exception regions using hotkeys
        print("Press 'e' to capture an exception region, 'q' to confirm all captured data.")
        exception_regions = []
        exc_area = capture_working_area.select_area(self.tk_root, f"{tool_id}_exception")
        exception_regions.append(exc_area)

        self.hide_all_temporary_overlays()
        # Return area and exception regions as a dict
        return {'area': area, 'exception_regions': exception_regions}

    """
    Manages the entire lifecycle of tools, including creation, execution, 
    data persistence, and task scheduling.
    """
    #endregion
    

    # region Event Loop Processing
    def event_loop(self):
        """The main responsive loop that processes all queued tasks."""
        while not self.quit_event.is_set():
            try:
                _priority, _count, payload = self.task_queue.get_nowait()
                self.last_task_time = time.time()
                
                task_type = payload.get('type')

                if task_type == 'command':
                    self._process_command(payload)
                elif task_type == 'execute':
                    self._process_execution(payload)

                self.task_queue.task_done()
            except queue.Empty:
                if self.idle_timeout and (time.time() - self.last_task_time > self.idle_timeout):
                    print(f"Idle timeout of {self.idle_timeout} seconds reached. Shutting down profile.")
                    self.shutdown()
                pass
            time.sleep(0.01)

    def _process_command(self, payload):
        """Processes command-type tasks from the queue."""
        command = payload.get('command')
        if command == 'update_heartbeat_id':
            tool_id = payload.get('tool_id')
            heartbeat_id = payload.get('heartbeat_id')
            if tool_id and heartbeat_id:
                self.update_task_heartbeat_id(tool_id, heartbeat_id)
        elif command == 'start_new_tool':
            tool_type = payload.get('tool_type')
            tool_config = payload.get('tool_config', {})
            if tool_type:
                print(f"Starting a new {tool_type} tool...")
                tool_config["base_priority"] = (len(self.active_tools) + 1) * 5
                tool_instance = self.build(tool_type, tool_config=tool_config)
                if tool_instance:
                    tool_instance.start()
                    # Save tool data immediately after creation
                    self.save_tool_data(tool_instance.tool_id, tool_instance.get_tool_data())
                    # Show overlay for the tool if area is available in config
                    # area = tool_config.get('area')
                    # exception_regions = tool_config.get('exception_regions')
                    # overlay_info = {'exception_regions': exception_regions} if exception_regions else None
                    # if area:
                    #     self.show_tool_overlay(tool_instance.tool_id, area, overlay_info)
                    from common.impl.profile.ProfileManager import ProfileManager
                    ProfileManager.add_tool_to_active_profile(tool_instance.tool_id)
            else:
                print("Error: 'tool_type' not specified for 'start_new_tool' command.")

    def _process_execution(self, payload):
        """Processes execution-type tasks, checking for obsolescence."""
        tool_id = payload.get('tool_id')
        heartbeat_id = payload.get('heartbeat_id')

        if tool_id and heartbeat_id:
            last_heartbeat = self.task_last_heartbeat.get(tool_id, 0)
            if heartbeat_id < last_heartbeat:
                return

        task = payload.get('call_back')
        if callable(task):
            args = payload.get('args', ())
            kwargs = payload.get('kwargs', {})
            task(*args, **kwargs)
    # endregion

    # region Task Queue Management
    def start_new_task(self, execution_type, task_id, on_detection=None, on_stop=None, sleep_period=2, detector_configs=[], area=None):
        """Creates and starts a new detection task. Area must be provided by the caller."""
        if area is None:
            raise ValueError("Area must be provided when creating a new task.")
        print(f"Creating new task '{task_id}' using provided area boundaries.")
        # Dynamically import DetectionTask to avoid circular import
        from common.wrappers.DetectionTask import DetectionTask
        task_config = {
            'execution_type': execution_type,
            'area': area,
            'detector_configs': detector_configs,
            'sleep_period': sleep_period
        }
        task = DetectionTask(task_id, task_config, on_detection=on_detection, on_stop=on_stop)
        task.start()
        print(f"Task '{task_id}' started. Press 'p' to pause/resume, 'r' to reset, 'esc' to stop.")
        return task
    
    def add_task_to_queue(self, priority, task_payload=None):
        """Adds a task to the priority queue."""
        self.task_queue.put((priority, next(self.tie_breaker), task_payload))

    def remove_all_execution_tasks(self, exception_tool_id=None):
        """Removes all 'execute' tasks from the queue, optionally keeping one tool's tasks."""
        with self.task_queue.mutex:
            new_queue = [
                item for item in self.task_queue.queue 
                if not (
                    isinstance(item[2], dict) and 
                    item[2].get('type') == 'execute' and 
                    item[2].get('tool_id') != exception_tool_id
                )
            ]
            self.task_queue.queue = new_queue
            heapq.heapify(self.task_queue.queue)
        self.pause_all_execution_tasks(exception_tool_id=exception_tool_id)

    def pause_all_execution_tasks(self, exception_tool_id=None):
        """Pauses all active tools except for the one specified."""
        for tool in self.active_tools.values():
            if tool.tool_id != exception_tool_id:
                tool.pause()

    def resume_all_execution_tasks(self, exception_tool_id=None):
        """Resumes all paused tools except for the one specified."""
        for tool in self.active_tools.values():
            if tool.tool_id != exception_tool_id:
                tool.resume()

    def update_task_heartbeat_id(self, tool_id, heartbeat_id):
        """Updates the latest heartbeat ID for a tool to manage task obsolescence."""
        self.task_last_heartbeat[tool_id] = max(self.task_last_heartbeat.get(tool_id, 0), heartbeat_id)
    # endregion

    # region Tool Building and Lifecycle
    def build(self, tool_type, tool_data=None, tool_config=None):
        """
        Builds a tool instance from saved data or a new configuration. Handles area selection and overlay binding to the tool.
        """
        tool_class = None
        if tool_type == 'simple_clicker':
            from common.impl.tool.SimpleClickerTool import SimpleClicker
            tool_class = SimpleClicker
        
        if not tool_class:
            print(f"Error: Unknown tool type '{tool_type}'")
            return None

        # # Area selection and overlay binding for new tool creation
        # if tool_config and 'area' not in tool_config:
        #     area_data = self.select_area_for_tool(tool_config.get('tool_id', tool_type))
        #     if area_data is None:
        #         return None
        #     tool_config['area'] = area_data.get('area')
        #     tool_config['exception_regions'] = area_data.get('exception_regions')

        if tool_config:
            final_config = tool_class.get_default_configuration()
            final_config.update(tool_config)
            return tool_class(self, self.task_manager, tool_configuration=final_config)
        else:
            return tool_class(self, self.task_manager, tool_data=tool_data)

    def load_and_start_tools(self, tool_ids):
        """Loads and starts a specific list of tools by their IDs."""
        print(f"Loading and starting specified tools: {tool_ids}")
        for tool_id in tool_ids:
            if self.get_tool(tool_id):
                print(f"Tool '{tool_id}' is already active. Skipping.")
                continue
            tool_data = self.load_tool_data(tool_id)
            if tool_data and 'tool_type' in tool_data:
                print(f"Building and starting tool '{tool_id}' of type '{tool_data['tool_type']}'...")
                tool_instance = self.build(tool_data['tool_type'], tool_data=tool_data)
                if tool_instance:
                    tool_instance.start()
            else:
                print(f"Warning: Could not load tool with ID '{tool_id}'.")

    def load_and_start_all_tools(self):
        """Scans storage, then loads and starts all saved tools."""
        print("Loading and starting all saved tools...")
        if not os.path.exists(self.storage_path):
            print("Tool storage directory not found.")
            return

        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                tool_id = filename[:-5]
                tool_data = self.load_tool_data(tool_id)
                if tool_data and 'tool_type' in tool_data:
                    if 'task_ids' not in tool_data or not tool_data['task_ids']:
                        print(f"Warning: Tool '{tool_id}' has no tasks. Skipping.")
                        continue
                    print(f"Building and starting tool '{tool_id}'...")
                    tool_instance = self.build(tool_data['tool_type'], tool_data=tool_data)
                    if tool_instance:
                        tool_instance.start()
                else:
                    print(f"Warning: Could not load tool from file '{filename}'.")
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

    def remove_and_delete_tool_instance(self, tool_id):
        """Unregisters a tool and deletes its data file."""
        self.get_tool(tool_id).stop()
        self.delete_tool_data(tool_id)
        self.hide_tool_overlay(tool_id)

    def get_tool(self, tool_id):
        """Returns an active tool instance by its ID."""
        return self.active_tools.get(tool_id)

    def get_all_tools(self):
        """Returns a list of all active tool instances."""
        return list(self.active_tools.values())
    # endregion

    # region Data Persistence (File I/O)
    def get_tool_filepath(self, tool_id):
        """Constructs the full file path for a tool's data file."""
        return os.path.join(self.storage_path, f"{tool_id}.json")

    def save_tool_data(self, tool_id, data):
        """Saves a tool's data to a JSON file."""
        filepath = self.get_tool_filepath(tool_id)
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"Error saving tool data for '{tool_id}': {e}")

    def load_tool_data(self, tool_id):
        """Loads a tool's data from a JSON file."""
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
        """Deletes a tool's data file."""
        filepath = self.get_tool_filepath(tool_id)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                if tool_id in self.active_tools:
                    del self.active_tools[tool_id]
                print(f"Tool data for '{tool_id}' deleted.")
                return True
            except OSError as e:
                print(f"Error deleting tool data file for '{tool_id}': {e}")
        return False
    # endregion

ToolManager = _ToolManager()
