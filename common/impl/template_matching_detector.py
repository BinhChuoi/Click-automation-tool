# -*- coding: utf-8 -*-
"""
This module contains a detector that uses classic template matching.
"""
from ..base.detector_base import BaseDetector
import cv2
import os
import numpy as np

class TemplateMatchingDetector(BaseDetector):
    """
    A detector that finds objects in an image using one or more templates.
    This class is stateless.
    """
    def __init__(self, template_paths, threshold=0.9):
        """
        Initializes the detector by loading one or more template images.

        Args:
            template_paths (list): A list of paths to the template images.
            threshold (float): The matching threshold.
        """
        if not template_paths or not isinstance(template_paths, list):
            print("Error: Missing or invalid 'template_paths' list for TemplateMatchingDetector")

        self.threshold = threshold
        self.templates = []
        for path in template_paths:
            template = cv2.imread(path, cv2.IMREAD_COLOR)
            if template is None:
                print(f"Error: Could not read template image at {path}")
                continue
            class_name = os.path.basename(path)
            self.templates.append({'image': template, 'class': class_name})

    def detect(self, image):
        """
        Performs template matching on the given image for all loaded templates.

        Args:
            image: The image (numpy array) to search within.

        Returns:
            A list of refined bounding boxes for all detected objects.
        """
        img_bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        all_matches = []
        for template_info in self.templates:
            template_image = template_info['image']
            class_name = template_info['class']
            
            matches = self._find_all_template_matches(img_bgr, template_image, self.threshold)
            
            for box in matches:
                all_matches.append({
                    'x': box[0] + box[2] / 2,
                    'y': box[1] + box[3] / 2,
                    'width': box[2],
                    'height': box[3],
                    'confidence': 1.0,
                    'class_name': class_name
                })
        
        return self._apply_nms(all_matches)

    def _find_all_template_matches(self, img, template, threshold):
        """Finds all occurrences of a template image within a main image."""
        if img is None or template is None:
            return []
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        h, w = template_gray.shape
        result = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)
        bounding_boxes = []
        for pt in zip(*loc[::-1]):
            bounding_boxes.append((int(pt[0]), int(pt[1]), w, h))
        return bounding_boxes

    def _apply_nms(self, boxes, confidence_threshold=0.5, nms_threshold=0.4):
        """Applies Non-Maximum Suppression to a list of bounding boxes."""
        if not boxes:
            return []

        # The output of YOLO is center x, center y, width, height.
        # The NMSBoxes function expects (x, y, w, h) where x,y is top-left.
        # The template matching is already returning top-left x,y.
        # The new format is center x,y, so we need to convert back.
        
        rects = []
        for box in boxes:
            rects.append([
                int(box['x'] - box['width'] / 2),
                int(box['y'] - box['height'] / 2),
                int(box['width']),
                int(box['height'])
            ])

        confidences = [box['confidence'] for box in boxes]
        
        indices = cv2.dnn.NMSBoxes(rects, confidences, confidence_threshold, nms_threshold)
        
        refined_boxes = []
        if len(indices) > 0:
            indices = indices.flatten().tolist()
            refined_boxes = [boxes[i] for i in indices]
            
        return refined_boxes
