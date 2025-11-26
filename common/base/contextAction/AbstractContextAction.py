from abc import ABC, abstractmethod

class AbstractContextAction(ABC):
    """
    Abstract base class for context-based action registration systems.
    """
    @abstractmethod
    def register_action(self, context, action_name, action_callable):
        """Register an action for a context."""
        pass

    @abstractmethod
    def unregister_action(self, context, action_name):
        """Unregister an action from a context."""
        pass

    @abstractmethod
    def trigger_action(self, context, action_name):
        """Trigger an action by name in a context."""
        pass

    @abstractmethod
    def get_actions_for_context(self, context):
        """Get all actions for a context."""
        pass
