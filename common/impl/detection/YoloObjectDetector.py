# -*- coding: utf-8 -*-
"""
This module contains the implementation of a detector using a YOLO model.
"""

from common.base.detection.AbstractDetector import AbstractDetector
from inference import get_model
import numpy as np
import yaml


class YoloObjectDetector(AbstractDetector):
    """
    A detector that uses a YOLO model to find objects in an image.
    """

    def __init__(self, settings):
        super().__init__()

        settings = settings or {}
        model_id = settings.get('model_id')
        api_key = settings.get('api_key')
        self.confidence_threshold = settings.get('confidence_threshold', 0.6)
        self.max_predictions = settings.get('max_predictions', 3)
        self.model = get_model(model_id=model_id, api_key=api_key)

    def detect(self, image):
        results = self.model.infer(image)
        predictions = [p.dict() for p in results[0].predictions]

        confident_predictions = [p for p in predictions if p.get('confidence', 0) > self.confidence_threshold]
        sorted_predictions = sorted(confident_predictions, key=lambda p: p.get('confidence', 0), reverse=True)
        top_predictions = sorted_predictions[:self.max_predictions]

        print("Prediction", top_predictions)
        return top_predictions
