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
        """
        Opens a Chrome browser with a specific user profile and navigates to a URL.

        Args:
            profile_name (str): The name of the Chrome profile to use.
            url (str): The URL to navigate to.
        """
        if self.driver is not None:
            print("Browser is already open.")
            return self.driver

        try:
            print(f"Attempting to open Chrome with profile: {profile_name}")

            # Correctly construct the path to the user data directory and the specific profile
            project_root = get_project_root()
            user_data_dir = os.path.join(project_root, 'chromeProfiles') # This is the parent
            profile_dir = profile_name # This is the specific profile to use

            print(f"Using user-data-dir: {user_data_dir}")
            print(f"Using profile-directory: {profile_name}")

            # Set up Chrome options
            chrome_options = Options()
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Disable the translation pop-up
            prefs = {
                "translate_prompt_enabled": False,
                "translate.enabled": False,
            }
            chrome_options.add_experimental_option("prefs", prefs)

            chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
            chrome_options.add_argument(f"--profile-directory={profile_dir}")
            
            # Disable the "Translate to English" popup
            chrome_options.add_experimental_option('prefs', {'translate_whitelists': {'your_language_code': 'en'}, 'translate': {'enabled': 'False'}})

            # Initialize the WebDriver service, hiding the console window on Windows
            service = ChromeService()
            if os.name == 'nt': # 'nt' is the name for Windows
                service.creationflags = subprocess.CREATE_NO_WINDOW
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            print(f"Navigating to: {url}")
            self.driver.get(url)
            
            return self.driver

        except Exception as e:
            print(f"An error occurred while trying to open Chrome: {e}")
            print("Please ensure you have Google Chrome and the correct chromedriver installed.")
            if self.driver:
                self.driver.quit()
            self.driver = None
            return None

    def close_browser(self):
        """Closes the browser and quits the WebDriver."""
        if self.driver:
            print("Closing browser...")
            self.driver.quit()
            self.driver = None

BrowserManager = _BrowserManager()
