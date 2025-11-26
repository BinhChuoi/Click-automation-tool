class KeyboardManager:
    """
    Handles binding and unbinding of keyboard hotkeys using the 'keyboard' library.
    """
    def __init__(self):
        import keyboard
        self.keyboard = keyboard
        self.bound_hotkeys = {}

    def add_hotkey(self, key, action):
        hotkey_id = self.keyboard.add_hotkey(key, action)
        self.bound_hotkeys[key] = hotkey_id

    def remove_hotkey(self, key):
        if key in self.bound_hotkeys:
            self.keyboard.remove_hotkey(self.bound_hotkeys[key])
            del self.bound_hotkeys[key]

    def clear_all_hotkeys(self):
        for key in list(self.bound_hotkeys.keys()):
            self.remove_hotkey(key)
