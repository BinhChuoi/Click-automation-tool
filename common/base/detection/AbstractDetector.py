# -*- coding: utf-8 -*-
"""
Abstract base class for all detection model implementations.
"""
from abc import ABC, abstractmethod

class AbstractDetector(ABC):
    """
    Abstract base class for a detector. A detector's role is to find
    things in a single image and return their locations. It holds no state
    about the application, screen, or threads.
    """
    @abstractmethod
    def __init__(self, *args, **kwargs):
        """
        Initializes the detector, e.g., by loading a model or templates.
        """
        pass

    @abstractmethod
    def detect(self, image):
        """
        Performs detection on a given image.

        Args:
            image: The image (e.g., a numpy array) to perform detection on.

        Returns:
            A list of detections (e.g., bounding boxes, coordinates).
        """
        pass
