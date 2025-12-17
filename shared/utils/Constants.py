# Constants for Sunflowerland-automation

# File and directory names
SETTINGS_FILE = "setting.yaml"
TOOLS_STORAGE_DIR = "storageData/tools"
PROCESSED_IMAGES_DIR = "storageData/processed_images"
CHROME_PROFILES_DIR = "chromeProfiles"
SCREENSHOTS_DIR = "screenshots"
TEMP_DIR = "temp"

# Overlay and UI
OVERLAY_TRANSPARENT_COLOR = "magenta"
OVERLAY_TITLE = "Bound Hotkeys"

# Default values
DEFAULT_LANGUAGE = "en"
DEFAULT_GPU = False
DEFAULT_UPSCALE_FACTOR = 5
DEFAULT_NL_MEANS = True
DEFAULT_NL_H = 15

# Hotkey actions
HOTKEY_PAUSE = "p"
HOTKEY_RESET = "r"
HOTKEY_STOP = "esc"
HOTKEY_EXCEPTION_REGION = "e"
HOTKEY_CONFIRM = "q"

# Detector types
DETECTOR_TYPE_TEMPLATE = "template"
DETECTOR_TYPE_TEXT = "text"
DETECTOR_TYPE_YOLO = "yolo"

# Execution strategy types
EXECUTION_STRATEGY_THREADED = "threaded"
EXECUTION_STRATEGY_NON_THREADED = "non_threaded"

# Misc
IDLE_TIMEOUT = 60  # seconds

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
