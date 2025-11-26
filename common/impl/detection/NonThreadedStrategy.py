# -*- coding: utf-8 -*-
"""
This module provides a detection strategy that runs on a schedule
using threading.Timer, without creating a persistent thread.
"""
import time
import pyautogui
import threading
from common.base.detection.BaseDetectionStrategy import BaseDetectionStrategy

class NonThreadedStrategy(BaseDetectionStrategy):
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
        self.detection_enabled = True
        self.found_objects = []
        self.timer = None
        self._lock = threading.Lock()
        self.paused = threading.Event()
        self.stopped = threading.Event()
        print(f"NonThreadedStrategy for '{self.task_id}' initialized.")
    def _loop(self):
        if self.stopped.is_set():
            return
        if not self.paused.is_set() and self.detection_enabled:
            self.trigger_detection()
        self.timer = threading.Timer(self.sleep_period, self._loop)
        self.timer.start()
    @property
    def detection_enabled_flag(self):
        return self.detection_enabled
    @detection_enabled_flag.setter
    def detection_enabled_flag(self, value):
        self.detection_enabled = bool(value)
    def trigger_detection(self):
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
        if self.timer:
            print(f"Task '{self.task_id}' is already running.")
            return
        self.stopped.clear()
        print(f"Task for '{self.task_id}' started.")
        self.timer = threading.Timer(self.sleep_period, self._loop)
        self.timer.start()
    def stop(self):
        self.stopped.set()
        if self.timer:
            self.timer.cancel()
            self.timer = None
        print(f"Task for '{self.task_id}' is stopping.")
    def pause(self):
        self.paused.set()
        print(f"Task '{self.task_id}' paused.")
    def resume(self):
        self.paused.clear()
        print(f"Task '{self.task_id}' resumed.")
    def is_paused(self):
        return self.paused.is_set()
    def is_alive(self):
        return self.timer is not None and not self.stopped.is_set()
    def get_found_objects(self):
        with self._lock:
            return list(self.found_objects)
    def reset(self):
        with self._lock:
            self.found_objects.clear()
        print(f"Task '{self.task_id}' has been reset.")
    def join(self, timeout=None):
        if self.timer:
            self.timer.join(timeout)
