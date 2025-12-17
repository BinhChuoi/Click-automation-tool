# -*- coding: utf-8 -*-
"""
This module contains a detector that uses the EAST text detection model from OpenCV.
"""

from core.main.src.base.detection.AbstractDetector import AbstractDetector
import easyocr
from PIL import Image
import os
from core.main.src.utils.Constants import DEFAULT_LANGUAGE, DEFAULT_GPU, DEFAULT_UPSCALE_FACTOR, DEFAULT_NL_MEANS, DEFAULT_NL_H, PROCESSED_IMAGES_DIR

class TextDetector(AbstractDetector):
    """
    A detector that finds text regions in an image using the EAST model.
    This class is stateless.
    """

    def __init__(self, config=None):
        self.config = config or {}
        lang = self.config.get('language', DEFAULT_LANGUAGE)
        gpu = self.config.get('gpu', DEFAULT_GPU)
        self.reader = easyocr.Reader([lang], gpu=gpu)

    def detect(self, image):
        import numpy as np
        import cv2
        import os

        results = []

        if isinstance(image, Image.Image):
            image = np.array(image)

        # Read params from config if not provided
       
        save_processed = self.config.get('save_processed', False)
        processed_path = self.config.get('processed_path', None)
        draw_boxes = self.config.get('draw_boxes', False)
        upscale_factor = self.config.get('upscale_factor', DEFAULT_UPSCALE_FACTOR)
        nl_means = self.config.get('nl_means', DEFAULT_NL_MEANS)
        nl_h = self.config.get('nl_h', DEFAULT_NL_H)
        
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
                os.makedirs(PROCESSED_IMAGES_DIR, exist_ok=True)
                processed_path = os.path.join(PROCESSED_IMAGES_DIR, 'processed.png')
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
