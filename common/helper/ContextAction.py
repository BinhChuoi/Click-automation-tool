class ContextAction:
    """
    Maps actions to keys for a given context. Allows multiple actions per context.
    """
    def __init__(self):
        self.action_map = {}

    def add_action(self, context, key, action):
        """Add an action mapped to a key for a specific context."""
        if context not in self.action_map:
            self.action_map[context] = {}
        self.action_map[context][key] = action

    def get_action(self, context, key):
        """Retrieve the action for a key in a specific context."""
        return self.action_map.get(context, {}).get(key)

    def get_actions_for_context(self, context):
        """Get all key-action pairs for a context."""
        return self.action_map.get(context, {})

    def remove_action(self, context, key):
        """Remove a key-action mapping from a context."""
        if context in self.action_map and key in self.action_map[context]:
            del self.action_map[context][key]

    def get_contexts(self):
        """List all available contexts."""
        return list(self.action_map.keys())
