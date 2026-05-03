import pyautogui
import random
import time
from itertools import count
from presentation.PresentationManager import PresentationManager

tie_breaker = count()

def move_mouse(tool_id, heartbeat_id, x, y, priority=1, duration=0):
    delay = random.uniform(0.1, 0.5)
    PresentationManager.get_instance().add_task_to_queue(priority, {
        'type': 'execute',
        'call_back': time.sleep,
        'args': (delay,),
        'tool_id': tool_id,
        'heartbeat_id': heartbeat_id
    })
    PresentationManager.get_instance().add_task_to_queue(priority, {
        'type': 'execute',
        'call_back': pyautogui.moveTo,
        'args': (x, y, duration),
        'tool_id': tool_id,
        'heartbeat_id': heartbeat_id
    })

def click(tool_id, heartbeat_id,  priority=1, button='left'):
    PresentationManager.get_instance().add_task_to_queue(priority, {
        'type': 'execute',
        'call_back': pyautogui.click,
        'args': (),
        'tool_id': tool_id,
        'heartbeat_id': heartbeat_id
    })
