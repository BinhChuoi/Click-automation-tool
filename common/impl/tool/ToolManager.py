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
from common.helper.overlay import OverlayWindow
import common.helper.capture_working_area as capture_working_area

class ToolManager:
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
        print("Resetting ToolManager for the next profile...")
        self.tk_root = tk.Tk()
        self.tk_root.withdraw()
        self.active_tools = {}
        self.task_queue = queue.PriorityQueue()
        self.quit_event.clear()
        self.idle_timeout = None
        self.last_task_time = None
    def start_event_loop(self, profile_name, idle_timeout=None):
        from common.impl.profile.ProfileManager import ProfileManager
        self.idle_timeout = idle_timeout
        self.last_task_time = time.time()
        profile_data = ProfileManager.load_profile(profile_name)
        tool_ids = profile_data.get('tool_ids', [])
        self.load_and_start_tools(tool_ids)
        worker_thread = threading.Thread(target=self.event_loop, daemon=True)
        worker_thread.start()
        try:
            self.tk_root.mainloop()
        except (KeyboardInterrupt, SystemExit):
            self.shutdown()
    def shutdown(self):
        print("Shutting down...")
        self.quit_event.set()
# ...existing code continues...
