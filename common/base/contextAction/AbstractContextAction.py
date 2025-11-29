from abc import ABC

class AbstractContextAction(ABC):
    """
    Abstract base class for context-based action registration systems.
    """
    def activate_context(self, context_name, action_handler_map=None):
        """Base activate_context method. Should be overridden by subclasses."""
        pass
