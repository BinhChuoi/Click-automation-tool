
from common.base.threaded_detection import ThreadDetection
from common.base.non_threaded_detection import NonThreadedDetection
from common.impl.template_matching_detector import TemplateMatchingDetector
from common.impl.text_detector import TextDetector
from common.impl.yolo_object_detector import YoloObjectDetector

# --- Detection Class Mapping ---
DETECTOR_CLASSES = {
    "template_matching": TemplateMatchingDetector,
    "text": TextDetector,
    "yolo": YoloObjectDetector
}

EXECUTION_CLASSES = {
    "threaded": ThreadDetection,
    "non_threaded": NonThreadedDetection
}

# --- Adapter for Detection Classes ---
class DetectionTask:
    """
    An adapter that wraps a detection strategy (e.g., template matching, text)
    and its execution model (threaded or non-threaded).
    """

    def set_detection_enabled(self, enabled: bool):
        """
        Sets the detection_enabled_flag property of the underlying execution strategy.
        """
        if hasattr(self.execution_strategy, 'detection_enabled_flag'):
            self.execution_strategy.detection_enabled_flag = enabled
        else:
            raise AttributeError("Underlying execution strategy does not support detection_enabled_flag.")

    def __init__(self, task_id, config, on_detection=None, on_stop=None):
        self.task_id = task_id
        self.config = config
        self.on_detection = on_detection
        self.on_stop = on_stop

        # Support multiple detectors: config['detectors'] is a list of dicts, each with 'type' and 'parameters'
        detectors_config = config.get('detectors')
        self.detectors = {}
        if detectors_config:
            for det_cfg in detectors_config:
                det_type = det_cfg.get('detector_type')
                det_params = det_cfg.get('parameters', {})
                if det_type:
                    self.detectors[det_type] = self._build_detector(det_type, det_params)
        else:
            # Fallback to single detector config for backward compatibility
            det_type = config.get('detector_type')
            det_params = config.get('parameters', {})
            if det_type:
                self.detectors[det_type] = self._build_detector(det_type, det_params)

        execution_type = config.get('execution_type', 'threaded')
        execution_class = EXECUTION_CLASSES.get(execution_type, ThreadDetection)
        # Prepare the arguments for the execution strategy
        strategy_args = {
            'detectors': list(self.detectors.values()),  # Pass a list of detectors
            'working_area': self.config['area'],
            'task_id': self.task_id,
            'on_detection': on_detection,
            'sleep_period': self.config.get('sleep_period', 1)
        }

        # If the execution is threaded, pass the on_detection callback
        if on_detection:
            strategy_args['on_detection'] = on_detection

        # Instantiate the execution strategy with the detectors and other parameters
        self.execution_strategy = execution_class(**strategy_args)

    def start(self):
        """Starts the task by delegating to the strategy."""
        self.execution_strategy.start()

    def get_found_objects(self):
        """Returns the list of found objects from the strategy."""
        return self.execution_strategy.get_found_objects()

    def stop(self):
        """Stops the task by delegating to the strategy and removes itself from the active list."""

        # First, stop the background thread if it's running
        self.execution_strategy.stop()
        self.execution_strategy.join(5) # Wait up to 5 seconds for the thread to finish


        # Finally, call the original on_stop callback if it exists, for any additional cleanup
        if self.on_stop:
            self.on_stop()
    
    def update_detector_params(self, new_params, detector_type):
        """
        Update parameters for the specified detector_type by merging new_params into the current parameters.
        Only updates parameters, not other config fields.
        """
        def merge_dicts(base, update):
            merged = base.copy()
            merged.update(update)
            return merged

        # Only update if detector_type exists
        if detector_type not in self.detectors:
            return
        # Find current config for the detector_type
        current_cfg = next((cfg for cfg in self.config.get('detectors', []) if cfg.get('type') == detector_type), {})
        merged_params = merge_dicts(current_cfg.get('parameters', {}), new_params)
        self.detectors[detector_type] = self._build_detector(detector_type, merged_params)
        # Update execution_strategy detectors list
        self.execution_strategy.detectors = list(self.detectors.values())
    

    def pause(self):
        """Pauses the task by delegating to the strategy."""
        self.execution_strategy.pause()

    def resume(self):
        """Resumes the task by delegating to the strategy."""
        self.execution_strategy.resume()

    def is_paused(self):
        """Returns True if the task is paused, from the strategy."""
        return self.execution_strategy.is_paused()

    def is_alive(self):
        """Returns True if the task is active, from the strategy."""
        return self.execution_strategy.is_alive()

    def trigger_detection(self):
        """Performs a single detection cycle."""
        return self.execution_strategy.trigger_detection()

    @property
    def is_threaded(self):
        """Returns True if the strategy is a threaded one."""
        return isinstance(self.execution_strategy, ThreadDetection)
    
    def _build_detector(self, detector_type, parameters):
        if detector_type not in DETECTOR_CLASSES:
            raise ValueError(f"Unknown detector type: {detector_type}")
        
        detector_class = DETECTOR_CLASSES[detector_type]
        return detector_class(**parameters)
