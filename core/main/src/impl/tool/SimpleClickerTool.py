
import os
from core.main.src.base.tool.BaseTool import BaseTool
from core.main.src.base.processor.AbstractActionExecutor import AbstractActionExecutor
from core.main.src.utils.Constants import (
    CONFIG_DETECTION_BRANCHES,
    CONFIG_AVAILABLE_TEMPLATES,
    CONFIG_TEMPLATE_PATHS,
    BRANCH_SCENARIOS,
    TEMPLATE_NAME,
    TEMPLATE_PATH
)
from shared.utils.Constants import INTERACTION_EVENT, TASK_STARTED_EVENT
from core.main.src.helper.Dispatcher import Dispatcher

DEFAULT_MODE = 'main'
CAPTCHA_PASSER_MODE = 'captcha_passer'


class SimpleClicker(BaseTool):

    def change_mode(self, mode):
        """
        Switches the tool's mode, manages pausing/resuming tasks, and clears the execution stack.
        Resumes the task associated with the selected mode, pauses all others.
        """
        self.mode = mode
        self.mode_retry_count = 0
        self.objects_detected = {} # task_id -> [previously detected objects]

        self.execution_stack.clear()

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

    def __init__(self, tool_configuration=None, executor_class=None):
        if tool_configuration and CONFIG_DETECTION_BRANCHES not in tool_configuration:
            raise ValueError(f"Configuration must include '{CONFIG_DETECTION_BRANCHES}'")
        if tool_configuration and 'modes' not in tool_configuration:
            raise ValueError("Configuration must include 'modes' for tool modes and tasks.")
        if (executor_class is None):
            raise ValueError("An AbstractActionExecutor instance must be provided to SimpleClickerTool.")
        
        # Perform validate on the scenarios if they exist
        # if tool_configuration and BRANCH_SCENARIOS in tool_configuration.get(CONFIG_DETECTION_BRANCHES, {}):
        #     ContextActionExecutor.validate_scenario_tree(tool_configuration[CONFIG_DETECTION_BRANCHES][BRANCH_SCENARIOS])
        # Only use tool_manager, ignore task_manager
        super().__init__(tool_configuration)
        self.execution_stack = []  # Stack to manage branch execution state
        self.mode = DEFAULT_MODE  # Default mode
        self.mode_retry_count = 0  # Count of retries in current mode

        self.executor = executor_class(
            tool_configuration.get(CONFIG_DETECTION_BRANCHES, {}).get(BRANCH_SCENARIOS, [])
        )
        self.dispatcher = Dispatcher.get_instance()
        self.dispatcher.register("change_mode", self.change_mode)

    @staticmethod
    def get_default_configuration():
        """Provides a default configuration structure for the SimpleClicker tool."""
        config = BaseTool.get_default_configuration()
        config.update({
            'base_priority': 5,
            CONFIG_DETECTION_BRANCHES: {},
            'sleep_period': 1
        })
        return config

    def _handle_current_scenario(self):
        """Evaluates anchor points and scenario conditions, triggers actions and/or branch if condition met."""
        current_scenario = self.execution_stack.pop()
        # Processing dected_objects for next steps
        global_detected_objects_map = {}
        for task_id in self.mode_tasks.get(self.mode, {}):
            task_config = self.mode_tasks[self.mode][task_id].config
            objects = self.objects_detected.get(task_id, [])
           
            # Convert matched objs local positions to global positions
            for obj in objects:
                area = task_config.get('area', {})
                obj['x'] += area.get('x', 0)
                obj['y'] += area.get('y', 0)

            global_detected_objects_map.setdefault(task_id, []).extend(objects)

        action_performed =  self.executor.execute(current_scenario.get('id'), global_detected_objects_map)
        if action_performed:
            # After performing actions, add children scenarios to stack
            for child_id in current_scenario.get('childrens', []):
                self.execution_stack.append(self.executor.find_scenario(child_id))
        
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
       
        # Loop over running tasks which have detector type 'template' and update their templates
        for task in self.mode_tasks.get(self.mode, {}).values():
            if task.is_alive() and not task.is_paused():

                next_scenario = self.execution_stack[-1]
                object_names = self.executor.find_scenario_param_names(next_scenario.get('id'))
                task.update_detector_configuration({
                    "template_names": object_names
                }, 'template')

    def _load_all_scenarios(self):
        """Loads all scenarios into the execution stack."""
        scenarios = self.tool_configuration.get(CONFIG_DETECTION_BRANCHES, {}).get(BRANCH_SCENARIOS, [])
        for scenario in scenarios:
            if scenario.get('mode', DEFAULT_MODE) == self.mode:
                self.execution_stack.append(scenario)

    def load_tasks(self, mode=DEFAULT_MODE):
        """Creates a single detection task per mode, with all detectors for that mode."""
        tasks = []
        task_configs = self.tool_configuration.get('modes', {}).get(mode, [])

        for task_config in task_configs:
            detectors = task_config.get('detectors', [])
            area = task_config.get('area', {})
            task_id = task_config.get('id')
            if mode in self.mode_tasks and task_id in self.mode_tasks[mode]:
                tasks.append(self.mode_tasks[mode][task_id])
                continue

            # Use execution_type from config, fallback to 'non_threaded'
            execution_type = task_config.get('execution_type', 'non_threaded')
            task = self.start_new_task(
                execution_type=execution_type,
                task_id=task_id,
                on_detection=self.on_detection,
                on_stop=lambda: print(f"SimpleClicker tool '{self.tool_id}' {mode} task stopped."),
                detectors=detectors,
                sleep_period=self.get_configuration_value('sleep_period'),
                area=area
            )

            # Use Mediator to publish the event
            from shared.mediator.impl.Mediator import BlinkerMediator
            mediator = BlinkerMediator.get_instance()
            mediator.publish(
                TASK_STARTED_EVENT,
                data={**task_config, 'id': task_id, 'tool_id': self.tool_id}
            )
            # self.tool_manager.show_tool_overlay(self.tool_id, area)
            tasks.append(task)
        return tasks

    def on_detection(self, task_id, capture_id, objects):
        """Callback for when items are detected."""
        # # Update heartbeat ID
        # self.heartbeat_id = time.time()
        # self.tool_manager.update_task_heartbeat_id(self.tool_id, self.heartbeat_id)

        # # Queues overlay display and tool execution.
        mapped_items = self._map_detected_objects(task_id, objects)

        # Store detected objects for potential future use
        self.objects_detected[task_id] = mapped_items

        # Fire event with all current detected objects
        from shared.mediator.impl.Mediator import BlinkerMediator
        mediator = BlinkerMediator.get_instance()
        from shared.utils.Constants import TOOL_HEARTBEAT_EVENT
        event_data = {
            "tool_id": self.tool_id,
            "detected_objects": self.objects_detected.copy(),
            "task_id": task_id,
            "capture_id": capture_id
        }
        mediator.publish(TOOL_HEARTBEAT_EVENT, data=event_data)

        self.process_detection_results(task_id)
    
    def process_detection_results(self, task_id):
        """Processes detection results for the given task."""
        if not self.execution_stack:
            return  # No scenarios loaded, ignore detection

        self._handle_current_scenario() # Be aware that this may modify the execution stack and mode
        self._schedule_next_detection()
        # self.tool_manager.add_task_to_queue(
        #     priority, {'type': 'execute', 'call_back': lambda: self._schedule_next_detection(), 'tool_id': self.tool_id, 'heartbeat_id': self.heartbeat_id, 'args': ()}
        # )
        # if action_performed:
        #      # Wait for all interactions to complete before triggering next detection
        #     task.set_detection_enabled(False)
        #     self.tool_manager.add_task_to_queue(
        #         priority, {'type': 'execute', 'call_back': lambda: task.set_detection_enabled(True), 'tool_id': self.tool_id, 'heartbeat_id': self.heartbeat_id, 'args': ()}
        #     )