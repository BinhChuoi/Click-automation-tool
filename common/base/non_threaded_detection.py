# -*- coding: utf-8 -*-
"""
This module provides a detection strategy that runs on a schedule
using threading.Timer, without creating a persistent thread.
"""
import time
import pyautogui
import threading
from common.base.detection_strategy import DetectionStrategy

class NonThreadedDetection(DetectionStrategy):
    """
    A detection strategy that uses threading.Timer to create a recurring
    detection loop. It is not a persistent thread.
    """
    def __init__(self,  detectors, working_area, task_id, sleep_period=2, on_detection=None):
        super().__init__()
        self.detectors = detectors
        self.task_id = task_id
        self.working_area = working_area
        self.on_detection = on_detection
        self.sleep_period = sleep_period

        # Detection enable/disable flag
        self.detection_enabled = True

        # State management
        self.found_objects = []
        self.timer = None
        self._lock = threading.Lock()
        self.paused = threading.Event()
        self.stopped = threading.Event()

        print(f"NonThreadedDetection for '{self.task_id}' initialized.")

    def _loop(self):
        """The main execution loop, driven by a timer."""
        if self.stopped.is_set():
            return

        if not self.paused.is_set() and self.detection_enabled:
            self.trigger_detection()

        # Reschedule the next loop
        self.timer = threading.Timer(self.sleep_period, self._loop)
        self.timer.start()
    @property
    def detection_enabled_flag(self):
        """Property to get or set detection enabled flag."""
        return self.detection_enabled

    @detection_enabled_flag.setter
    def detection_enabled_flag(self, value):
        self.detection_enabled = bool(value)

    def trigger_detection(self):
        # --- Single detection ---
        screen = pyautogui.screenshot(region=(
            self.working_area['x'], self.working_area['y'],
            self.working_area['width'], self.working_area['height']
        ))
            
        with self._lock:
            all_found_objects = []
            for detector in self.detectors:
                all_found_objects.extend(detector.detect(screen))
            self.found_objects = all_found_objects
            
        capture_id = time.time()
        self.on_detection(self.task_id, capture_id, self.found_objects)

    def start(self):
        """Starts the task by scheduling the first loop."""
        if self.timer:
            print(f"Task '{self.task_id}' is already running.")
            return
        
        self.stopped.clear()
        print(f"Task for '{self.task_id}' started.")
        self.timer = threading.Timer(self.sleep_period, self._loop)
        self.timer.start()

    def stop(self):
        """Stops the task and cancels the timer."""
        self.stopped.set()
        if self.timer:
            self.timer.cancel()
            self.timer = None
        print(f"Task for '{self.task_id}' is stopping.")

    def pause(self):
        """Pauses the task."""
        self.paused.set()
        print(f"Task '{self.task_id}' paused.")

    def resume(self):
        """Resumes the task."""
        self.paused.clear()
        print(f"Task '{self.task_id}' resumed.")

    def is_paused(self):
        """Returns True if the task is paused."""
        return self.paused.is_set()

    def is_alive(self):
        """Returns True if the timer is active."""
        return self.timer is not None and not self.stopped.is_set()

    def get_found_objects(self):
        """Returns a thread-safe copy of the last found objects."""
        with self._lock:
            return list(self.found_objects)

    def reset(self):
        """Resets the task's internal state."""
        with self._lock:
            self.found_objects.clear()
        print(f"Task '{self.task_id}' has been reset.")

    def join(self, timeout=None):
        """Waits for the timer to be cancelled."""
        if self.timer:
            self.timer.join(timeout)

