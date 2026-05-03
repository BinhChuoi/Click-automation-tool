from typing import List, TypedDict
from shared.types.Action import Action

class Scenario(TypedDict, total=False):
    """
    Type definition for a scenario used in action executors.
    Fields:
        id: Unique identifier for the scenario (str)
        condition: Python expression as a string, evaluated with detected_objects (str)
        actions: List of Action objects, each with at least a 'type' key (list)
    """
    id: str
    condition: str
    actions: List[Action]
