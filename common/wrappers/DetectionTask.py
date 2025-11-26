from common.impl.detection.ThreadedStrategy import ThreadedStrategy
from common.impl.detection.NonThreadedStrategy import NonThreadedStrategy
from common.impl.detection.TemplateDetector import TemplateDetector
from common.impl.detection.TextDetector import TextDetector
from common.impl.detection.YoloObjectDetector import YoloObjectDetector

# --- Detection Class Mapping ---
DETECTOR_CLASSES = {
    "template": TemplateDetector,
    "text": TextDetector,
    "yolo": YoloObjectDetector
}

EXECUTION_CLASSES = {
    "threaded": ThreadedStrategy,
    "non_threaded": NonThreadedStrategy
}

# --- Adapter for Detection Classes ---
class DetectionTask:
    """
    An adapter that wraps a detection strategy (e.g., template matching, text)
    and its execution model (threaded or non-threaded).
    """
    # ...existing code...
    def set_detection_enabled(self, enabled: bool):
        # ...existing code...
        if hasattr(self.execution_strategy, 'detection_enabled_flag'):
            self.execution_strategy.detection_enabled_flag = enabled
        else:
            raise AttributeError("Underlying execution strategy does not support detection_enabled_flag.")

    def __init__(self, task_id, config, on_detection=None, on_stop=None):
        # ...existing code...
        self.task_id = task_id
        self.config = config
        self.on_detection = on_detection
        self.on_stop = on_stop
        # ...existing code...
        detectors_config = config.get('detectors')
        self.detectors = {}
        if detectors_config:
            for det_cfg in detectors_config:
                det_type = det_cfg.get('detector_type')
                det_params = det_cfg.get('parameters', {})
                if det_type:
                    self.detectors[det_type] = self._build_detector(det_type, det_params)
        else:
            det_type = config.get('detector_type')
            det_params = config.get('parameters', {})
            if det_type:
                self.detectors[det_type] = self._build_detector(det_type, det_params)
        execution_type = config.get('execution_type', 'threaded')
        execution_class = EXECUTION_CLASSES.get(execution_type, ThreadDetection)
        strategy_args = {
            'detectors': list(self.detectors.values()),
            'working_area': self.config['area'],
            'task_id': self.task_id,
            'on_detection': on_detection,
            'sleep_period': self.config.get('sleep_period', 1)
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
    def update_detector_params(self, new_params, detector_type):
        def merge_dicts(base, update):
            merged = base.copy()
            merged.update(update)
            return merged
        if detector_type not in self.detectors:
            return
        current_cfg = next((cfg for cfg in self.config.get('detectors', []) if cfg.get('type') == detector_type), {})
        merged_params = merge_dicts(current_cfg.get('parameters', {}), new_params)
        self.detectors[detector_type] = self._build_detector(detector_type, merged_params)
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
        return isinstance(self.execution_strategy, ThreadDetection)
    def _build_detector(self, detector_type, parameters):
        if detector_type not in DETECTOR_CLASSES:
            raise ValueError(f"Unknown detector type: {detector_type}")
        detector_class = DETECTOR_CLASSES[detector_type]
        return detector_class(**parameters)
