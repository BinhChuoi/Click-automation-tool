# -*- coding: utf-8 -*-
"""
This module contains a detector that uses the EAST text detection model from OpenCV.
"""

from common.base.detection.AbstractDetector import AbstractDetector
import cv2
import numpy as np
import easyocr
from PIL import Image
import os


class TextDetector(AbstractDetector):
    """
    A detector that finds text regions in an image using the EAST model.
    This class is stateless.
    """

    def __init__(self, settings=None):
        self.settings = settings or {}
        lang = self.settings.get('language', 'en')
        gpu = self.settings.get('gpu', False)
        self.reader = easyocr.Reader([lang], gpu=gpu)

    def detect(self, image):
        import numpy as np
        import cv2
        import os

        results = []

        if isinstance(image, Image.Image):
            image = np.array(image)

        # Read params from settings if not provided
       
        save_processed = self.settings.get('save_processed', False)
        processed_path = self.settings.get('processed_path', None)
        draw_boxes = self.settings.get('draw_boxes', False)
        upscale_factor = self.settings.get('upscale_factor', 5)
        nl_means = self.settings.get('nl_means', True)
        nl_h = self.settings.get('nl_h', 15)
        
        # Upscale
        image_upscaled = upscale_image(image, scale_factor=upscale_factor)

        # Grayscale
        image_processed = to_grayscale(image_upscaled)

        # Non-local means denoising
        if nl_means:
            image_processed = apply_nl_means_denoising(image_processed, h=nl_h)

        ocr_results = self.reader.readtext(image_processed)
        boxed_image = cv2.cvtColor(image_processed, cv2.COLOR_GRAY2BGR)

        for (bbox, text, confidence) in ocr_results:
            results.append({
                'x': int((bbox[0][0] + bbox[2][0]) // 2),
                'y': int((bbox[0][1] + bbox[2][1]) // 2),
                'width': int(abs(bbox[2][0] - bbox[0][0])),
                'height': int(abs(bbox[2][1] - bbox[0][1])),
                'confidence': confidence,
                'class_name': text
            })
            if draw_boxes:
                pts = np.array(bbox, np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(boxed_image, [pts], isClosed=True, color=(0, 255, 0), thickness=2)

        if save_processed:
            if processed_path is None:
                os.makedirs('storageData/processed_images', exist_ok=True)
                processed_path = 'storageData/processed_images/processed.png'
            if draw_boxes:
                cv2.imwrite(processed_path, boxed_image)
            else:
                cv2.imwrite(processed_path, image_processed)

        return results


def upscale_image(image, scale_factor=5):
    import cv2
    h, w = image.shape[:2]
    upscaled = cv2.resize(image, (w * scale_factor, h * scale_factor), interpolation=cv2.INTER_NEAREST)
    return upscaled


def to_grayscale(image):
    import cv2
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def apply_median_blur(image, ksize=3):
    import cv2
    return cv2.medianBlur(image, ksize)


def apply_nl_means_denoising(image, h=10):
    import cv2
    return cv2.fastNlMeansDenoising(image, None, h)
