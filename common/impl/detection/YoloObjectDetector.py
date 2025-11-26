# -*- coding: utf-8 -*-
"""
This module contains the implementation of a detector using a YOLO model.
"""
from common.base.detection.AbstractDetector import AbstractDetector
from inference import get_model
import numpy as np

class YoloObjectDetector(AbstractDetector):
    """
    A detector that uses a YOLO model to find objects in an image.
    """
    def __init__(self, model_id, api_key, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = get_model(model_id=model_id, api_key=api_key)
    def detect(self, image):
        results = self.model.infer(image)
        predictions = [p.dict() for p in results[0].predictions]
        confident_predictions = [p for p in predictions if p.get('confidence', 0) > 0.6]
        sorted_predictions = sorted(confident_predictions, key=lambda p: p.get('confidence', 0), reverse=True)
        top_predictions = sorted_predictions[:3]
        print("Prediction", top_predictions)
        return top_predictions
