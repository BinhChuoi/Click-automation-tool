import math
import os
from time import time
from common.base.tool_base import ToolBase
from common.helper.screen_action import move_mouse, click

MAX_ITEMS_PER_CYCLE = 2  # Limit items processed per cycle to avoid long delays

class Harvestor(ToolBase):
    TOOL_NAME = "harvestor"
    
    @staticmethod
    def get_default_configuration():
        config = ToolBase.get_default_configuration()
        
        # Load image paths
        image_paths = []
        templates_folder = os.path.join(os.path.dirname(__file__), 'harvest_templates')
        if os.path.isdir(templates_folder):
            for filename in os.listdir(templates_folder):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_paths.append(os.path.join(templates_folder, filename))

        config.update({
            'base_priority': 10,
            'number_of_click': 1,
            'detector_type': 'template_matching',
            'execution_type': 'threaded',
            'parameters': {
                'template_paths': image_paths,
                'threshold': 0.8
            },
            'sleep_period': 10
        })
        return config

    def on_detection(self, task_id, capture_id, items):
        """Callback for when items are detected."""
     
        # Update heartbeat ID
        self.heartbeat_id = time()
        self.tool_manager.update_task_heartbeat_id(self.tool_id, self.heartbeat_id)

        # Queues overlay display and tool execution.
        mapped_items = self._map_detected_objects(task_id, items)

        # Queue overlay display
        self.tool_manager.add_task_to_queue(
            self.get_configuration_value('base_priority'), {'type': 'execute', 'call_back': self.tool_manager.update_tool_overlay_objects, 'tool_id': self.tool_id, 'heartbeat_id': self.heartbeat_id, 'args': (task_id, mapped_items)}
        )

        self.execute(task_id, capture_id, mapped_items)

    def create_tasks(self):
        """Creates a new harvesting task."""
        print(f"Starting new harvest task for tool '{self.tool_id}'...")
        if not self.get_configuration_value('parameters', {}).get('template_paths'):
            print("No template images found for harvesting. Aborting.")
            return None
        
        task = self.task_manager.start_new_task(
            detector_type=self.get_configuration_value('detector_type'),
            execution_type=self.get_configuration_value('execution_type'),
            task_id="task_" + self.tool_id,
            on_detection=self.on_detection,
            on_stop=lambda: self.tool_manager.unregister_tool_instance(self.tool_id),
            parameters=self.get_configuration_value('parameters'),
            sleep_period=self.get_configuration_value('sleep_period')
        )
        return [task]

    def execute(self, task_id, capture_id, items):
        """
            Callback function to be executed when items are detected.
            When no items are detected, it simply resumes the task to continue detection loop.
            When items are detected, it pauses the task, performs harvesting actions, and then re-triggers detection after completing the actions.
        """
        print(f"Executing harvest for tool '{self.tool_id}' with {len(items)} items detected.")
        task = self.tasks.get(task_id)
        if not task:
            print(f"Warning: Task '{task_id}' not found in tool '{self.tool_id}'.")
            return

        # If no items detected, resume threading and return
        if not items:
            task.resume()
            return
        
        # Pause the threading to prevent overlapping executions
        task.pause()
        priority = self.get_configuration_value('base_priority')

        for object in items[:MAX_ITEMS_PER_CYCLE]:
            start_x = task.config['area']['x']
            start_y = task.config['area']['y']

            # The object dictionary contains center x, center y
            center_x = object['x']
            center_y = object['y']


            # print(f"Harvesting at ({start_x + center_x}, {start_y + center_y})")
            move_mouse(tool_id=self.tool_id, heartbeat_id=self.heartbeat_id, x=start_x + center_x, y=start_y + center_y, priority=priority, duration=0.2)
            for _ in range(self.get_configuration_value('number_of_click')):
                click(tool_id=self.tool_id, heartbeat_id=self.heartbeat_id, priority=priority, button='left')

            # Add remove box after harvesting, make sure the task will be called after the click task is done
                self.tool_manager.add_task_to_queue(
                    priority, {'type': 'execute', 'call_back': self.tool_manager.remove_objects_from_tool_overlay, 'tool_id': self.tool_id, 'heartbeat_id': self.heartbeat_id, 'args': (task_id, [object])}
                )
            print("Waiting briefly before next action...")

        self.tool_manager.add_task_to_queue(
            priority, {'type': 'execute', 'call_back': lambda: task.trigger_detection(), 'tool_id': self.tool_id, 'heartbeat_id': self.heartbeat_id, 'args': ()}
        )


