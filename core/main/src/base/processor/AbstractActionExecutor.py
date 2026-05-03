# --- AbstractActionExecutor: Abstract base class for action executors ---
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from shared.types.Scenario import Scenario

class AbstractActionExecutor(ABC):
    """
    Abstract base class for action executors in scenario processing.

    Scenario structure example:
        {
            "id": "test",
            "condition": "'mush_room.png' in detected_objects['default']",
            "actions": [
                {"type": "click", "templates": ["mush_room.png"], "max_items": 3},
            ],
        }
    - id: Unique identifier for the scenario (str)
    - condition: Python expression as a string, evaluated with detected_objects (str)
    - actions: List of action dicts, each with at least a 'type' key (list)
    """

    def __init__(self, scenarios: List[Scenario]):
        """
        Initialize the action executor with a list of scenarios.
        Args:
            scenarios: List of scenario dictionaries.
        """
        self.validate(scenarios)
        self.scenarios = scenarios
    
    @staticmethod
    def validate(scenarios: List[Scenario]) -> bool:
        return True
    
    @abstractmethod
    def execute(self, input_data : Any, scenario_id: str) -> Any:
        """
        Execute the action executor with the given input data and context.
        Args:
            input_data: Input data for execution (e.g., detected objects).
            context: Optional context information for execution.
        Returns:
            Any result from the execution.
        """

    @abstractmethod
    def find_scenario_param_names(self, scenario_id: str) -> List[str]:
        """
        Find and return parameters of a scenario by its ID.
        Args:
            scenario_id: The ID of the scenario to find.
        Returns:
            A dictionary of scenario parameters if found, None otherwise.
        """ 

    def find_scenario(self, scenario_id: str):
        for scenario in self.scenarios:
            if scenario.get('id') == scenario_id:
                return scenario
        return None