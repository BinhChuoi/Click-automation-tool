# -*- coding: utf-8 -*-
"""
This module contains the thread management class for running detection tasks.
"""
from threading import Thread, Event, Lock
import pyautogui
import time
import numpy as np
from common.base.detection.BaseDetectionStrategy import BaseDetectionStrategy

class ThreadedStrategy(Thread, BaseDetectionStrategy):
    """
    A thread that runs a detection instance, with controls for pausing,
    resuming, stopping, and resetting. This class handles application state
    and actions, while the detector handles pure detection.
    """
    def __init__(self, detectors, working_area, task_id, sleep_period=2, on_detection=None):
        Thread.__init__(self)
        BaseDetectionStrategy.__init__(self)
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
        self.detection_enabled = True
    def resume(self):
        self._pause_event.clear()
        print(f"Task '{self.task_id}' resumed.")
    def is_paused(self):
        return self._pause_event.is_set()
    def get_found_objects(self):
        with self._lock:
            return list(self.found_objects)
    def run(self):
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
        return self.detection_enabled
    @detection_enabled_flag.setter
    def detection_enabled_flag(self, value):
        self.detection_enabled = bool(value)
    def trigger_detection(self):
        screenshot = pyautogui.screenshot(region=(
        self.working_area['x'], self.working_area['y'], self.working_area['width'], self.working_area['height']))
        # ...existing code for detection...
