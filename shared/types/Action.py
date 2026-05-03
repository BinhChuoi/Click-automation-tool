from typing import Any, List, TypedDict, Optional

class Action(TypedDict, total=False):
    """
    Type definition for an action in a scenario.
    Fields:
        type: The type of action to perform (e.g., 'click', 'wait', etc.) (str)
        templates: List of template names or identifiers (optional, list of str)
        max_items: Maximum number of items to process (optional, int)
        [other fields as needed for specific action types]
    """
    type: str
    templates: Optional[List[str]]
    max_items: Optional[int]
    # Add other fields as needed for your actions
