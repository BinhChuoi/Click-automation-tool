
# File and directory names
PROCESSED_IMAGES_DIR = "storageData/processed_images"

# Default values
DEFAULT_LANGUAGE = "en"
DEFAULT_GPU = False
DEFAULT_UPSCALE_FACTOR = 5
DEFAULT_NL_MEANS = True
DEFAULT_NL_H = 15

# Detector types
DETECTOR_TYPE_TEMPLATE = "template"
DETECTOR_TYPE_TEXT = "text"
DETECTOR_TYPE_YOLO = "yolo"

# Execution strategy types
EXECUTION_STRATEGY_THREADED = "threaded"
EXECUTION_STRATEGY_NON_THREADED = "non_threaded"

# Configuration Keys
CONFIG_DETECTION_BRANCHES = 'detection_branches'
CONFIG_AVAILABLE_TEMPLATES = 'available_templates'
CONFIG_TEMPLATE_PATHS = 'template_paths'

# Branch Keys
BRANCH_ANCHORS = 'anchors'  # List of anchor point template names
BRANCH_SCENARIOS = 'scenarios'  # List of scenario dicts: {condition, branch}

# Template Keys
TEMPLATE_NAME = 'class_name'
TEMPLATE_PATH = 'path'
