from core.main.main import build_core_component
from presentation.OverlayWindow import OverlayWindow  # Add this import, adjust path if needed
from shared.utils.Constants import TASK_STARTED_EVENT
import queue
import time
import tkinter as tk
import itertools
import threading
import heapq

from presentation.ToolMaker import ToolMakerUI
from persistant.FileToolDataStore import FileToolDataStore

from presentation.ToolMaker import default_mode_task_config, default_detection_branches

class PresentationManager:
    # Provide default configs for ToolMakerUI dialogs
    default_mode_task_config = default_mode_task_config
    default_detection_branches = default_detection_branches
    _instance = None
    _initialized = False
    def run_event_loop(self):
        """Runs the main responsive loop for ToolManager tasks."""
        # Use Mediator pattern for event handling
        from shared.mediator.impl.Mediator import BlinkerMediator
        from shared.utils.Constants import TASK_STARTED_EVENT, TOOL_HEARTBEAT_EVENT, INTERACTION_EVENT
        mediator = BlinkerMediator.get_instance()
        mediator.subscribe(TASK_STARTED_EVENT, self.handle_task_started)
        mediator.subscribe(TOOL_HEARTBEAT_EVENT, self.handle_tool_heartbeat)
        mediator.subscribe(INTERACTION_EVENT, self.handle_interaction_event)
        while not self.quit_event.is_set():
            try:
                _priority, _count, payload = self.task_queue.get_nowait()
                print("Processing task:", payload)
                self.last_task_time = time.time()
                task_type = payload.get('type')
                if task_type == 'execute':
                    self._process_execution(payload)
                self.task_queue.task_done()
            except queue.Empty:
                pass
            self.tk_root.update()
            time.sleep(0.01)

    def handle_interaction_event(self, sender, **kwargs):
        """Handles INTERACTION_EVENT to process UI interactions like clicks."""
        data = kwargs.get('data', kwargs)
        action = data.get('action', {})
        detected_objects_map = data.get('detected_objects_map', {})
        clickable_object_names = action.get('templates', [])
        # Gather all matched objects from detected_objects_map
        all_detected_objects = []
        for objects in detected_objects_map.values():
            all_detected_objects.extend(objects)

        action_type = action.get('type')
        click_count = action.get('click_count', 1)
        max_items = action.get('max_items', 1)
        # For each matched object, perform the click action
        if action_type == 'click':
            # Import ScreenActions from the helper module
            try:
                from core.main.src.helper.ScreenActions import move_mouse, click
            except ImportError:
                from presentation.ScreenActions import move_mouse, click
            for obj in all_detected_objects:
                if obj.get('class_name', '') not in clickable_object_names or max_items <= 0:
                    continue

                max_items -= 1
                x = obj.get('x', 0)
                y = obj.get('y', 0)
                priority = 5  # Or fetch from config if needed
                print(f"PresentationManager: Clicking at ({x}, {y}) for template '{obj.get('class_name', '')}', {click_count} time(s)")
                move_mouse(x=x, y=y, priority=priority, duration=0.2)
                for _ in range(click_count):
                    click(priority=priority, button='left')

    def handle_tool_heartbeat(self, sender, **kwargs):
        data = kwargs.get('data', kwargs)
        all_detected = data.get('detected_objects', {})
        
        # Draw rectangles in overlays per task_id
        if not hasattr(self, 'tool_overlays'):
            self.tool_overlays = {}
        # TODO: Create unique task_id from tool_id and task_id, reconsider this
        for task_id, objects in all_detected.items():
            overlay = self.tool_overlays.get(task_id)
            # Add a new execution task for this task_id
            self.add_task_to_queue(1, {
                'type': 'execute',
                'call_back': lambda overlay=overlay, objects=objects: overlay.update_boxes(objects),
                'tool_id': task_id,
                'heartbeat_id': time.time(),
                'args': ()
            })

    def _process_execution(self, payload):
        """Processes execution-type tasks, checking for obsolescence."""
        tool_id = payload.get('tool_id')
        heartbeat_id = payload.get('heartbeat_id')

        # if tool_id and heartbeat_id:
        #     last_heartbeat = self.task_last_heartbeat.get(tool_id, 0)
        #     if heartbeat_id < last_heartbeat:
        #         return

        task = payload.get('call_back')
        if callable(task):
            args = payload.get('args', ())
            kwargs = payload.get('kwargs', {})
            task(*args, **kwargs)

    def __init__(self):
        self.tk_root = tk.Tk()
        self.task_queue = queue.PriorityQueue()
        self.tie_breaker = itertools.count()
        self.last_task_time = time.time()
        self.idle_timeout = 450  # Default idle timeout in seconds
        self.quit_event = threading.Event()

        # Core component thread reference
        self.core_thread = None
        self.core_component = None

        # Handle window close to shutdown all threads
        self.tk_root.protocol("WM_DELETE_WINDOW", self.on_close)
        # Start ToolMaker UI integrated with PresentationManager's event loop
        self.tool_data_store = FileToolDataStore()  # Uses default persistant/data
        self.toolmaker_app = ToolMakerUI(master=self.tk_root, manager=self, datastore=self.tool_data_store)

    def start_core_component(self, callback=None):
        if self.core_thread and self.core_thread.is_alive():
            if callback:
                self.tk_root.after(100, callback)
            return
        def start_core():
            self.core_component = build_core_component()
            self.core_component.start()
            if callback:
                self.tk_root.after(0, callback)
        self.core_thread = threading.Thread(target=start_core, daemon=True)
        self.core_thread.start()

    def stop_core_component(self, callback=None):
        if self.core_component and hasattr(self.core_component, 'stop'):
            self.core_component.stop()
        self.core_component = None
        if callback:
            self.tk_root.after(0, callback)

    def on_close(self):
        print("Shutting down all threads and cleaning up...")
        self.quit_event.set()
        # Optionally join threads or perform other cleanup here
        self.tk_root.destroy()

        PresentationManager._instance = self

    def get_task_queue(self):
        return self.task_queue

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_tk_root(self):
        return self.tk_root
    
    def handle_task_started(self, sender, **kwargs):
        data = kwargs.get('data', kwargs)
        print(f"Task started: {data}")
        self.add_task_to_queue(1, {
            'type': 'execute',
            'call_back': lambda: self.show_tool_overlay(
                 id=data.get('id'), area=data.get('area'), object_names=data.get('object_names', {})),
            'tool_id': data.get('tool_id'),
            'heartbeat_id': time.time(),
            'args': ()
        })
    

    def show_tool_overlay(self, id, area, object_names={}):
        """Creates or updates an overlay for a specific area, bound to the tool."""
        if not hasattr(self, 'tool_overlays'):
            self.tool_overlays = {}
        if id in self.tool_overlays:
            self.tool_overlays[id].destroy()
            
        new_overlay = OverlayWindow(self.tk_root, area, id, object_names, on_close=lambda tool_id: self.remove_and_delete_tool_instance(tool_id))
        self.tool_overlays[id] = new_overlay
        print(f"Overlay shown for tool '{id}'.")
    
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
