from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller
import os
import json
import logging
import time
from urllib.parse import unquote
from selenium.webdriver.common.keys import Keys

class WellfoundAutomation:
    def __init__(self, headless=True):
        self.setup_logging()
        self.setup_driver(headless)

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def setup_driver(self, headless):
        try:
            # Install ChromeDriver
            chromedriver_autoinstaller.install()
            
            # Set up Chrome options
            chrome_options = Options()
            if headless:
                chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-infobars')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--ignore-certificate-errors')
            
            # Add additional preferences
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_experimental_option('prefs', {
                'profile.default_content_setting_values.cookies': 1,
                'profile.block_third_party_cookies': False,
                'profile.cookie_controls_mode': 0
            })
            
            # Create Chrome driver
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Set window size
            self.driver.set_window_size(1920, 1080)
            
            # Set longer wait time for elements
            self.wait = WebDriverWait(self.driver, 15)
            
            # Execute CDP commands to modify navigator.webdriver flag
            self.driver.execute_cdp_cmd('Network.enable', {})
            self.driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}})
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                """
            })
            
            self.logger.info("Chrome driver created successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to create Chrome driver: {str(e)}")
            raise

    def parse_cookie_string(self, cookie_string):
        try:
            # URL decode the cookie string
            cookie_string = unquote(cookie_string)
            
            # Split the cookie string into individual cookies
            cookie_pairs = cookie_string.split('&')
            cookies = []
            
            for pair in cookie_pairs:
                if '=' in pair:
                    name, value = pair.split('=', 1)
                    cookie = {
                        'name': name,
                        'value': value,
                        'domain': '.wellfound.com',
                        'path': '/',
                        'secure': True,
                        'httpOnly': True
                    }
                    cookies.append(cookie)
            
            # Save cookies to file
            with open('cookies.json', 'w') as f:
                json.dump(cookies, f)
            self.logger.info(f"Parsed and saved {len(cookies)} cookies")
            return True
            
        except Exception as e:
            self.logger.error(f"Error parsing cookies: {str(e)}")
            return False

    def setup_with_cookies(self, cookie_string):
        if not cookie_string:
            self.logger.error("No cookie string provided")
            return False
            
        if self.parse_cookie_string(cookie_string):
            return self.load_cookies()
        return False

    def load_cookies(self):
        try:
            if not os.path.exists('cookies.json'):
                self.logger.error("Cookie file not found")
                return False
                
            # First navigate to the domain
            self.driver.get('https://wellfound.com')
            time.sleep(2)  # Wait for page to load
            
            # Load and add cookies
            with open('cookies.json', 'r') as f:
                cookies = json.load(f)
            
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    self.logger.error(f"Error adding cookie {cookie['name']}: {str(e)}")
                    continue
            
            # Verify login status
            self.driver.get('https://wellfound.com')
            time.sleep(3)  # Wait for page to load
            
            # Check if we're logged in by looking for specific elements
            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='user-menu']")))
                self.logger.info("Successfully logged in with cookies")
                return True
            except TimeoutException:
                self.logger.error("Failed to verify login status after adding cookies")
                return False
                
        except Exception as e:
            self.logger.error(f"Error loading cookies: {str(e)}")
            return False

    def save_cookies(self):
        try:
            cookies = self.driver.get_cookies()
            with open('cookies.json', 'w') as f:
                json.dump(cookies, f)
            self.logger.info(f"Saved {len(cookies)} cookies to file")
        except Exception as e:
            self.logger.error(f"Error saving cookies: {str(e)}")

    def login(self, email, password):
        try:
            self.logger.info("Attempting to login")
            self.driver.get('https://wellfound.com/login')
            time.sleep(2)  # Wait for initial page load
            
            # Wait for email input and enter email
            email_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            email_input.send_keys(email)
            self.logger.info("Email entered")

            # Find and click continue button
            continue_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )
            continue_button.click()
            self.logger.info("Clicked continue")
            time.sleep(2)  # Wait for password field

            # Wait for password input and enter password
            password_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            password_input.send_keys(password)
            self.logger.info("Password entered")

            # Click login button
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )
            login_button.click()
            self.logger.info("Clicked login")

            # Wait for login to complete and verify
            time.sleep(5)
            try:
                self.driver.find_element(By.CSS_SELECTOR, "[data-test='nav-profile-dropdown']")
                self.logger.info("Login successful")
                self.save_cookies()
                return True
            except:
                self.logger.error("Could not verify login success")
                return False

        except Exception as e:
            self.logger.error(f"Login failed: {str(e)}")
            return False

    def setup_with_browser_cookies(self, cookies):
        """Set up the browser with cookies from an active browser session"""
        try:
            # First navigate to the domain
            self.driver.get('https://wellfound.com')
            time.sleep(2)  # Wait for page to load
            
            # Add each cookie to the browser
            for cookie in cookies:
                try:
                    # Clean the cookie data to only include required fields
                    clean_cookie = {
                        'name': cookie.get('name'),
                        'value': cookie.get('value'),
                        'domain': cookie.get('domain', '.wellfound.com'),
                        'path': cookie.get('path', '/'),
                    }
                    # Only add optional fields if they exist
                    if 'expiry' in cookie:
                        clean_cookie['expiry'] = cookie['expiry']
                    if 'secure' in cookie:
                        clean_cookie['secure'] = cookie['secure']
                    if 'httpOnly' in cookie:
                        clean_cookie['httpOnly'] = cookie['httpOnly']
                        
                    self.driver.add_cookie(clean_cookie)
                    self.logger.info(f"Added cookie: {clean_cookie['name']}")
                except Exception as e:
                    self.logger.error(f"Error adding cookie {cookie.get('name')}: {str(e)}")
                    continue
            
            # Verify login status
            self.driver.get('https://wellfound.com')
            time.sleep(3)  # Wait for page to load
            
            # Check if we're logged in
            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='user-menu']")))
                self.logger.info("Successfully logged in with browser cookies")
                return True
            except TimeoutException:
                self.logger.error("Failed to verify login status after adding browser cookies")
                return False
                
        except Exception as e:
            self.logger.error(f"Error setting up browser cookies: {str(e)}")
            return False

    def setup_with_specific_cookies(self):
        """Set up the browser with specific Wellfound cookies"""
        try:
            # First navigate to the domain to ensure cookies can be set
            self.driver.get('https://wellfound.com')
            time.sleep(2)  # Wait for page load
            
            # Define the specific cookies
            cookies = [
                {
                    'name': 'CF_VERIFIED_DEVICE_ea160c806c7098c731795de2b4d94509e3227fbd1751c6c160a6b11fdfd7bfb7',
                    'value': '1733516879',
                    'domain': 'wellfound.com',
                    'path': '/',
                    'secure': True,
                    'httpOnly': True
                },
                {
                    'name': 'OptanonConsent',
                    'value': 'isGpcEnabled=0&datestamp=Sat+Dec+07+2024+01%3A59%3A37+GMT%2B0530+(India+Standard+Time)&version=202407.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=b3e7953a-a59a-47f4-8239-80e107f4d4fe&interactionCount=0&isAnonUser=1&landingPath=https%3A%2F%2Fdevelopers.cloudflare.com%2Fpages%2Fconfiguration%2Fbranch-build-controls%2F&groups=C0001%3A1%2CC0003%3A1%2CC0002%3A1%2CC0004%3A1',
                    'domain': 'wellfound.com',
                    'path': '/',
                    'secure': True
                }
            ]
            
            # Delete all existing cookies first
            self.driver.delete_all_cookies()
            self.logger.info("Cleared existing cookies")
            
            # Add each cookie to the browser
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                    self.logger.info(f"Added cookie: {cookie['name']}")
                except Exception as e:
                    self.logger.error(f"Error adding cookie {cookie['name']}: {str(e)}")
                    return False
            
            # Refresh the page to apply cookies
            self.driver.refresh()
            time.sleep(3)
            
            # Verify login status
            try:
                # Try to access a protected page
                self.driver.get('https://wellfound.com/inbox')
                time.sleep(3)
                
                # Check if we're still on the login page
                if 'login' in self.driver.current_url.lower():
                    self.logger.error("Still on login page after adding cookies")
                    # Save screenshot for debugging
                    self.driver.save_screenshot("login_redirect_screenshot.png")
                    return False
                
                # Additional verification
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='user-menu'], .user-menu-toggle, .dropdown-toggle")))
                self.logger.info("Successfully logged in with specific cookies")
                return True
                
            except TimeoutException:
                self.logger.error("Failed to verify login status after adding cookies")
                # Save screenshot for debugging
                self.driver.save_screenshot("login_failed_screenshot.png")
                return False
                
        except Exception as e:
            self.logger.error(f"Error setting up specific cookies: {str(e)}")
            # Save screenshot for debugging
            try:
                self.driver.save_screenshot("cookie_error_screenshot.png")
            except:
                pass
            return False

    def send_message(self, recipient_url, message):
        """Send a message to a recipient"""
        try:
            # Navigate to the recipient's profile
            self.driver.get(recipient_url)
            time.sleep(3)  # Wait for page load
            
            # Find and click the message button (try different selectors)
            message_button = None
            for selector in [
                "[data-test='message-button']",
                "button:contains('Message')",
                ".message-button",
                "//button[contains(text(), 'Message')]"
            ]:
                try:
                    if selector.startswith("//"):
                        message_button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        message_button = self.wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    break
                except:
                    continue
            
            if not message_button:
                raise Exception("Could not find message button")
                
            message_button.click()
            time.sleep(2)
            
            # Find the message input (try different selectors)
            message_input = None
            for selector in [
                "[data-test='messaging-composer'] textarea",
                ".message-input",
                "textarea[placeholder*='message']",
                "//textarea[contains(@placeholder, 'message')]"
            ]:
                try:
                    if selector.startswith("//"):
                        message_input = self.wait.until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                    else:
                        message_input = self.wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                    break
                except:
                    continue
            
            if not message_input:
                raise Exception("Could not find message input")
                
            message_input.clear()
            message_input.send_keys(message)
            time.sleep(1)
            
            # Find and click the send button (try different selectors)
            send_button = None
            for selector in [
                "[data-test='send-message-button']",
                "button:contains('Send')",
                ".send-button",
                "//button[contains(text(), 'Send')]"
            ]:
                try:
                    if selector.startswith("//"):
                        send_button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        send_button = self.wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    break
                except:
                    continue
            
            if not send_button:
                raise Exception("Could not find send button")
                
            send_button.click()
            time.sleep(2)
            
            self.logger.info("Message sent successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending message: {str(e)}")
            return False

    def send_company_message(self, message_url, message):
        """Send a message in a company chat thread"""
        try:
            # Navigate directly to the message thread
            self.driver.get(message_url)
            time.sleep(3)  # Wait for page load
            
            # Find the message input (try different selectors)
            message_input = None
            for selector in [
                "[data-test='messaging-composer'] textarea",
                "textarea[placeholder*='Type a message']",
                "textarea.message-input",
                "//textarea[contains(@placeholder, 'Type')]"
            ]:
                try:
                    if selector.startswith("//"):
                        message_input = self.wait.until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                    else:
                        message_input = self.wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                    break
                except:
                    continue
            
            if not message_input:
                raise Exception("Could not find message input")
                
            # Clear and enter message
            message_input.clear()
            message_input.send_keys(message)
            time.sleep(1)
            
            # Find and click the send button (try different selectors)
            send_button = None
            for selector in [
                "[data-test='send-message']",
                "button[type='submit']",
                ".send-button",
                "//button[contains(text(), 'Send')]"
            ]:
                try:
                    if selector.startswith("//"):
                        send_button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        send_button = self.wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    break
                except:
                    continue
            
            if not send_button:
                # Try pressing Enter key if button not found
                message_input.send_keys(Keys.RETURN)
                self.logger.info("Used Enter key to send message")
            else:
                send_button.click()
                self.logger.info("Clicked send button")
            
            time.sleep(2)
            self.logger.info("Company message sent successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending company message: {str(e)}")
            return False

    def close(self):
        try:
            if hasattr(self, 'driver'):
                self.driver.quit()
                self.logger.info("Driver closed successfully")
        except Exception as e:
            self.logger.error(f"Error closing driver: {str(e)}")
