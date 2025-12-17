# -*- coding: utf-8 -*-
"""
This module contains the implementation of a detector using a YOLO model.
"""

from core.main.src.base.detection.AbstractDetector import AbstractDetector
from inference import get_model

class YoloObjectDetector(AbstractDetector):
    """
    A detector that uses a YOLO model to find objects in an image.
    """

    def __init__(self, config=None):
        super().__init__()

        config = config or {}
        model_id = config.get('model_id')
        api_key = config.get('api_key')

        if not model_id:
            raise ValueError("YOLO model_id is required in config")
        if not api_key:
            raise ValueError("YOLO api_key is required in config")
        
        self.confidence_threshold = config.get('confidence_threshold', 0.6)
        self.max_predictions = config.get('max_predictions', 3)
        self.model = get_model(model_id=model_id, api_key=api_key)

    def detect(self, image):
        results = self.model.infer(image)
        predictions = [p.dict() for p in results[0].predictions]

        confident_predictions = [p for p in predictions if p.get('confidence', 0) > self.confidence_threshold]
        sorted_predictions = sorted(confident_predictions, key=lambda p: p.get('confidence', 0), reverse=True)
        top_predictions = sorted_predictions[:self.max_predictions]

        print("Prediction", top_predictions)
        return top_predictions
