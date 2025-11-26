from common.base.contextAction.AbstractContextAction import AbstractContextAction

import yaml
import os

class KeyboardContext(AbstractContextAction):
    """
    Manages keyboard hotkey sets for different contexts.
    """
    def __init__(self, keyboard_manager, action_map, config_path=None):
        self.contexts = {}  # {context: {action_name: hotkey}}
        self.current_context = None
        self.keyboard_manager = keyboard_manager
        self.action_map = action_map  # {action_name: callable}
        # Load mappings from YAML config if provided
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), '../../config.yaml')
        config_path = os.path.abspath(config_path)
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            mappings = config.get('keyboard_mappings', {})
            for context, actions in mappings.items():
                self.add_context(context, actions)

    def get_actions_for_context(self, context):
        """Get all actions for a context."""
        return list(self.contexts.get(context, {}).keys())


    def register_action(self, context, action_name, action_callable):
        """Register an action for a context."""
        if context not in self.contexts:
            self.contexts[context] = {}
        self.contexts[context][action_name] = action_callable

    def unregister_action(self, context, action_name):
        """Unregister an action from a context."""
        if context in self.contexts and action_name in self.contexts[context]:
            del self.contexts[context][action_name]

    def trigger_action(self, context, action_name):
        """Trigger an action by name in a context."""
        if context in self.contexts and action_name in self.contexts[context]:
            self.contexts[context][action_name]()
        else:
            raise ValueError(f"Action '{action_name}' not found in context '{context}'.")

    def add_context(self, name, action_hotkey_map):
        """Add a new context with its action-to-hotkey mapping."""
        self.contexts[name] = action_hotkey_map

    def set_context(self, name):
        """Switch to a different context and bind its hotkeys to actions."""
        if self.current_context:
            self.unhook_context(self.current_context)
        if name in self.contexts:
            for action_name, hotkey in self.contexts[name].items():
                action_callable = self.action_map.get(action_name)
                if action_callable:
                    self.keyboard_manager.add_hotkey(hotkey, action_callable)
            self.current_context = name
        else:
            raise ValueError(f"Context '{name}' not found.")

    def unhook_context(self, name):
        """Remove all hotkeys for a given context."""
        if name in self.contexts:
            for action_name, hotkey in self.contexts[name].items():
                self.keyboard_manager.remove_hotkey(hotkey)

    def get_context(self):
        return self.current_context

    def get_contexts(self):
        return list(self.contexts.keys())
