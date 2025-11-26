import os
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from common.utils.PathResolver import get_project_root

class _BrowserManager:
    """Manages the Selenium WebDriver instance."""
    def __init__(self):
        self.driver = None

    def open_chrome_with_profile(self, profile_name='Profile 7', url='https://sunflower-land.com/play/'):
        # ...existing code...
        pass

    def close_browser(self):
        # ...existing code...
        pass

BrowserManager = _BrowserManager()
