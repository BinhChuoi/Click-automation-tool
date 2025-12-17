# -*- coding: utf-8 -*-
"""
Hotkey-driven working-area selector for multiple named areas.
"""
import time
from PIL import ImageTk
import tkinter as tk
import pyautogui

class _SelectionTool:
    def __init__(self, master, pil_image, enforce_aspect_ratio=False):
        self.master = master
        self.pil_image = pil_image
        self.enforce_aspect_ratio = enforce_aspect_ratio
        
        # Use Toplevel for the selection window
        self.top = tk.Toplevel(self.master)
        self.top.overrideredirect(True)
        self.top.attributes('-topmost', True)

        self.img_w, self.img_h = pil_image.size
        self.top.geometry(f"{self.img_w}x{self.img_h}+0+0")
        self.canvas = tk.Canvas(self.top, width=self.img_w, height=self.img_h, cursor='cross')
        self.canvas.pack()

        self.tk_img = ImageTk.PhotoImage(pil_image)
        self.canvas.create_image(0, 0, anchor='nw', image=self.tk_img)

        self.start_x = None
        self.start_y = None
        self.rect = None
        self.selection = None
        
        # Calculate screen aspect ratio
        self.screen_aspect_ratio = self.img_w / self.img_h if self.img_h != 0 else 1.0

        self.canvas.bind('<ButtonPress-1>', self._on_press)
        self.canvas.bind('<B1-Motion>', self._on_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_release)
        self.top.bind('<Escape>', self._on_escape)

    def _on_escape(self, event=None):
        self.selection = None
        self.top.destroy()

    def _on_press(self, event):
        self.start_x = int(self.canvas.canvasx(event.x))
        self.start_y = int(self.canvas.canvasy(event.y))
        if self.rect:
            self.canvas.delete(self.rect)
            self.rect = None

    def _on_drag(self, event):
        cur_x = int(self.canvas.canvasx(event.x))
        cur_y = int(self.canvas.canvasy(event.y))
        dx = cur_x - self.start_x
        dy = cur_y - self.start_y
        # Always use the sign of the drag to determine direction
        if self.enforce_aspect_ratio and abs(dx) / self.screen_aspect_ratio > abs(dy):
            width = dx
            height = int(abs(dx) / self.screen_aspect_ratio) * (1 if dy >= 0 else -1)
        elif self.enforce_aspect_ratio:
            height = dy
            width = int(abs(dy) * self.screen_aspect_ratio) * (1 if dx >= 0 else -1)
        else:
            width = dx
            height = dy
        end_x = self.start_x + width
        end_y = self.start_y + height
        # Draw rectangle
        if self.rect:
            self.canvas.coords(self.rect, self.start_x, self.start_y, end_x, end_y)
        else:
            self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, end_x, end_y, outline='red', width=2)

    def _on_release(self, event):
        # Use the last drawn rectangle coordinates BEFORE destroying the window
        coords = self.canvas.coords(self.rect) if self.rect else None
        if coords:
            x1, y1, x2, y2 = [int(c) for c in coords]
            # Enforce aspect ratio strictly
            w = abs(x2 - x1)
            h = abs(y2 - y1)
            # Adjust width/height to match aspect ratio
            if w / self.screen_aspect_ratio > h:
                h = int(w / self.screen_aspect_ratio)
            else:
                w = int(h * self.screen_aspect_ratio)
            # Recalculate x2/y2 based on adjusted w/h
            if x2 < x1:
                x2 = x1 - w
            else:
                x2 = x1 + w
            if y2 < y1:
                y2 = y1 - h
            else:
                y2 = y1 + h
            x1 = max(0, min(self.img_w, x1))
            y1 = max(0, min(self.img_h, y1))
            x2 = max(0, min(self.img_w, x2))
            y2 = max(0, min(self.img_h, y2))
            w = abs(x2 - x1)
            h = abs(y2 - y1)
            if w > 0 and h > 0:
                self.selection = {'x': min(x1, x2), 'y': min(y1, y2), 'width': w, 'height': h}
        self.top.destroy()

    def run(self):
        # This makes the Toplevel modal, so the user must interact with it
        self.top.grab_set()
        self.master.wait_window(self.top)
        return self.selection



def select_area(root, task_id, enforce_aspect_ratio=False):
    """
    Takes a screenshot, opens the selection GUI, and returns the selected area.
    """
    print(f"Please select the area for '{task_id}'...")
    time.sleep(0.2)
    img = pyautogui.screenshot()
    tool = _SelectionTool(root, img, enforce_aspect_ratio=enforce_aspect_ratio)
    area = tool.run()
    if area:
        print(f"Area selected for '{task_id}': {area}")
    else:
        print('No area selected.')
    return area



if __name__ == '__main__':
    # To test, create a root window and pass it
    root = tk.Tk()
    root.withdraw()
    
    # Test selecting an area
    task_id_to_test = 'test_area_1'
    selected_area = select_area(root, task_id_to_test)
    print(f"Result of selection for '{task_id_to_test}':", selected_area)

    # For testing other functions, you would need to import the DetectionTaskManager
    # and use its methods, since the file I/O logic has been moved there.

    root.destroy()
