from presentation.base.contextAction.AbstractContextAction import AbstractContextAction
from utils.Configuration import load_configuration
from presentation.contextAction.KeyboardManager import KeyboardManager

class KeyboardContext(AbstractContextAction):
    """
    Manages keyboard hotkey sets for different contexts.
    """
    def __init__(self):
        self.current_context = None
        config = load_configuration()
        self.keyboard_mappings = config.get('keyboard_mappings', {})
        self._overlay_window = None

    def activate_context(self, context_name, action_handler_map=None):
        """Activate a context by name. Returns set of bound hotkeys."""
        bound_hotkeys = []
        if context_name in self.keyboard_mappings:
            self.current_context = context_name
            KeyboardManager.clear_all_hotkeys()
            # Remove overlay management from KeyboardContext
            if action_handler_map:
                for action_name, handler_tuple in action_handler_map.items():
                    handler, args = handler_tuple
                    hotkey = self.keyboard_mappings[context_name].get(action_name)
                    if hotkey is not None:
                        KeyboardManager.add_hotkey(hotkey, handler, args)
                        bound_hotkeys.append(hotkey)
        else:
            raise ValueError(f"Context '{context_name}' not found in keyboard mappings.")
        return tuple(bound_hotkeys)
