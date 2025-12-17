import tkinter as tk
from tkinter import scrolledtext, messagebox
from tkinter import ttk
import json
import jsonschema


class DetectionBranchesDialog:
    def __init__(self, tk_root, default_detection_branches, schema, draft, close_callback=None):
        self.result = {}
        self.draft = draft
        self.close_callback = close_callback
        self.window = tk.Toplevel(tk_root)
        self.window.title("Enter Detection Branches JSON Configuration")
        self.window.geometry("700x600")
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()
        self.window.attributes('-topmost', True)
        label = tk.Label(self.window, text="Paste your detection_branches JSON configuration below:")
        label.pack(pady=5)
        self.text_area = scrolledtext.ScrolledText(self.window, wrap=tk.WORD, width=80, height=25)
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.text_area.insert(tk.END, default_detection_branches)
        style = ttk.Style(self.window)
        style.configure('Big.TButton', font=('TkDefaultFont', 12), padding=(10, 10), height=40)
        submit_btn = ttk.Button(self.window, text="Submit", command=self.on_submit, style='Big.TButton')
        submit_btn.pack(padx=20, pady=10, fill=tk.X)
        self.schema = schema
        self.window.transient(tk_root)
        self.window.grab_set()
        tk_root.wait_window(self.window)

    def on_submit(self):
        try:
            config = json.loads(self.text_area.get("1.0", tk.END))
            jsonschema.validate(config, self.schema)
            self.draft['detection_branches'] = config
            messagebox.showinfo("Success", "Detection branches loaded and validated successfully!")
            self.window.destroy()
            if self.close_callback:
                self.close_callback(json.loads(config))
        except jsonschema.ValidationError as ve:
            messagebox.showerror("Validation Error", f"JSON does not match schema: {ve.message}")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid JSON: {e}")

class ToolModeDialog:
    def __init__(self, tk_root,  default_mode_task_config, schema, draft, close_callback=None):
        self.result = {}
        self.draft = draft
        self.close_callback = close_callback
        self.window = tk.Toplevel(tk_root)
        self.window.title("Enter Tool Mode JSON Configuration")
        self.window.geometry("600x500")
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()
        self.window.attributes('-topmost', True)
        label = tk.Label(self.window, text="Paste your tool mode JSON configuration below:")
        label.pack(pady=5)
        self.text_area = scrolledtext.ScrolledText(self.window, wrap=tk.WORD, width=70, height=20)
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.text_area.insert(tk.END, default_mode_task_config)
        style = ttk.Style(self.window)
        style.configure('Big.TButton', font=('TkDefaultFont', 12), padding=(10, 10), height=40)
        submit_btn = ttk.Button(self.window, text="Submit", command=self.on_submit, style='Big.TButton')
        submit_btn.pack(padx=20, pady=10, fill=tk.X)
        self.schema = schema
        self.window.transient(tk_root)
        self.window.grab_set()
        print("ToolModeDialog closed.")

    def on_submit(self):
        try:
            config = json.loads(self.text_area.get("1.0", tk.END))
            jsonschema.validate(config, self.schema)
            self.window.destroy()
            if self.close_callback:
                self.close_callback(json.loads(config))
        except jsonschema.ValidationError as ve:
            messagebox.showerror("Validation Error", f"JSON does not match schema: {ve.message}")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid JSON: {e}")
