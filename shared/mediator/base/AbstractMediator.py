from abc import ABC, abstractmethod
from typing import Any

class MediatorInterface(ABC):
    """
    Interface for the Mediator pattern supporting both pub/sub and request/response.
    Implementations should provide methods for registering/unregistering components,
    publishing events, subscribing to events, and handling request/response.
    """

    @abstractmethod
    def register(self, component: Any) -> None:
        """Register a component with the mediator (for coordination or direct notification)."""
        pass

    @abstractmethod
    def unregister(self, component: Any) -> None:
        """Unregister a component from the mediator."""
        pass

    @abstractmethod
    def publish(self, event: str, *args, **kwargs) -> None:
        """Publish an event to all subscribers (pub/sub pattern)."""
        pass

    @abstractmethod
    def subscribe(self, event: str, callback: Any) -> None:
        """Subscribe a callback to an event (pub/sub pattern)."""
        pass

    @abstractmethod
    def unsubscribe(self, event: str, callback: Any) -> None:
        """Unsubscribe a callback from an event (pub/sub pattern)."""
        pass

    @abstractmethod
    async def request(self, event: str, *args, **kwargs) -> Any:
        """Send a request and await a response (request/response pattern)."""
        pass

    @abstractmethod
    def register_handler(self, event: str, handler: Any) -> None:
        """Register a handler for a request/response event."""
        pass

    @abstractmethod
    def unregister_handler(self, event: str) -> None:
        """Unregister the handler for a request/response event."""
        pass
