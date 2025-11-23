from time import time
from common.base.tool_base import ToolBase
from common.helper.screen_action import move_mouse, click

MAX_ITEMS_PER_CYCLE = 3  # Limit items processed per cycle to avoid long delays


class CaptchaPasser(ToolBase):
    TOOL_NAME = "captcha_passer"

    @staticmethod
    def get_default_configuration():
        """Provides default configuration for a new captcha passer tool."""
        config = ToolBase.get_default_configuration()
        config.update({
            'base_priority': 1,
            'detector_type': 'yolo',
            'execution_type': 'threaded',
            'parameters': {
                'model_id': 'sunflower-captcha-detection-idxoo/10',
                'api_key': 'ds4cacROzFGinfEsMrm0'
            },
            'sleep_period': 2
        })
        return config

    def on_detection(self, task_id, capture_id, items):
        """Callback for when items are detected."""

        # Update heartbeat ID
        self.heartbeat_id = time()
        self.tool_manager.update_task_heartbeat_id(self.tool_id, self.heartbeat_id)
        

        # Queues overlay display and tool execution.
        mapped_items = self._map_detected_objects(task_id, items)

        # Queue drawing overlays for detected items (high priority)
        self.tool_manager.add_task_to_queue(
            self.get_configuration_value('base_priority'), {'type': 'execute', 'call_back': self.tool_manager.update_tool_overlay_objects, 'tool_id': self.tool_id, 'heartbeat_id': self.heartbeat_id, 'args': (task_id, mapped_items, True)}
        )

        # Add task command here to remove all task in queue
        self.tool_manager.add_task_to_queue(
            0, {'type': 'execute', 'call_back': self.tool_manager.remove_all_execution_tasks, 'tool_id': self.tool_id, 'heartbeat_id': self.heartbeat_id, 'args': (self.tool_id,)}
        )

        self.execute(task_id, capture_id, mapped_items)

    def create_tasks(self):
        """Handles the logic for creating a new detection task for captchas."""
        task_id = "task_" + self.tool_id
        
        task = self.task_manager.start_new_task(
            detector_type=self.get_configuration_value('detector_type'),
            execution_type=self.get_configuration_value('execution_type'),
            task_id=task_id,
            on_detection=self.on_detection,
            on_stop=lambda: self.tool_manager.unregister_tool_instance(self.tool_id),
            parameters=self.get_configuration_value('parameters'),
            sleep_period=self.get_configuration_value('sleep_period')
        )
        return [task]

    def execute(self, task_id, capture_id, objects):
        """
            Callback function to be executed when items are detected.
            When no items are detected, it simply resumes the task to continue detection loop.
            When items are detected, it pauses the task, performs bypass captcha actions, and then re-triggers detection after completing the actions.
        """
        print(f"Executing harvest for tool '{self.tool_id}' with {len(objects)} items detected.")

        task = self.tasks.get(task_id)
        if not task:
            print(f"Warning: Task '{task_id}' not found in tool '{self.tool_id}'.")
            return

        # If no items detected, resume threading and return
        if not objects:
            task.resume()
            return
        
        # Pause the threading to prevent overlapping executions
        task.pause()
        priority = self.get_configuration_value('base_priority')

        for object in objects[:MAX_ITEMS_PER_CYCLE]:
            start_x = task.config['area']['x']
            start_y = task.config['area']['y']

            # The object dictionary contains center x, center y
            center_x = object['x']
            center_y = object['y']

            print(f"Harvesting at ({start_x + center_x}, {start_y + center_y})")
            move_mouse(tool_id=self.tool_id, heartbeat_id=self.heartbeat_id, x=start_x + center_x, y=start_y + center_y, priority=priority, duration=0.2)
            click(tool_id=self.tool_id, heartbeat_id=self.heartbeat_id, priority=priority, button='left')
            print("Waiting briefly before next action...")
             # Add remove box after harvesting, make sure the task will be called after the click task is done
            self.tool_manager.add_task_to_queue(
                priority, {'type': 'execute', 'call_back': self.tool_manager.remove_objects_from_tool_overlay, 'tool_id': self.tool_id, 'heartbeat_id': self.heartbeat_id, 'args': (task_id, [object])}
            )

        # Add a conditional check for no interaction tasks
        self.tool_manager.add_task_to_queue(
            priority, {
                'type': 'execute',
                'call_back': self.tool_manager.resume_all_execution_tasks,
                'tool_id': self.tool_id,
                'heartbeat_id': self.heartbeat_id,
                'args': (self.tool_id,)
            }
        )

        # Re-trigger detection after completing all actions to post-check for any remaining captchas and continue the loop
        self.tool_manager.add_task_to_queue(
            priority, {'type': 'execute', 'call_back': lambda: task.trigger_detection(), 'tool_id': self.tool_id, 'heartbeat_id': self.heartbeat_id, 'args': ()}
        )

    def start(self):
        """Starts the captcha passer tool."""
        print(f"Starting Captcha Passer tool '{self.tool_id}'.")
        super().start()
