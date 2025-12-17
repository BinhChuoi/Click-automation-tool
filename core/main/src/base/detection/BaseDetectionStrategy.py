from abc import ABC, abstractmethod

class BaseDetectionStrategy(ABC):
    """
    Abstract base class for a detection strategy, defining the common interface
    for different execution modes (e.g., threaded, non-threaded).
    """
    def __init__(self):
        self._detectors = []

    @property
    def detectors(self):
        """Gets the list of detectors."""
        return self._detectors

    @detectors.setter
    def detectors(self, value):
        """Sets the list of detectors."""
        if not isinstance(value, list):
            raise TypeError("detectors must be a list")
        self._detectors = value
        
    @abstractmethod
    def start(self):
        """Starts the detection task."""
        pass

    @abstractmethod
    def stop(self):
        """Stops the detection task."""
        pass

    @abstractmethod
    def pause(self):
        """Pauses the detection task."""
        pass

    @abstractmethod
    def resume(self):
        """Resumes the detection task."""
        pass
