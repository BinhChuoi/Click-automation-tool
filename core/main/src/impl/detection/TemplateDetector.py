
# -*- coding: utf-8 -*-
"""
This module contains a detector that uses classic template matching.
"""

from core.main.src.base.detection.AbstractDetector import AbstractDetector
import cv2
import os
import numpy as np

# _SHARED_TEMPLATES will be initialized after TemplateDetector is defined

class TemplateDetector(AbstractDetector):
    """
    A detector that finds objects in an image using one or more templates.
    This class is stateless.
    """

    def __init__(self, config=None):
        config = config or {}
        template_names = config.get('template_names', [])
        threshold = config.get('threshold', 0.9)
        self.threshold = threshold
        self.templates = []

        template_paths = []
        for name in template_names:
            template_info = self.get_template_by_name(_SHARED_TEMPLATES, name)
            if template_info:
                template_paths.append(template_info['path'])

        for path in template_paths:
            template = cv2.imread(path, cv2.IMREAD_COLOR)
            if template is None:
                print(f"Error: Could not read template image at {path}")
                continue
            class_name = os.path.basename(path)
            self.templates.append({'image': template, 'class': class_name})

    @staticmethod
    def scan_for_templates():
        """
        Scans the 'simple_clicker_templates' directory for image files using module path resolution.
        Returns a list of template dicts with name and path.
        """
        import shared.resources.templates
        import os
        from core.main.src.utils.Constants import TEMPLATE_NAME, TEMPLATE_PATH
        templates = []
        templates_folder = shared.resources.templates.__path__[0]
        if os.path.isdir(templates_folder):
            for filename in os.listdir(templates_folder):
                if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                    templates.append({TEMPLATE_NAME: filename, TEMPLATE_PATH: os.path.join(templates_folder, filename)})
        return templates

    @staticmethod
    def get_template_by_name(templates, template_name):
        """Finds a template's full data from its name in a list of templates."""
        from core.main.src.utils.Constants import TEMPLATE_NAME
        for t in templates:
            if t[TEMPLATE_NAME] == template_name:
                return t
        return None

    def detect(self, image):
        img_bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        all_matches = []

        for template_info in self.templates:
            template_image = template_info['image']
            class_name = template_info['class']
            matches, scores = self._find_all_template_matches(img_bgr, template_image, self.threshold, return_scores=True)
            for box, score in zip(matches, scores):
                all_matches.append({
                    'x': box[0] + box[2] / 2,
                    'y': box[1] + box[3] / 2,
                    'width': box[2],
                    'height': box[3],
                    'confidence': float(score),
                    'class_name': class_name
                })

        return self._apply_nms(all_matches)

    def _find_all_template_matches(self, img, template, threshold, return_scores=False):
        if img is None or template is None:
            return [] if not return_scores else ([], [])

        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        h, w = template_gray.shape
        result = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)
        bounding_boxes = []
        scores = []
        for pt in zip(*loc[::-1]):
            bounding_boxes.append((int(pt[0]), int(pt[1]), w, h))
            scores.append(result[pt[1], pt[0]])

        if return_scores:
            return bounding_boxes, scores
        return bounding_boxes

    def _apply_nms(self, boxes, confidence_threshold=0.5, nms_threshold=0.4):
        if not boxes:
            return []

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
        
        
# Initialize _SHARED_TEMPLATES after TemplateDetector is defined
_SHARED_TEMPLATES = TemplateDetector.scan_for_templates()
