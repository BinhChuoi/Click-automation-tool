import pytest
from PIL import Image
import numpy as np
import cv2
import os
from core.main.src.impl.detection.TemplateDetector import TemplateDetector

@pytest.fixture(scope='module')
import os

def setup_images():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    resources_dir = os.path.abspath(os.path.join(base_dir, '..', '..', 'resources'))
    template_path = os.path.join(resources_dir, 'template_1.png')
    image_path = os.path.join(resources_dir, 'screenshot_1.png')
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
    base_dir = os.path.dirname(os.path.abspath(__file__))
    resources_dir = os.path.abspath(os.path.join(base_dir, '..', '..', 'resources'))
    blank_template_path = os.path.join(resources_dir, 'template_3.png')
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
    base_dir = os.path.dirname(os.path.abspath(__file__))
    resources_dir = os.path.abspath(os.path.join(base_dir, '..', '..', 'resources'))
    second_template_path = os.path.join(resources_dir, 'template_2.png')
    settings = {
        'template_paths': [template_path, second_template_path],
        'threshold': 0.95
    }
    detector = TemplateDetector(settings)
    img = Image.open(image_path)
    results = detector.detect(img)
    assert any(r['class_name'] == 'template_2.png' for r in results)
    assert any(r['class_name'] == 'template_1.png' for r in results)
