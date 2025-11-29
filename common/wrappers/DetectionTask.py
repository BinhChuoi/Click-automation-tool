from common.impl.detection.ThreadedStrategy import ThreadedStrategy
from common.impl.detection.NonThreadedStrategy import NonThreadedStrategy
from common.impl.detection.TemplateDetector import TemplateDetector
from common.impl.detection.TextDetector import TextDetector
from common.impl.detection.YoloObjectDetector import YoloObjectDetector
from common.utils.Settings import load_settings

# Settings are now loaded and merged in ToolManager
DEFAULT_SETTINGS = load_settings()

# --- Detection Class Mapping ---
DETECTOR_CLASSES = {
    "template": TemplateDetector,
    "text": TextDetector,
    "yolo": YoloObjectDetector,
}

EXECUTION_CLASSES = {
    "threaded": ThreadedStrategy,
    "non_threaded": NonThreadedStrategy,
}


class DetectionTask:
    """
    Adapter that wraps a detection strategy (e.g., template matching, text)
    and its execution model (threaded or non-threaded).
    """

    def set_detection_enabled(self, enabled: bool):
        if hasattr(self.execution_strategy, 'detection_enabled_flag'):
            self.execution_strategy.detection_enabled_flag = enabled
        else:
            raise AttributeError("Underlying execution strategy does not support detection_enabled_flag.")

    def __init__(self, task_id, config, on_detection=None, on_stop=None):
        self.task_id = task_id
        self.config = config
        self.on_detection = on_detection
        self.on_stop = on_stop

        detectors_config = config.get('detector_configs')
        self.detectors = {}

        if detectors_config:
            for det_cfg in detectors_config:
                det_type = det_cfg.get('detector_type')
                det_settings = det_cfg.get('settings', {})

                # Extract default settings for this detector type from setting.yaml structure
                default_det_settings = DEFAULT_SETTINGS.get(det_type, {}) if DEFAULT_SETTINGS else {}
                merged_settings = {**default_det_settings, **det_settings}
                if det_type:
                    self.detectors[det_type] = self._build_detector(det_type, merged_settings)
        else:
            det_type = config.get('detector_type')
            det_settings = config.get('settings', {})
            default_det_settings = DEFAULT_SETTINGS.get(det_type, {}) if DEFAULT_SETTINGS else {}
            merged_settings = {**default_det_settings, **det_settings}
            if det_type:
                self.detectors[det_type] = self._build_detector(det_type, merged_settings)

        execution_type = config.get('execution_type', 'threaded')
        execution_class = EXECUTION_CLASSES.get(execution_type, ThreadedStrategy)
        strategy_args = {
            'detectors': list(self.detectors.values()),
            'working_area': self.config['area'],
            'task_id': self.task_id,
            'on_detection': on_detection,
            'sleep_period': self.config.get('sleep_period', 1),
        }
        if on_detection:
            strategy_args['on_detection'] = on_detection
        self.execution_strategy = execution_class(**strategy_args)

    def start(self):
        self.execution_strategy.start()

    def get_found_objects(self):
        return self.execution_strategy.get_found_objects()

    def stop(self):
        self.execution_strategy.stop()
        self.execution_strategy.join(5)
        if self.on_stop:
            self.on_stop()

    def update_detector_setting(self, new_settings, detector_type):
        def merge_dicts(base, update):
            merged = base.copy()
            merged.update(update)
            return merged
        if detector_type not in self.detectors:
            return
        current_cfg = next((cfg for cfg in self.config.get('detector_configs', []) if cfg.get('type') == detector_type), {})
        merged_settings = merge_dicts(current_cfg.get('settings', {}), new_settings)
        self.detectors[detector_type] = self._build_detector(detector_type, merged_settings)
        self.execution_strategy.detectors = list(self.detectors.values())

    def pause(self):
        self.execution_strategy.pause()

    def resume(self):
        self.execution_strategy.resume()

    def is_paused(self):
        return self.execution_strategy.is_paused()

    def is_alive(self):
        return self.execution_strategy.is_alive()

    def trigger_detection(self):
        return self.execution_strategy.trigger_detection()

    @property
    def is_threaded(self):
        return isinstance(self.execution_strategy, ThreadedStrategy)

    def _build_detector(self, detector_type, settings):
        if detector_type not in DETECTOR_CLASSES:
            raise ValueError(f"Unknown detector type: {detector_type}")
        detector_class = DETECTOR_CLASSES[detector_type]
        # Always pass settings to all detectors
        return detector_class(settings=settings)
