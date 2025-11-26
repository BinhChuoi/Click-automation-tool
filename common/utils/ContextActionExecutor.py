# --- ContextActionExecutor as a configuration parser/reader ---
class ContextActionExecutor:
    BRANCH_ANCHORS = 'anchors'  # List of anchor point template names
    BRANCH_SCENARIOS = 'scenarios'  # List of scenario dicts: {condition, branch, actions}
    @staticmethod
    def validate_scenario_tree(scenarios):
        # ...existing code...
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
    @staticmethod
    def evaluate_scenario_condition(scenario, detected_objects):
        condition = scenario.get('condition')
        if not condition:
            return False
        result = ContextActionExecutor._evaluate_condition(condition, detected_objects)
        if scenario.get('not', False):
            return not result
        return result
    @staticmethod
    def _evaluate_condition(condition, detected_objects):
        try:
            safe_globals = {
                "__builtins__": __builtins__,
                "any": any,
                "all": all,
                "list": list,
                "dict": dict,
                "set": set,
                "tuple": tuple,
                "detected_objects": detected_objects
            }
            return eval(condition, safe_globals, {})
        except Exception:
            return False
    @staticmethod
    def extract_filename_from_condition(scenario):
        import re
        import keyword
        condition = scenario.get('condition', '')
        identifiers = set(re.findall(r"([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*)", condition))
        return identifiers
    @staticmethod
    def get_scenario_by_id(scenarios, scenario_id):
        for scenario in scenarios:
            if scenario.get('id') == scenario_id:
                return scenario
        return None
