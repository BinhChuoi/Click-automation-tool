# --- Sample Configuration for ContextActionExecutor ---
# This is a flat array of scenarios, each with a unique 'id'.
# Scenarios can reference children by 'childrens' (list of ids), and/or have 'actions'.
# The 'not' option inverts the condition logic if set to true.
SAMPLE_SCENARIOS = [
    {
        "id": "main",
        "condition": "A or B",
        "childrens": ["sub1", "sub2"]
    },
    {
        "id": "sub1",
        "condition": "C",
        "actions": [
            {"type": "click", "templates": ["C"], "max_items": 1}
        ]
    },
    {
        "id": "sub2",
        "condition": "not D",
        "not": True,
        "actions": [
            {"type": "click", "templates": ["E"], "max_items": 2}
        ],
        "childrens": ["leaf"]
    },
    {
        "id": "leaf",
        "condition": "F and G",
        "actions": [
            {"type": "click", "templates": ["F", "G"], "max_items": 1}
        ]
    }
]


import time
import os
import itertools
from common.base.tool_base import ToolBase
from common.helper.screen_action import move_mouse, click
from common.utils.context_action_executor import ContextActionExecutor

# Configuration Keys
CONFIG_DETECTION_BRANCHES = 'detection_branches'
CONFIG_AVAILABLE_TEMPLATES = 'available_templates'
CONFIG_PARAMETERS = 'parameters'
CONFIG_TEMPLATE_PATHS = 'template_paths'

# Branch Keys
BRANCH_ANCHORS = 'anchors'  # List of anchor point template names
BRANCH_SCENARIOS = 'scenarios'  # List of scenario dicts: {condition, branch}

# State Keys
STATE_EXECUTION_STACK = 'execution_stack'
STATE_BRANCH_NAME = 'branch_name'
STATE_INDEX = 'index'

# Template Keys
TEMPLATE_NAME = 'class_name'
TEMPLATE_PATH = 'path'


def _scan_for_shared_templates():
    """
    Scans the 'simple_clicker_templates' directory for image files.
    This function is executed once when the module is loaded, and the result
    is cached in the _SHARED_TEMPLATES constant.
    """
    templates = []
    templates_folder = os.path.join(os.path.dirname(__file__), 'simple_clicker_templates')
    if os.path.isdir(templates_folder):
        for filename in os.listdir(templates_folder):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                templates.append({TEMPLATE_NAME: filename, TEMPLATE_PATH: os.path.join(templates_folder, filename)})
    return templates

# This constant is populated once when the script is loaded, providing a shared cache.
_SHARED_TEMPLATES = _scan_for_shared_templates()


DEFAULT_MODE = 'main'
CAPTCHA_PASSER_MODE = 'captcha_passer'

# Refactored: Each mode maps to a list of detector configs (one per detector type)
MODE_TASK_CONFIG = {
    DEFAULT_MODE: [
    # {
    #     "id": "default",
    #     "execution_type": "non_threaded",
    #     "area" : { "x": 0, "y": 0, "width": 1920, "height": 1080 },
    #     "detectors": [{
    #         'detector_type': 'template_matching',
    #         'parameters': {
    #             CONFIG_TEMPLATE_PATHS: [], # Placeholder to prevent error, will be updated dynamically
    #             'threshold': 0.8
    #         }
    #     }]
    # },
    {
        "id": "tool_text",
        "execution_type": "non_threaded",
        "area" : { "x": 1800, "y": 365, "width": 120, "height": 120 },
        "detectors": [{
            'detector_type': 'text',
            'parameters': {
                
            }
        }]
    }
    ],
    # CAPTCHA_PASSER_MODE: [{
    #     "id": "captcha_passer",
    #     "execution_type": "non_threaded",
    #     "area" : { "x": 0, "y": 0, "width": 1920, "height": 1080 },
    #     "detectors": [{
    #         'detector_type': 'yolo',
    #         'parameters': {
    #             "model_id": "sunflower-captcha-detection-idxoo/12",
    #             "api_key": "ds4cacROzFGinfEsMrm0"
    #         }
    #     }]
    # }]
}


