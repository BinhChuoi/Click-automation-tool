# -*- coding: utf-8 -*-
"""
This module provides a persistent, transparent overlay window.
"""

from tkinter import Toplevel, Canvas, Button, BOTH, FLAT, NW, NE
from typing import Callable
from shared.utils.Constants import OVERLAY_TRANSPARENT_COLOR

class OverlayWindow:
        # Draw a red border to match the selection tool
    def __init__(self, tk_root, working_area, id, object_names=None, on_close: Callable = None):
        self.tk_root = tk_root
        self.working_area = working_area
        self.id = id
        self.object_names = object_names or []
        self.on_close = on_close
        self.top = None
        self.canvas = None
        self._create_widgets()
    def _create_widgets(self):
            """Creates the Toplevel window and canvas."""
            if not self.tk_root:
                print("Error: OverlayWindow requires a master window.")
                return
            self.top = Toplevel(self.tk_root)
            self.top.attributes('-topmost', True)
            self.top.overrideredirect(True)
            self.top.attributes('-transparentcolor', OVERLAY_TRANSPARENT_COLOR)

            x, y, w, h = self.working_area['x'], self.working_area['y'], self.working_area['width'], self.working_area['height']
            # Ensure w and h are positive and non-zero
            if w <= 0 or h <= 0:
                print(f"Invalid overlay size: width={w}, height={h}. Overlay will not be shown.")
                return
            self.top.geometry(f"{w}x{h}+{x}+{y}")

            self.canvas = Canvas(self.top, bg=OVERLAY_TRANSPARENT_COLOR, highlightthickness=0)
            self.canvas.pack(fill=BOTH, expand=True)

            if self.canvas:
                # Draw a red border to match the selection tool
                self.canvas.create_rectangle(1, 1, w-1, h-1, outline='red', width=2)

                # Draw exception regions as filled rectangles (white)
                exception_regions = []
                if self.object_names and isinstance(self.object_names, dict) and 'exception_regions' in self.object_names:
                    exception_regions = self.object_names['exception_regions']
                elif isinstance(self.object_names, list):
                    exception_regions = self.object_names
                for exc in exception_regions:
                    ex = exc.get('x', 0) - x
                    ey = exc.get('y', 0) - y
                    ew = exc.get('width', 0)
                    eh = exc.get('height', 0)
                    self.canvas.create_rectangle(ex, ey, ex+ew, ey+eh, outline='black', width=2, fill='white')

                # self.canvas.create_text(10, 10, text=self.id, fill="white", anchor="nw")

                close_button = Button(self.canvas, text="X", command=lambda: self.on_close(self.id), bg="red", fg="white", relief=FLAT)
                self.canvas.create_window(w - 5, 5, anchor="ne", window=close_button)

    def update_boxes(self, found_objects, show_labels=False):
        """Clears old boxes and draws new ones for found objects."""
        if not self.top or not self.top.winfo_exists():
            return

        self.canvas.delete("found_object")
        offset = 2  # An offset to make the box slightly larger for better visibility

        for obj in found_objects:
            # The object dictionary contains center x, center y, width, and height
            center_x = obj['x']
            center_y = obj['y']
            w = obj['width']
            h = obj['height']
            
            # Calculate top-left corner coordinates
            x1 = center_x - w / 2
            y1 = center_y - h / 2
            
            # Calculate bottom-right corner coordinates
            x2 = center_x + w / 2
            y2 = center_y + h / 2

            # Create a tuple of tags
            tags = ("found_object", obj['id'])

            # Draw the bounding box
            self._draw_corner_box(
                x1 - offset, y1 - offset, x2 + offset, y2 + offset,
                color='red', width=2, tags=tags
            )
            
            # Display class name and confidence
            if show_labels:
                label = f"{obj['class']} ({obj['confidence']:.2f})"
                self.canvas.create_text(x1, y1 - 10, text=label, fill="white", anchor="nw", tags=tags)
                
    def remove_boxes(self, tags):
        """Removes specific boxes from the overlay by their tags."""
        if not self.top or not self.top.winfo_exists():
            return
        for tag in tags:
            self.canvas.delete(tag)
            
    def _draw_corner_box(self, x1, y1, x2, y2, color='red', width=2, tags="found_object"):
        """Draws a box with only corners visible."""
        corner_length = min((x2 - x1), (y2 - y1)) * 0.2  # 20% of the smaller dimension

        # Top-left corner
        self.canvas.create_line(x1, y1, x1 + corner_length, y1, fill=color, width=width, tags=tags)
        self.canvas.create_line(x1, y1, x1, y1 + corner_length, fill=color, width=width, tags=tags)

        # Top-right corner
        self.canvas.create_line(x2, y1, x2 - corner_length, y1, fill=color, width=width, tags=tags)
        self.canvas.create_line(x2, y1, x2, y1 + corner_length, fill=color, width=width, tags=tags)

        # Bottom-left corner
        self.canvas.create_line(x1, y2, x1 + corner_length, y2, fill=color, width=width, tags=tags)
        self.canvas.create_line(x1, y2, x1, y2 - corner_length, fill=color, width=width, tags=tags)

        # Bottom-right corner
        self.canvas.create_line(x2, y2, x2 - corner_length, y2, fill=color, width=width, tags=tags)
        self.canvas.create_line(x2, y2, x2, y2 - corner_length, fill=color, width=width, tags=tags)

    def destroy(self):
        """Closes the overlay window and calls the on_close callback."""
        if self.top and self.top.winfo_exists():
            self.top.destroy()
            self.top = None
