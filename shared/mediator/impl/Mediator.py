import asyncio
from blinker import Signal as BlinkerSignal
from ..base.AbstractMediator import MediatorInterface
from typing import Any, Dict, Callable, Set

class BlinkerMediator(MediatorInterface):
    """
    Mediator implementation using blinker.Signal for pub/sub and asyncio for request/response.
    Singleton pattern: all calls return the same instance.
    """
    _instance = None

    @staticmethod
    def get_instance():
        if BlinkerMediator._instance is None:
            BlinkerMediator._instance = super(BlinkerMediator, BlinkerMediator).__new__(BlinkerMediator)
            BlinkerMediator._instance._init_singleton()
        return BlinkerMediator._instance

    def _init_singleton(self):
        self._signals: Dict[str, BlinkerSignal] = {}
        self._components: Set[Any] = set()
        self._subscriptions: Dict[str, Set[Callable]] = {}
        self._handlers: Dict[str, Callable] = {}

    # Coordination (optional, for direct notification/registration)
    def register(self, component: Any) -> None:
        self._components.add(component)

    def unregister(self, component: Any) -> None:
        self._components.discard(component)

    # Pub/Sub pattern
    def publish(self, event: str, *args, **kwargs) -> None:
        if event not in self._signals:
            self._signals[event] = BlinkerSignal(event)
        self._signals[event].send(self, *args, **kwargs)

    def subscribe(self, event: str, callback: Callable) -> None:
        if event not in self._signals:
            self._signals[event] = BlinkerSignal(event)
        self._signals[event].connect(callback, weak=False)
        self._subscriptions.setdefault(event, set()).add(callback)

    def unsubscribe(self, event: str, callback: Callable) -> None:
        if event in self._signals:
            self._signals[event].disconnect(callback)
        if event in self._subscriptions:
            self._subscriptions[event].discard(callback)

    # Request/Response pattern (async)
    async def request(self, event: str, *args, **kwargs) -> Any:
        handler = self._handlers.get(event)
        if handler is None:
            raise Exception(f"No handler registered for event: {event}")
        if asyncio.iscoroutinefunction(handler):
            return await handler(*args, **kwargs)
        else:
            # Run sync handler in thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: handler(*args, **kwargs))

    def register_handler(self, event: str, handler: Callable) -> None:
        self._handlers[event] = handler

    def unregister_handler(self, event: str) -> None:
        if event in self._handlers:
            del self._handlers[event]