class SimpleClicker(ToolBase):

    def change_mode(self, mode):
        """
        Switches the tool's mode, manages pausing/resuming tasks, and clears the execution stack.
        Resumes the task associated with the selected mode, pauses all others.
        """
        self.mode = mode
        self.mode_retry_count = 0
        self.objects_detected = {} # task_id -> [previously detected objects]

        self.execution_stack.clear()
        self.tool_manager.remove_all_execution_tasks(self.tool_id) # Terminate old non-running tasks

        # Create new tasks for the mode if not present
        tasks = self.load_tasks(mode=mode)
        self.mode_tasks[mode] = {task.task_id: task for task in tasks}

        # Resume only the tasks for the new target mode, pause all others
        for m, tasks in self.mode_tasks.items():
            for task in tasks.values():
                if m == mode:
                    task.resume()
                else:
                    task.pause()

        self._load_all_scenarios() # Load scenarios for the new mode
        self._schedule_next_detection()

    """
    A highly configurable tool that acts as a state machine for UI automation.

    The SimpleClicker operates based on a "detection_branches" configuration, which
    defines a graph of states (branches). The tool navigates this graph to perform
    complex, conditional automation tasks.

    Key Concepts:
    - Branches: A branch is a state that defines a set of actions. There are two main types:
        1. Decision Branch: Contains a "detect" key with a list of templates to look
           for simultaneously. An "on_match" key maps each template to a new branch
           to transition to upon detection.
        2. Sequence Branch: Contains a "sequence" key with an ordered list of steps
           to execute. Steps can be template names (to detect and click) or nested
           decision branches.

    - Execution Stack: A stack (`self.execution_stack`) tracks the tool's current
      position in the branch graph. Each item on the stack holds the state for a
      branch, including the current `index` within its sequence. This allows for
      deeply nested and recursive logic.

    - State Machine: The core logic is in `load_next_action`, which acts as the state
      machine's transition function. It inspects the current state on the stack
      and determines the next action, whether it's detecting templates for a
      decision, processing a sequence step, or transitioning between branches.
    """
    TOOL_NAME = "simple_clicker"

    def __init__(self, tool_manager, tool_data=None, tool_configuration=None):
        if tool_configuration and CONFIG_DETECTION_BRANCHES not in tool_configuration:
            raise ValueError(f"Configuration must include '{CONFIG_DETECTION_BRANCHES}'")
        # Perform validate on the scenarios if they exist
        if tool_configuration and BRANCH_SCENARIOS in tool_configuration.get(CONFIG_DETECTION_BRANCHES, {}):
            ContextActionExecutor.validate_scenario_tree(tool_configuration[CONFIG_DETECTION_BRANCHES][BRANCH_SCENARIOS])
        # Only use tool_manager, ignore task_manager
        super().__init__(tool_manager, tool_data, tool_configuration)
        self.tool_configuration[CONFIG_AVAILABLE_TEMPLATES] = _SHARED_TEMPLATES
        self.execution_stack = []  # Stack to manage branch execution state
        self.mode = DEFAULT_MODE  # Default mode
        self.mode_retry_count = 0  # Count of retries in current mode

    @staticmethod
    def get_default_configuration():
        """Provides a default configuration structure for the SimpleClicker tool."""
        config = ToolBase.get_default_configuration()
        config.update({
            'base_priority': 5,
            CONFIG_DETECTION_BRANCHES: {},
            CONFIG_AVAILABLE_TEMPLATES: _SHARED_TEMPLATES,
            'sleep_period': 1
        })
        return config

    def _get_template_by_name(self, template_name):
        """Finds a template's full data from its name."""
        for t in self.tool_configuration.get(CONFIG_AVAILABLE_TEMPLATES, []):
            if t[TEMPLATE_NAME] == template_name:
                return t
        return None


    def _handle_current_scenario(self, detected_objects):
        """Evaluates anchor points and scenario conditions, triggers actions and/or branch if condition met."""
        current_scenario = self.execution_stack.pop()
        action_performed = False

        # Processing dected_objects for next steps
        object_names_map = {}
        for key, items in detected_objects.items():
            object_names_map[key] = [item[TEMPLATE_NAME] for item in items]

        print("Detected scenario:", self.mode, current_scenario["id"], object_names_map)

        if ContextActionExecutor.evaluate_scenario_condition(current_scenario, object_names_map) is False:
            return action_performed # Condition not met, do nothing. Travel up the stack.

        # Perform action if defined
        actions = current_scenario.get('actions', [])
        if actions:
            self._perform_scenario_actions(actions, detected_objects)
            action_performed = True

        # After performing actions, add children scenarios to stack
        for child_id in current_scenario.get('childrens', []):
            self.execution_stack.append(ContextActionExecutor.get_scenario_by_id(self.tool_configuration.get(CONFIG_DETECTION_BRANCHES, {}).get(BRANCH_SCENARIOS, []), child_id))

        return action_performed

    def _schedule_next_detection(self):
        if not self.execution_stack:
            # No scenarios loaded for current mode, reload based on current mode as a fallback
            self.mode_retry_count += 1
            if self.mode_retry_count > 5:
                print(f"Max retries reached in mode '{self.mode}'. Resetting to default mode.")
                self.mode = DEFAULT_MODE
                self.mode_retry_count = 0
            self._load_all_scenarios()
       
        # Loop over running tasks which have detector type 'template_matching' and update their templates
        for task in self.mode_tasks.get(self.mode, {}).values():
            if task.is_alive() and not task.is_paused():

                next_scenario = self.execution_stack[-1]
                object_names = ContextActionExecutor.extract_filename_from_condition(next_scenario)
                template_paths = []
                for name in object_names:
                    template = self._get_template_by_name(name)
                    if template:
                        template_paths.append(template[TEMPLATE_PATH])

                task.update_detector_params({
                    CONFIG_TEMPLATE_PATHS: template_paths
                }, 'template_matching')

    def _load_all_scenarios(self):
        """Loads all scenarios into the execution stack."""
        scenarios = self.tool_configuration.get(CONFIG_DETECTION_BRANCHES, {}).get(BRANCH_SCENARIOS, [])
        for scenario in scenarios:
            if scenario.get('mode', DEFAULT_MODE) == self.mode:
                self.execution_stack.append(scenario)

    def _perform_scenario_actions(self, actions, detected_objects):
        """Perform actions (e.g., click) on matched objects as defined in scenario actions."""
        for action in actions:
            action_type = action.get('type')
            templates = action.get('templates', [])
            max_items = action.get('max_items', 1)
            click_count = action.get('click_count', 1)  # New option, default 1
            for task_id in self.mode_tasks.get(self.mode, {}):
                task_config = self.mode_tasks[self.mode][task_id].config
                objects = self.objects_detected.get(task_id, [])
                # Find matched objects for the specified templates
                matched_objs = [item for item in objects if item[TEMPLATE_NAME] in templates][:max_items]
                if action_type == 'click':
                    for obj in matched_objs:
                        area = task_config.get('area', {})
                        x = area.get('x', 0) + obj['x'] 
                        y = area.get('y', 0) + obj['y']
                        priority = self.get_configuration_value('base_priority')
                        print(f"Scenario action: Clicking at ({x}, {y}) for template '{obj[TEMPLATE_NAME]}' (center of box, area-relative), {click_count} time(s)")
                        move_mouse(tool_id=self.tool_id, heartbeat_id=self.heartbeat_id, x=x, y=y, priority=priority, duration=0.2)
                        for _ in range(click_count):
                            click(tool_id=self.tool_id, heartbeat_id=self.heartbeat_id, priority=priority, button='left')
                        
            if action_type == 'change_mode':
                # Make sure all interactions complete before changing mode
                self.tool_manager.add_task_to_queue(
                        self.get_configuration_value('base_priority'), {'type': 'execute', 'call_back': lambda: self.change_mode(action.get('mode')), 'tool_id': self.tool_id, 'heartbeat_id': self.heartbeat_id, 'args': ()}
                    )

    def load_tasks(self, mode=DEFAULT_MODE):
        """Creates a single detection task per mode, with all detectors for that mode."""
        tasks = []
        task_configs = MODE_TASK_CONFIG.get(mode, [])

        for task_config in task_configs:
            detector_configs = task_config.get('detectors', [])
            area = task_config.get('area', {})
            task_id = task_config.get('id')
            if mode in self.mode_tasks and task_id in self.mode_tasks[mode]:
                tasks.append(self.mode_tasks[mode][task_id])
                continue

            # Use execution_type from config, fallback to 'non_threaded'
            execution_type = task_config.get('execution_type', 'non_threaded')
            task = self.tool_manager.start_new_task(
                execution_type=execution_type,
                task_id=task_id,
                on_detection=self.on_detection,
                on_stop=lambda: print(f"SimpleClicker tool '{self.tool_id}' {mode} task stopped."),
                detectors=detector_configs,
                sleep_period=self.get_configuration_value('sleep_period'),
                area=area
            )
            self.tool_manager.show_tool_overlay(self.tool_id, area)
            tasks.append(task)
        return tasks

    def on_detection(self, task_id, capture_id, objects):
        """Callback for when items are detected."""
        # Update heartbeat ID
        self.heartbeat_id = time.time()
        self.tool_manager.update_task_heartbeat_id(self.tool_id, self.heartbeat_id)

        # Queues overlay display and tool execution.
        mapped_items = self._map_detected_objects(task_id, objects)

        # Queue overlay display
        self.tool_manager.add_task_to_queue(
            self.get_configuration_value('base_priority'), {'type': 'execute', 'call_back': self.tool_manager.update_tool_overlay_objects, 'tool_id': self.tool_id, 'heartbeat_id': self.heartbeat_id, 'args': (self.tool_id, objects)}
        )

        # Store detected objects for potential future use
        self.objects_detected[task_id] = mapped_items

        self.process_detection_results(task_id)
    
    def process_detection_results(self, task_id):
        """Processes detection results for the given task."""
        if not self.execution_stack:
            return  # No scenarios loaded, ignore detection

        priority = self.get_configuration_value('base_priority')
        task = self.mode_tasks.get(self.mode, {}).get(task_id)

        action_performed = self._handle_current_scenario(self.objects_detected) # Be aware that this may modify the execution stack and mode
        self.tool_manager.add_task_to_queue(
            priority, {'type': 'execute', 'call_back': lambda: self._schedule_next_detection(), 'tool_id': self.tool_id, 'heartbeat_id': self.heartbeat_id, 'args': ()}
        )
        if action_performed:
             # Wait for all interactions to complete before triggering next detection
            task.set_detection_enabled(False)
            self.tool_manager.add_task_to_queue(
                priority, {'type': 'execute', 'call_back': lambda: task.set_detection_enabled(True), 'tool_id': self.tool_id, 'heartbeat_id': self.heartbeat_id, 'args': ()}
            )