import pyautogui
import random
import time
from itertools import count
from common.impl.tool_manager import ToolManager

# Add a tie-breaker counter
tie_breaker = count()

def move_mouse(tool_id, heartbeat_id, x, y, priority=1, duration=0):
    """
    Queues a mouse movement action to the main application's queue.

    Args:
        tool_id (str): The ID of the tool queuing the action.
        heartbeat_id (int): The heartbeat ID for obsolescence checks.
        capture_id (int): The capture ID for obsolescence checks.
        x (int): The x-coordinate to move the mouse to.
        y (int): The y-coordinate to move the mouse to.
        duration (float): The duration of the mouse movement.
    """
    delay = random.uniform(0.1, 0.5)
    ToolManager.add_task_to_queue(priority, {
        'type': 'execute',
        'call_back': time.sleep,
        'args': (delay,),
        'tool_id': tool_id,
        'heartbeat_id': heartbeat_id
    })
    ToolManager.add_task_to_queue(priority, {
        'type': 'execute',
        'call_back': pyautogui.moveTo,
        'args': (x, y, duration),
        'tool_id': tool_id,
        'heartbeat_id': heartbeat_id
    })

def click(tool_id, heartbeat_id,  priority=1, button='left'):
    """
    Queues a mouse click action to the main application's queue.

    Args:
        tool_id (str): The ID of the tool queuing the action.
        heartbeat_id (int): The heartbeat ID for obsolescence checks.
        capture_id (int): The capture ID for obsolescence checks.
        button (str): The mouse button to click ('left', 'right', 'middle').
    """
    delay = random.uniform(0.1, 0.3)
    ToolManager.add_task_to_queue(priority, {
        'type': 'execute',
        'call_back': time.sleep,
        'args': (delay,),
        'tool_id': tool_id,
        'heartbeat_id': heartbeat_id
    })
    ToolManager.add_task_to_queue(priority, {
        'type': 'execute',
        'call_back': pyautogui.click,
        'kwargs': {'button': button},
        'tool_id': tool_id,
        'heartbeat_id': heartbeat_id
    })

def double_click(tool_id, heartbeat_id,  priority=1, button='left'):
    """
    Queues a double click action to the main application's queue.

    Args:
        tool_id (str): The ID of the tool queuing the action.
        heartbeat_id (int): The heartbeat ID for obsolescence checks.
        capture_id (int): The capture ID for obsolescence checks.
        button (str): The mouse button to click ('left', 'right', 'middle').
    """
    delay = random.uniform(0.1, 0.3)
    ToolManager.add_task_to_queue(priority, {
        'type': 'execute',
        'call_back': time.sleep,
        'args': (delay,),
        'tool_id': tool_id,
        'heartbeat_id': heartbeat_id
    })
    ToolManager.add_task_to_queue(priority, {
        'type': 'execute',
        'call_back': pyautogui.doubleClick,
        'kwargs': {'button': button},
        'tool_id': tool_id,
        'heartbeat_id': heartbeat_id
    })

def queue_sleep(tool_id, heartbeat_id, duration, priority=1):
    """Queues a sleep action."""
    ToolManager.add_task_to_queue(priority, {
        'type': 'execute',
        'call_back': time.sleep,
        'args': (duration,),
        'tool_id': tool_id,
        'heartbeat_id': heartbeat_id
    })


