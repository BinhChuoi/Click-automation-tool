import pytest
import numpy as np
import cv2
import os
from unittest.mock import patch, MagicMock
from common.impl.text_detector import TextDetector
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@pytest.fixture
def blank_image():
    return np.zeros((320, 320, 3), dtype=np.uint8)

@patch('os.path.isfile', return_value=False)
def test_model_file_not_found(mock_isfile):
    # No longer relevant, TextDetector does not require a model file
    pass

@patch('os.path.isfile', return_value=True)
@patch('cv2.dnn.readNet')
def test_init_valid_model(mock_readnet, mock_isfile):
    # No longer relevant, TextDetector does not require a model file
    detector = TextDetector()
    assert isinstance(detector, TextDetector)

@patch('cv2.dnn.blobFromImage', return_value='blob')
def test_detect_blank_image(mock_blob, blank_image):
    detector = TextDetector()
    results = detector.detect(blank_image)
    assert isinstance(results, list)
    assert results == []

def test_detect_returns_expected_format(blank_image):
    detector = TextDetector()
    # Create a white image with some text
    cv2.putText(blank_image, 'Hello', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 3)
    results = detector.detect(blank_image)
    if results:
        r = results[0]
        assert 'x' in r
        assert 'y' in r
        assert 'width' in r
        assert 'height' in r
        assert 'confidence' in r
        assert isinstance(r['class_name'], str)

def test_detect_on_sample_image():
    detector = TextDetector()
    SAMPLE_IMAGE_PATH = os.path.join(os.path.dirname(__file__), 'images', 'sample_1.png')
    image = cv2.imread(SAMPLE_IMAGE_PATH)
    assert image is not None, 'Failed to load sample_1.png'
    results = detector.detect(image)
    assert isinstance(results, list)
    
    assert 'class_name' in results[0]
    assert isinstance(results[0]['class_name'], str)
    assert int(results[0]['class_name']) == 118

def test_detect_on_sample_image_2():
    detector = TextDetector()
    SAMPLE_IMAGE_PATH = os.path.join(os.path.dirname(__file__), 'images', 'sample_6.png')
    image = cv2.imread(SAMPLE_IMAGE_PATH)
    assert image is not None, 'Failed to load sample_6.png'
    results = detector.detect(image)
    assert isinstance(results, list)
  
    assert 'class_name' in results[0]
    assert isinstance(results[0]['class_name'], str)
    assert int(results[0]['class_name']) == 3
