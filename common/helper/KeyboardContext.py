class KeyboardContext:
    """
    Manages keyboard hotkey sets for different contexts.
    """
    def __init__(self):
        self.contexts = {}
        self.current_context = None

    def add_context(self, name, hotkeys):
        """Add a new context with its hotkey definitions."""
        self.contexts[name] = hotkeys

    def set_context(self, name):
        """Switch to a different context and apply its hotkeys."""
        import keyboard
        if self.current_context:
            self.unhook_context(self.current_context)
        if name in self.contexts:
            for key, action in self.contexts[name].items():
                keyboard.add_hotkey(key, action)
            self.current_context = name
        else:
            raise ValueError(f"Context '{name}' not found.")

    def unhook_context(self, name):
        """Remove all hotkeys for a given context."""
        import keyboard
        if name in self.contexts:
            for key in self.contexts[name]:
                keyboard.remove_hotkey(key)

    def get_context(self):
        return self.current_context

    def get_contexts(self):
        return list(self.contexts.keys())
