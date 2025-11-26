import time
import os
import itertools
from common.base.tool.BaseTool import BaseTool
from common.helper.screen_action import move_mouse, click
from common.utils.ContextActionExecutor import ContextActionExecutor
SAMPLE_SCENARIOS = [
    # ...existing code...
]
CONFIG_DETECTION_BRANCHES = 'detection_branches'
CONFIG_AVAILABLE_TEMPLATES = 'available_templates'
CONFIG_PARAMETERS = 'parameters'
CONFIG_TEMPLATE_PATHS = 'template_paths'
BRANCH_ANCHORS = 'anchors'
BRANCH_SCENARIOS = 'scenarios'
STATE_EXECUTION_STACK = 'execution_stack'
STATE_BRANCH_NAME = 'branch_name'
STATE_INDEX = 'index'
TEMPLATE_NAME = 'class_name'
TEMPLATE_PATH = 'path'
def _scan_for_shared_templates():
    templates = []
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    templates_folder = os.path.join(project_root, 'storageData', 'templates')
    if os.path.isdir(templates_folder):
        for filename in os.listdir(templates_folder):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                templates.append({TEMPLATE_NAME: filename, TEMPLATE_PATH: os.path.join(templates_folder, filename)})
    return templates
_SHARED_TEMPLATES = _scan_for_shared_templates()
DEFAULT_MODE = 'main'
CAPTCHA_PASSER_MODE = 'captcha_passer'
MODE_TASK_CONFIG = {
    DEFAULT_MODE: [
        {
            "id": "tool_text",
            "execution_type": "non_threaded",
            "area" : { "x": 1800, "y": 365, "width": 120, "height": 120 },
            "detectors": [{
                'detector_type': 'text',
                'parameters': {}
            }]
        }
    ],
}
class SimpleClickerTool(BaseTool):
    TOOL_NAME = "simple_clicker"
    def __init__(self, tool_manager, tool_data=None, tool_configuration=None):
        if tool_configuration and CONFIG_DETECTION_BRANCHES not in tool_configuration:
            raise ValueError(f"Configuration must include '{CONFIG_DETECTION_BRANCHES}'")
        if tool_configuration and BRANCH_SCENARIOS in tool_configuration.get(CONFIG_DETECTION_BRANCHES, {}):
            ContextActionExecutor.validate_scenario_tree(tool_configuration[CONFIG_DETECTION_BRANCHES][BRANCH_SCENARIOS])
        super().__init__(tool_manager, tool_data, tool_configuration)
        self.tool_configuration[CONFIG_AVAILABLE_TEMPLATES] = _SHARED_TEMPLATES
        self.execution_stack = []
        self.mode = DEFAULT_MODE
        self.mode_retry_count = 0
    @staticmethod
    def get_default_configuration():
        config = BaseTool.get_default_configuration()
        config.update({
            'base_priority': 5,
            CONFIG_DETECTION_BRANCHES: {},
            CONFIG_AVAILABLE_TEMPLATES: _SHARED_TEMPLATES,
            'sleep_period': 1
        })
        return config
    # ...existing methods from SimpleClicker...
