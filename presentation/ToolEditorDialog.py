import tkinter as tk
from tkinter import ttk, messagebox
import webview
import json

class ToolEditorDialog(tk.Toplevel):
    def __init__(self, master=None, tool_data=None, on_save=None):
        super().__init__(master)
        self.title("Tool Editor")
        self.geometry("600x600")
        self.tool_data = tool_data or {}
        self.on_save = on_save
        self.result = None

        # Use defaults passed in tool_data
        self.default_modes = self.tool_data.get("modes", {})
        self.default_branches = self.tool_data.get("detection_branches", {})

        self._build_ui()
        self.transient(master)
        self.grab_set()
        self.wait_window(self)


    def _edit_json(self, field_name, initial_data):
        class JSONEditorAPI:
            def __init__(self):
                self.json_data = None
            def on_change(self, json_str):
                self.json_data = json.loads(json_str)

        api = JSONEditorAPI()
        html_path = 'file://' + __import__('os').path.abspath(__import__('os').path.join(__import__('os').path.dirname(__file__), 'jsoneditor.html'))
        window = webview.create_window(
            f'Edit {field_name}',
            html_path,
            js_api=api,
            width=800,
            height=600
        )
        # Set initial data after window loads
        def set_data():
            window.evaluate_js(f"setData({json.dumps(json.dumps(initial_data))})")
        webview.start(set_data, window)
        return api.json_data if api.json_data is not None else initial_data


    def _build_ui(self):
        # Tool Name
        tk.Label(self, text="Tool Name:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        self.name_var = tk.StringVar(value=self.tool_data.get("name", ""))
        tk.Entry(self, textvariable=self.name_var).pack(fill=tk.X, padx=10)

        # Tool Type
        tk.Label(self, text="Tool Type:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        self.type_var = tk.StringVar(value=self.tool_data.get("type", ""))
        ttk.Combobox(self, textvariable=self.type_var, values=["simple_clicker", "text_detector", "captcha_passer"]).pack(fill=tk.X, padx=10)

        # Modes (JSON) with JSON Editor
        tk.Label(self, text="Modes (JSON):").pack(anchor=tk.W, padx=10, pady=(10, 0))
        self.modes_data = self.default_modes
        btn_modes = tk.Button(self, text="Edit Modes", command=self._edit_modes)
        btn_modes.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Detection Branches (JSON) with JSON Editor
        tk.Label(self, text="Detection Branches (JSON):").pack(anchor=tk.W, padx=10, pady=(10, 0))
        self.branches_data = self.default_branches
        btn_branches = tk.Button(self, text="Edit Detection Branches", command=self._edit_branches)
        btn_branches.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=20)
        tk.Button(btn_frame, text="Save", command=self._on_save).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Cancel", command=self._on_cancel).pack(side=tk.LEFT, padx=10)

    def _edit_modes(self):
        self.modes_data = self._edit_json("Modes", self.modes_data)

    def _edit_branches(self):
        self.branches_data = self._edit_json("Detection Branches", self.branches_data)


    def _on_save(self):
        self.after(1, self.destroy)  # Always close the dialog immediately after Save is clicked
        name = self.name_var.get().strip()
        ttype = self.type_var.get().strip()
        if not name or not ttype:
            messagebox.showerror("Validation Error", "Tool name and type are required.", parent=self)
            return
        modes = self.modes_data
        branches = self.branches_data
        self.result = {"name": name, "type": ttype, "modes": modes, "detection_branches": branches}
        if self.on_save:
            try:
                self.on_save(self.result)
            except Exception as e:
                print(f"Error in on_save callback: {e}")

    def _on_cancel(self):
        self.result = None
        self.destroy()
