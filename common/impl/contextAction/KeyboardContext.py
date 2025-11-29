from common.base.contextAction.AbstractContextAction import AbstractContextAction
from common.utils.Settings import load_settings
from common.impl.contextAction.KeyboardManager import KeyboardManager

class KeyboardContext(AbstractContextAction):
    """
    Manages keyboard hotkey sets for different contexts.
    """
    def __init__(self):
        self.current_context = None

        # Load mappings from settings utility
        settings = load_settings()
        self.keyboard_mappings = settings.get('keyboard_mappings', {})

    def activate_context(self, context_name, action_handler_map=None):
        """Activate a context by name."""
        if context_name in self.keyboard_mappings:
            self.current_context = context_name
            KeyboardManager.clear_all_hotkeys()

            if action_handler_map:
                for action_name, handler_tuple in action_handler_map.items():
                    handler, args = handler_tuple
                    hotkey = self.keyboard_mappings[context_name].get(action_name)
                    if hotkey is not None:
                        KeyboardManager.add_hotkey(hotkey, handler, args)
        else:
            raise ValueError(f"Context '{context_name}' not found in keyboard mappings.")
