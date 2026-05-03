class Dispatcher:
    """
    Singleton Dispatcher for routing events or commands to registered handlers.
    Use Dispatcher.get_instance() to access the singleton.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.handlers = {}
        return cls._instance

    @classmethod
    def get_instance(cls):
        return cls.__new__(cls)

    def register(self, event_type, handler):
        self.handlers[event_type] = handler

    def dispatch(self, event_type, *args, **kwargs):
        if event_type in self.handlers:
            return self.handlers[event_type](*args, **kwargs)
        else:
            raise ValueError(f"No handler registered for event: {event_type}")
