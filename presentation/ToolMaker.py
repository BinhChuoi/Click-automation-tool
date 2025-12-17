
# Keep these for later use
default_mode_task_config = {
    "main": [
        {
            "id": "default",
            "execution_type": "non_threaded",
            "area": {"x": 0, "y": 0, "width": 1920, "height": 1080},
            "detectors": [
                {"detector_type": "template", "config": {"template_paths": [], "threshold": 0.8}}
            ]
        },
        {
            "id": "tool_text",
            "execution_type": "non_threaded",
            "area": {"x": 1800, "y": 365, "width": 120, "height": 120},
            "detectors": [
                {"detector_type": "text", "config": {}}
            ]
        }
    ],
    "captcha_passer": [
        {
            "id": "captcha_passer",
            "execution_type": "non_threaded",
            "area": {"x": 0, "y": 0, "width": 1920, "height": 1080},
            "detectors": [
                {"detector_type": "yolo", "config": {"model_id": "sunflower-captcha-detection-idxoo/12", "api_key": "ds4cacROzFGinfEsMrm0"}}
            ]
        }
    ]
}

default_detection_branches = {
    "scenarios": [
        {
            "id": "planting",
            "condition": "all([k in detected_objects['default'] for k in ['base_template.png', 'hole.png']])",
            "actions": [
                {"type": "click", "templates": ["hole.png"], "max_items": 10, "click_count": 1}
            ]
        },
        {
            "id": "havert_crops",
            "condition": "('base_template.png' in detected_objects['default']) and any([k in detected_objects['default'] for k in ['sunflower_crop_v2.png', 'rhubard_crop.png']])",
            "actions": [
                {"type": "click", "templates": ["sunflower_crop_v2.png", "rhubard_crop.png"], "max_items": 10, "click_count": 1}
            ]
        },
        {
            "id": "close_basket_tool",
            "condition": "all([k in detected_objects['default'] for k in ['basket_window.png', 'close_button.png']])",
            "actions": [
                {"type": "click", "templates": ["close_button.png"], "max_items": 1}
            ]
        },
        {
            "id": "select_seed_in_basket_tool",
            "condition": "all([k in detected_objects['default'] for k in ['basket_window.png', 'rhubard_seed.png']])",
            "actions": [
                {"type": "click", "templates": ["rhubard_seed.png"], "max_items": 2}
            ],
            "childrens": ["close_basket_tool"]
        },
        {
            "id": "detect_seed_tool_not_suitable",
            "condition": "all([k in detected_objects['default'] for k in ['base_template.png', 'basket_v2.png']]) and not ('rhubard_seed_tool.png' in detected_objects['default'])",
            "actions": [
                {"type": "click", "templates": ["basket_v2.png"], "max_items": 1}
            ],
            "childrens": ["select_seed_in_basket_tool"]
        },
        {
            "id": "close_captcha",
            "condition": "'close_text.png' in detected_objects['default']",
            "actions": [
                {"type": "click", "templates": ["close_text.png"], "max_items": 1}
            ]
        },
        {
            "id": "handle_captcha",
            "condition": "any([(k in detected_objects['captcha_passer']) for k in ['goblin', 'chest', 'skeleton']])",
            "mode": "captcha_passer",
            "actions": [
                {"type": "click", "templates": ["goblin", "chest", "skeleton"], "max_items": 3},
                {"type": "change_mode", "mode": "main"}
            ],
            "childrens": ["close_captcha"]
        },
        {
            "id": "detect_captcha",
            "condition": "any([(k in detected_objects['default']) for k in ['attempt_left_blue.png', 'tap_chest.png', 'attempt_left_red.png']])",
            "actions": [{"type": "change_mode", "mode": "captcha_passer"}],
            "childrens": ["handle_captcha"]
        }
    ]
}

import tkinter as tk
from tkinter import ttk, messagebox
import os

class ToolMakerUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tool Maker")
        self.geometry("600x400")
        self._build_ui()

    def _build_ui(self):
        # Toolbar
        toolbar = tk.Frame(self)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        btn_create = tk.Button(toolbar, text="Create Tool", command=self.create_tool)
        btn_create.pack(side=tk.LEFT, padx=2, pady=2)
        btn_edit = tk.Button(toolbar, text="Edit Tool", command=self.edit_tool)
        btn_edit.pack(side=tk.LEFT, padx=2, pady=2)

        # Tool list
        self.tool_list = ttk.Treeview(self, columns=("Name", "Type"), show="headings")
        self.tool_list.heading("Name", text="Tool Name")
        self.tool_list.heading("Type", text="Tool Type")
        self.tool_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Sample data
        self._populate_sample_tools()

        # Add start button for each row (simulate with a column for now)
        self.tool_list.bind("<Double-1>", self.on_start_tool)

    def _populate_sample_tools(self):
        # This would be loaded from storage in a real app
        sample_tools = [
            ("Auto Clicker", "simple_clicker"),
            ("Text Detector", "text_detector"),
            ("Captcha Solver", "captcha_passer")
        ]
        for name, ttype in sample_tools:
            self.tool_list.insert("", "end", values=(name, ttype))

    def on_start_tool(self, event):
        item = self.tool_list.selection()
        if item:
            tool = self.tool_list.item(item[0], "values")
            messagebox.showinfo("Start Tool", f"Starting tool: {tool[0]} ({tool[1]})")

    def create_tool(self):
        messagebox.showinfo("Create Tool", "Create Tool dialog would appear here.")

    def edit_tool(self):
        item = self.tool_list.selection()
        if item:
            tool = self.tool_list.item(item[0], "values")
            messagebox.showinfo("Edit Tool", f"Edit Tool dialog for: {tool[0]} ({tool[1]})")
        else:
            messagebox.showinfo("Edit Tool", "Please select a tool to edit.")

if __name__ == "__main__":
    app = ToolMakerUI()
    app.mainloop()
