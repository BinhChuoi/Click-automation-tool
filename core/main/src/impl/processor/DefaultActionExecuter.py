from shared.types.Scenario import Scenario
from .ActionProcessor import ActionProcessor
from core.main.src.utils.Constants import CONFIG_DETECTION_BRANCHES, BRANCH_SCENARIOS, TEMPLATE_NAME
from core.main.src.base.processor.AbstractActionExecutor import AbstractActionExecutor
from typing import Dict

try:
    from typing import override
except ImportError:
    try:
        from typing_extensions import override
    except ImportError:
        def override(func):
            return func

class DefaultActionExecutor(AbstractActionExecutor):
    @override
    @staticmethod
    def validate(scenarios):
        if not isinstance(scenarios, list):
            raise ValueError("Scenarios must be a list.")
        id_map = {s['id']: s for s in scenarios if 'id' in s}
        if len(id_map) != len(scenarios):
            raise ValueError("Duplicate or missing scenario IDs detected.")
        
        def _validate(scenario_id):
            node = id_map.get(scenario_id)
            if not node:
                raise ValueError(f"Scenario ID '{scenario_id}' not found in id_map.")
            if 'condition' not in node:
                raise ValueError(f"Scenario '{scenario_id}' missing required 'condition' key.")
            has_children = 'childrens' in node and isinstance(node['childrens'], list) and len(node['childrens']) > 0
            has_actions = 'actions' in node and isinstance(node['actions'], list) and len(node['actions']) > 0
            if not (has_children or has_actions):
                raise ValueError(f"Scenario '{scenario_id}' must have at least one of: 'childrens' or 'actions'.")
            if has_children:
                for child_id in node['childrens']:
                    if child_id not in id_map:
                        raise ValueError(f"Child scenario ID '{child_id}' referenced in '{scenario_id}' not found.")
                    _validate(child_id)
            return True
        
        all_ids = set(id_map.keys())
        referenced = set(child_id for s in scenarios for child_id in s.get('childrens', []))
        root_ids = list(all_ids - referenced)
        if not root_ids:
            raise ValueError("At least one root scenario (not referenced as a child) is required.")
        for rid in root_ids:
            _validate(rid)
        return True
    
    @override
    def execute(self, scenario_id: str, input_data: Dict) -> bool:
        scenario = self.find_scenario(scenario_id)

        return self._process_senario(scenario, input_data)
    
    @override
    def find_scenario_param_names(self, scenario_id: str):
        import re
        scenario = self.find_scenario(scenario_id)
        condition = scenario.get('condition', '')

        identifiers = set(re.findall(r"([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*)", condition))
        return identifiers

    def _process_senario(self, scenario: Scenario, input_data: Dict) -> bool:
        """Evaluates anchor points and scenario conditions, triggers actions and/or branch if condition met."""
        action_performed = False
        condition = scenario.get('condition', '')
        object_names_map = {}
        for key, items in input_data.items():
            object_names_map[key] = [item[TEMPLATE_NAME] for item in items]

        print(f"Evaluating scenario '{scenario.get('id', '')}' with condition: {condition} and input_data keys: {list(input_data.keys())}")
        print(f"Object names map for scenario '{scenario.get('id', '')}': {object_names_map}")
        if self._evaluate_condition(condition, object_names_map) is False:
            return action_performed # Condition not met, do nothing. Travel up the stack.

        # Perform action if defined
        actions = scenario.get('actions', [])
        if actions:
            # Use ActionProcessor singleton to process actions
            processor = ActionProcessor.get_instance()
            processor.process_actions(actions, input_data)
            action_performed = True
        return action_performed
    
    @staticmethod
    def _evaluate_condition(condition, input_data: Dict):
        try:
            safe_globals = {
                "__builtins__": __builtins__,
                "any": any,
                "all": all,
                "list": list,
                "dict": dict,
                "set": set,
                "tuple": tuple,
                "input_data": input_data
            }
            print(f"Evaluating condition: {condition} with input_data: {input_data}")
            return eval(condition, safe_globals, {})
        except Exception:
            return False


# Backward-compatible alias for modules importing the legacy spelling.
DefaultActionExecuter = DefaultActionExecutor
