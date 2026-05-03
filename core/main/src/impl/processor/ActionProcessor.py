from core.main.src.helper.Dispatcher import Dispatcher
from shared.utils.Constants import INTERACTION_EVENT

class ActionProcessor:
    """
    Singleton ActionProcessor for routing actions to handlers.
    Use ActionProcessor.get_instance() to access the singleton.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.handlers = {}
            cls._instance.dispatcher = Dispatcher.get_instance()
        return cls._instance

    @classmethod
    def get_instance(cls):
        return cls.__new__(cls)

    def process_actions(self, actions, detected_objects_map):
         for action in actions:
            action_type = action.get('type')

            if action_type == 'change_mode':
                self.dispatcher.dispatch("change_mode", action.get('mode'))

            else:
                # Use Mediator to publish the event
                from shared.mediator.impl.Mediator import BlinkerMediator
                mediator = BlinkerMediator.get_instance()
                mediator.publish(
                    INTERACTION_EVENT,
                    data={
                        "action":action,
                        "detected_objects_map": detected_objects_map,
                    }
                )
