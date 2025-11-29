# Singleton

class _KeyboardManager:
    """
    Handles binding and unbinding of keyboard hotkeys using the 'keyboard' library.
    """
    def __init__(self):
        import keyboard
        self.keyboard = keyboard
        self.bound_hotkeys = {}

    def show_bound_hotkeys_gui(self):
        import tkinter as tk
        from common.impl.tool.ToolManager import ToolManager
        root = ToolManager.tk_root
        root.title("Bound Hotkeys")
        label = tk.Label(root, text="Currently bound hotkeys:")
        label.pack()

    def add_hotkey(self, key, callback, args=()):
        hotkey_id = self.keyboard.add_hotkey(key, callback, args=args)
        self.bound_hotkeys[key] = hotkey_id

    def remove_hotkey(self, key):
        if key in self.bound_hotkeys:
            self.keyboard.remove_hotkey(self.bound_hotkeys[key])
            del self.bound_hotkeys[key]

    def clear_all_hotkeys(self):
        for key in list(self.bound_hotkeys.keys()):
            self.remove_hotkey(key)


KeyboardManager = _KeyboardManager()

