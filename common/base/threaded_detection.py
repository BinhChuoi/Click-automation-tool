# -*- coding: utf-8 -*-
"""
This module contains the thread management class for running detection tasks.
"""
from threading import Thread, Event, Lock
import pyautogui
import time
import numpy as np
from common.base.detection_strategy import DetectionStrategy

class ThreadDetection(Thread, DetectionStrategy):
    """
    A thread that runs a detection instance, with controls for pausing,
    resuming, stopping, and resetting. This class handles application state
    and actions, while the detector handles pure detection.
    """
    def __init__(self, detectors, working_area, task_id, sleep_period=2, on_detection=None):
        Thread.__init__(self)
        DetectionStrategy.__init__(self)
        self.daemon = True
        self.detectors = detectors
        self.task_id = task_id
        self.working_area = working_area
        self.on_detection = on_detection
        self.sleep_period = sleep_period
        self._stop_event = Event()
        self._pause_event = Event()
        self._reset_event = Event()
        self.found_objects = []
        self._lock = Lock()
        # Detection enable/disable flag
        self.detection_enabled = True

    def resume(self):
        """Signals the thread to resume."""
        self._pause_event.clear()
        print(f"Task '{self.task_id}' resumed.")

    def is_paused(self):
        """Returns True if the task is paused."""
        return self._pause_event.is_set()

    def get_found_objects(self):
        """
        Returns a thread-safe copy of the list of found objects.
        """
        with self._lock:
            return list(self.found_objects)

    def run(self):
        """The main loop of the detection thread."""
        print(f"Detection thread for '{self.task_id}' started.")
        time.sleep(self.sleep_period)
        while not self._stop_event.is_set():
            if self._reset_event.is_set():
                self.found_objects.clear()
                self._reset_event.clear()

            if self._pause_event.is_set() or not self.detection_enabled:
                time.sleep(0.5)
                continue

            self.trigger_detection()

            time.sleep(self.sleep_period)
            print("Detection cycle complete.")
        print(f"Detection thread for '{self.task_id}' stopped.")
    @property
    def detection_enabled_flag(self):
        """Property to get or set detection enabled flag."""
        return self.detection_enabled

    @detection_enabled_flag.setter
    def detection_enabled_flag(self, value):
        self.detection_enabled = bool(value)

    def trigger_detection(self):
        screenshot = pyautogui.screenshot(region=(
        self.working_area['x'], self.working_area['y'], self.working_area['width'], self.working_area['height']))

        with self._lock:
            all_found_objects = []
            for detector in self.detectors:
                all_found_objects.extend(detector.detect(screenshot))
            self.found_objects = all_found_objects

        capture_id = time.time()
        self.on_detection(self.task_id, capture_id, self.found_objects)

    
    def stop(self):
        """Signals the thread to stop."""
        self._stop_event.set()
        print(f"Stopping detection for '{self.task_id}'.")

    def pause(self):
        """Pauses the thread's execution loop."""
        self._pause_event.set()
        print(f"Task '{self.task_id}' paused.")

    def reset(self):
        """Signals the thread to reset to its initial state."""
        self._reset_event.set()
        print(f"Resetting detection for '{self.task_id}'.")

    def is_alive(self):
        """Checks if the thread is alive."""
        return super().is_alive()


