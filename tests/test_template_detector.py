import pytest
from PIL import Image
import numpy as np
import cv2
import os
from common.impl.detection.TemplateDetector import TemplateDetector

@pytest.fixture(scope='module')
def setup_images():
    template_path = 'tests/images/template_1.png'
    image_path = 'tests/images/screenshot_1.png'
    return template_path, image_path

def test_detect_single_match(setup_images):
    template_path, image_path = setup_images
    settings = {
        'template_paths': [template_path],
        'threshold': 0.95
    }
    detector = TemplateDetector(settings)
    img = Image.open(image_path)
    results = detector.detect(img)
    assert any(r['class_name'] == 'template_1.png' for r in results)

def test_no_match(setup_images):
    template_path, image_path = setup_images
    blank_template_path = 'tests/images/template_3.png'
    settings = {
        'template_paths': [blank_template_path],
        'threshold': 0.95
    }
    detector = TemplateDetector(settings)
    img = Image.open(image_path)
    results = detector.detect(img)
    assert len(results) == 0

def test_multiple_templates(setup_images):
    template_path, image_path = setup_images
    second_template_path = 'tests/images/template_2.png'
    settings = {
        'template_paths': [template_path, second_template_path],
        'threshold': 0.95
    }
    detector = TemplateDetector(settings)
    img = Image.open(image_path)
    results = detector.detect(img)
    assert any(r['class_name'] == 'template_2.png' for r in results)
    assert any(r['class_name'] == 'template_1.png' for r in results)
