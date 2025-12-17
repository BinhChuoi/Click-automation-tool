import pytest
import numpy as np
import cv2
import os
from core.main.src.impl.detection.TextDetector import TextDetector

IMAGE_TESTS = [
    ("sample_1.png", "118"),
    ("sample_2.png", "84"),
    ("sample_3.png", "84"),
    ("sample_4.png", "Expand"),
    ("sample_5.png", "3222"),
    ("sample_6.png", "3"),
    ("sample_7.png", "74.77"),
    ("sample_8.png", "18.6145"),
    ("sample_9.png", "50"),
    ("sample_10.png", "15"),
    ("sample_11.png", "UPGRADE"),
    ("sample_12.png", "PETE"),
    ("sample_13.png", "PEGGY"),
    ("sample_14.png", "71,652,466.431")
]

@pytest.mark.parametrize("filename,expected_class", IMAGE_TESTS)
def test_text_detector_on_image(filename, expected_class):
    settings = {
        'languages': ['en'],
        'gpu': False,
        'save_processed' : False,
        'draw_boxes' : False,
        'upscale_factor' : 5,
        'nl_means' : True,    
        'nl_h' : 15
    }
    detector = TextDetector(settings)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    resources_dir = os.path.abspath(os.path.join(base_dir, '..', 'resources'))
    image_path = os.path.join(resources_dir, filename)
    image = cv2.imread(image_path)
    assert image is not None, f"Failed to load {filename} or alternate case variant. Looked in {resources_dir}"
    results = detector.detect(image)
    assert isinstance(results, list)
    if expected_class is not None:
        assert 'class_name' in results[0]
        assert isinstance(results[0]['class_name'], str)
        assert results[0]['class_name'].strip().lower() == expected_class.strip().lower()
    else:
        # Just check that results are present and formatted
        if results:
            r = results[0]
            assert 'x' in r
            assert 'y' in r
            assert 'width' in r
            assert 'height' in r
            assert 'confidence' in r
            assert isinstance(r['class_name'], str)
