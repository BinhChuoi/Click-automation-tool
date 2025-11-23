# -*- coding: utf-8 -*-
"""
This module contains the implementation of a detector using a YOLO model.
"""
from common.base.detector_base import BaseDetector
from inference import get_model
import numpy as np


class YoloObjectDetector(BaseDetector):
    """
    A detector that uses a YOLO model to find objects in an image.
    """
    def __init__(self, model_id, api_key, *args, **kwargs):
        """
        Initializes the YOLO object detector.
        """
        super().__init__(*args, **kwargs)
        self.model = get_model(model_id=model_id, api_key=api_key)

    def detect(self, image):
        """
        Performs detection on a given image using the YOLO model.

        Args:
            image: The image (e.g., a numpy array) to perform detection on.

        Returns:
            A list of detections (e.g., bounding boxes, coordinates).
        """
        # The inference library can handle PIL images directly
        results = self.model.infer(image)
        
        predictions = [p.dict() for p in results[0].predictions]
        
        # 1. Filter by confidence > 0.85
        confident_predictions = [p for p in predictions if p.get('confidence', 0) > 0.6]

        # 2. Sort by confidence in descending order
        sorted_predictions = sorted(confident_predictions, key=lambda p: p.get('confidence', 0), reverse=True)
        
        # 3. Limit to a maximum of 3 objects
        top_predictions = sorted_predictions[:3]
        
        print("Prediction", top_predictions)
        return top_predictions
