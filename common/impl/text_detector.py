# -*- coding: utf-8 -*-
"""
This module contains a detector that uses the EAST text detection model from OpenCV.
"""
from ..base.detector_base import BaseDetector
import cv2
import numpy as np
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
import easyocr
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image

class TextDetector(BaseDetector):
    """
    A detector that finds text regions in an image using the EAST model.
    This class is stateless.
    """
    def __init__(self):
        """
        Initializes the detector. Loads EasyOCR reader.
        """
        self.reader = easyocr.Reader(['en'], gpu=False)

    def detect(self, image):
        """
        Detects and extracts text from the given image using EasyOCR, with upscaling for improved pixel-art digit recognition.
        Args:
            image: The image (numpy array or PIL Image) to search within.
        Returns:
            A list of dicts with extracted text.
        """
        import numpy as np
        import cv2
        results = []
        # Convert PIL Image to numpy array if needed
        if isinstance(image, Image.Image):
            image = np.array(image)
        # Upscale the image before OCR
        image_upscaled = upscale_image(image, scale_factor=5)
        # Use the upscaled image for OCR
        ocr_results = self.reader.readtext(image_upscaled)
        for (bbox, text, confidence) in ocr_results:
            results.append({
                'x': int((bbox[0][0] + bbox[2][0]) // 2),
                'y': int((bbox[0][1] + bbox[2][1]) // 2),
                'width': int(abs(bbox[2][0] - bbox[0][0])),
                'height': int(abs(bbox[2][1] - bbox[0][1])),
                'confidence': confidence,
                'class_name': text
            })
        return results

def preprocess_digit_image(image, upscale_factor=3):
    
    # Upscale the image
    h, w = image.shape[:2]
    image_up = cv2.resize(image, (w * upscale_factor, h * upscale_factor), interpolation=cv2.INTER_NEAREST)

    # Sharpen the image
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    image_sharp = cv2.filter2D(image_up, -1, kernel)

    # Convert to grayscale
    gray = cv2.cvtColor(image_sharp, cv2.COLOR_BGR2GRAY)

    # Contrast enhancement (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)

    # Adaptive thresholding
    thresh = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)

    # Optional: Morphological operations to clean up
    kernel_morph = np.ones((2,2), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel_morph)

    return cleaned

def upscale_image(image, scale_factor=5):
    """
    Upscales the input image by the given scale factor using nearest-neighbor interpolation.
    Args:
        image: numpy array (BGR or grayscale)
        scale_factor: int, how much to upscale
    Returns:
        Upscaled image as numpy array
    """
    import cv2
    h, w = image.shape[:2]
    upscaled = cv2.resize(image, (w * scale_factor, h * scale_factor), interpolation=cv2.INTER_NEAREST)
    return upscaled