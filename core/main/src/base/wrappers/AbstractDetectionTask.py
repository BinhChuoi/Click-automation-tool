from abc import ABC, abstractmethod
from typing import Any

class AbstractDetectionTask(ABC):
    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def get_found_objects(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def update_detector_configuration(self, new_configuration: dict, detector_type: str):
        pass

    @abstractmethod
    def pause(self):
        pass

    @abstractmethod
    def resume(self):
        pass

    @abstractmethod
    def is_paused(self) -> bool:
        pass

    @abstractmethod
    def is_alive(self) -> bool:
        pass

    @abstractmethod
    def trigger_detection(self):
        pass

    @property
    @abstractmethod
    def is_threaded(self) -> bool:
        pass
