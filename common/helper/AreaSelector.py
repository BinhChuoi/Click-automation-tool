# -*- coding: utf-8 -*-
"""
Hotkey-driven working-area selector for multiple named areas.
"""
import json
import time
from PIL import Image, ImageTk
import tkinter as tk
import pyautogui

class _SelectionTool:
    def __init__(self, master, pil_image, enforce_aspect_ratio=False):
        self.master = master
        self.pil_image = pil_image
        self.enforce_aspect_ratio = enforce_aspect_ratio
        # ...existing code...

    def _on_escape(self, event=None):
        # ...existing code...

    def _on_press(self, event):
        # ...existing code...

    def _on_drag(self, event):
        # ...existing code...

    def _on_release(self, event):
        # ...existing code...

    def run(self):
        # ...existing code...


def select_area(root, task_id, enforce_aspect_ratio=False):
    # ...existing code...

if __name__ == '__main__':
    # ...existing code...
