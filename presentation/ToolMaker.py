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



import os
import tkinter as tk
from tkinter import ttk, messagebox
from persistant.AbstractToolDataStore import AbstractToolDataStore


class ToolMakerUI(tk.Frame):
    def __init__(self, master=None, manager=None, datastore=None):
        super().__init__(master)
        self.master = master
        self.manager = manager
        if datastore is None:
            raise ValueError("A datastore implementing AbstractToolDataStore must be provided to ToolMakerUI.")
        self.datastore = datastore
        self.tool_data_map = {}
        self.core_running = False
        self._init_ui()
        self._load_tools_from_store()

    def _load_tools_from_store(self):
        """Load all tool data from the datastore and populate the tool list."""
        self.tool_list.delete(*self.tool_list.get_children())
        self.tool_data_map.clear()
        try:
            all_tools = self.datastore.get_all_tool_data()
            for tool_id, data in all_tools.items():
                item_id = self.tool_list.insert("", "end", values=(data.get("name", tool_id), data.get("type", "")))
                self.tool_data_map[item_id] = data
        except Exception as e:
            print(f"Failed to load tools: {e}")

    def _init_ui(self):
        """Initialize all UI components."""
        self.pack(fill=tk.BOTH, expand=True)
        if self.master is not None:
            self.master.title("Tool Maker")
            self.master.geometry("600x400")

        self._build_toolbar()
        self._build_tool_list()
        self._build_edit_buttons()

    def _build_toolbar(self):
        toolbar = tk.Frame(self)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        tk.Label(toolbar, text="Tool Name:").pack(side=tk.LEFT, padx=(5, 2))
        self.entry_tool_name = tk.Entry(toolbar, width=15)
        self.entry_tool_name.pack(side=tk.LEFT, padx=2)
        tk.Label(toolbar, text="Tool Type:").pack(side=tk.LEFT, padx=(10, 2))
        self.tool_type_var = tk.StringVar()
        self.combo_tool_type = ttk.Combobox(toolbar, textvariable=self.tool_type_var, values=["simple_clicker", "text_detector", "captcha_passer"], width=15)
        self.combo_tool_type.pack(side=tk.LEFT, padx=2)
        btn_save = tk.Button(toolbar, text="Save Tool", command=self.save_tool)
        btn_save.pack(side=tk.LEFT, padx=10)

        self.core_status = tk.StringVar(value="Core not started")
        self.btn_core = tk.Button(toolbar, text="Start Core", command=self.toggle_core)
        self.btn_core.pack(side=tk.LEFT, padx=10, pady=2)
        self.status_label = tk.Label(toolbar, textvariable=self.core_status, fg="blue")
        self.status_label.pack(side=tk.LEFT, padx=10)

        self.progress = ttk.Progressbar(toolbar, mode="indeterminate", length=120)
        self.progress.pack(side=tk.LEFT, padx=10)
        self.progress.pack_forget()

    def _build_tool_list(self):
        columns = ("Name", "Type")
        self.tool_list = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tool_list.heading(col, text=col)
        self.tool_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tool_list.bind("<ButtonRelease-1>", self.on_tool_select)

    def _build_edit_buttons(self):
        self.edit_btn_frame = tk.Frame(self)
        self.edit_btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        self.btn_edit_modes = tk.Button(self.edit_btn_frame, text="Edit Modes", command=self.edit_selected_modes, state=tk.DISABLED)
        self.btn_edit_modes.pack(side=tk.LEFT, padx=5)
        self.btn_edit_branches = tk.Button(self.edit_btn_frame, text="Edit Detection Branches", command=self.edit_selected_branches, state=tk.DISABLED)
        self.btn_edit_branches.pack(side=tk.LEFT, padx=5)
    def toggle_core(self):
        """Toggle the core component between started and stopped states."""
        if not self.core_running:
            self.start_core()
        else:
            self.stop_core()

    def start_core(self):
        self.core_status.set("Starting core...")
        self.progress.pack(side=tk.LEFT, padx=10)
        self.progress.start()
        self.btn_core.config(state=tk.DISABLED)
        self.after(100, self._do_start_core)

    def _do_start_core(self):
        if self.manager and hasattr(self.manager, "start_core_component"):
            self.manager.start_core_component(callback=self.on_core_started)
        else:
            self.after(1000, self.on_core_started)

    def on_core_started(self):
        self.progress.stop()
        self.progress.pack_forget()
        self.core_status.set("Core started")
        self.btn_core.config(text="Stop Core", state=tk.NORMAL)
        self.core_running = True

    def stop_core(self):
        self.core_status.set("Stopping core...")
        self.btn_core.config(state=tk.DISABLED)
        if self.manager and hasattr(self.manager, "stop_core_component"):
            self.manager.stop_core_component(callback=self.on_core_stopped)
        else:
            self.after(1000, self.on_core_stopped)

    def on_core_stopped(self):
        self.core_status.set("Core stopped")
        self.btn_core.config(text="Start Core", state=tk.NORMAL)
        self.core_running = False


    # --- Tool CRUD and UI logic ---

    def save_tool(self):
        """Save a new tool with the provided name and type."""
        name = self.entry_tool_name.get().strip()
        ttype = self.tool_type_var.get().strip()
        if not name or not ttype:
            messagebox.showerror("Validation Error", "Tool name and type are required.")
            return
        default_modes = getattr(self.manager, 'default_mode_task_config', default_mode_task_config)
        default_branches = getattr(self.manager, 'default_detection_branches', default_detection_branches)
        tool_id = name.replace(" ", "_").lower()
        tool_data = {"name": name, "type": ttype, "modes": default_modes, "detection_branches": default_branches}
        item_id = self.tool_list.insert("", "end", values=(name, ttype))
        self.tool_data_map[item_id] = tool_data
        try:
            self.datastore.save_tool_data(tool_id, tool_data)
        except Exception as e:
            print(f"Failed to save tool {tool_id}: {e}")
        messagebox.showinfo("Tool Created", f"Tool '{name}' created.")
        self.entry_tool_name.delete(0, tk.END)
        self.tool_type_var.set("")
        self.tool_list.selection_set(item_id)
        self.update_edit_buttons()


    def on_tool_select(self, event):
        self.update_edit_buttons()

    def update_edit_buttons(self):
        selected = self.tool_list.selection()
        state = tk.NORMAL if selected else tk.DISABLED
        self.btn_edit_modes.config(state=state)
        self.btn_edit_branches.config(state=state)


    def edit_selected_modes(self):
        self._edit_selected_json_field('modes', 'Edit Modes')


    def edit_selected_branches(self):
        self._edit_selected_json_field('detection_branches', 'Edit Detection Branches')

    def _edit_selected_json_field(self, field, window_title):
        selected = self.tool_list.selection()
        if not selected:
            return
        item_id = selected[0]
        tool_data = self.tool_data_map.get(item_id)
        if not tool_data:
            return
        try:
            import webview
            import json
            import threading
            class JSONEditorAPI:
                def __init__(self):
                    self.json_data = None
                    self.saved = threading.Event()
                def on_change(self, json_str):
                    self.json_data = json.loads(json_str)
                    self.saved.set()
            api = JSONEditorAPI()
            html_path = 'file://' + os.path.abspath(os.path.join(os.path.dirname(__file__), 'jsoneditor.html'))
            window = webview.create_window(
                window_title,
                html_path,
                js_api=api,
                width=800,
                height=600
            )
            def on_loaded(window):
                print(f"DEBUG: {field} data", tool_data[field])
                window.evaluate_js(f"setData({json.dumps(json.dumps(tool_data[field]))})")
            webview.start(on_loaded, window)
            api.saved.wait()  # Wait for Save button
            if api.json_data is not None:
                tool_data[field] = api.json_data
                tool_id = tool_data['name'].replace(" ", "_").lower()
                try:
                    self.datastore.save_tool_data(tool_id, tool_data)
                except Exception as e:
                    print(f"Failed to save tool {tool_id}: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open JSON editor: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ToolMakerUI(master=root)
    app.mainloop()
