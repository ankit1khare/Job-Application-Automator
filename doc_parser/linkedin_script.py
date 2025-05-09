import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.action_chains import ActionChains

class LinkedInLogin:
    
    def __init__(self, email, password, job_url, time_to_stay=550):
        """Initialize the class with necessary fields."""
        self.email = email
        self.password = password
        self.job_url = job_url
        self.time_to_stay = time_to_stay
        self.driver = webdriver.Chrome()  # No need to specify path if chromedriver is in the PATH
    
    def login(self):
        """Logs into LinkedIn with provided credentials."""
        self.driver.get("https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin")
        print("Trying to log in to LinkedIn...")
        
        try:
            # Find and input email
            username_field = self.driver.find_element(By.ID, "username")
            username_field.clear()
            username_field.send_keys(self.email)
            
            # Find and input password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(self.password)
            print(f"Password entered.")

            time.sleep(random.uniform(2, 5))  
            
            # Wait until the login button is clickable and then click it
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )
            login_button.click()
            print("Login successful.")
            
            # Wait for CAPTCHA challenge (if present)
            time.sleep(5)  # Giving time for CAPTCHA to load
            
            # Check if CAPTCHA is present, if so, manually solve it
            captcha_frame = self.driver.find_elements(By.XPATH, "//iframe[contains(@src, 'captcha')]")
            if captcha_frame:
                print("Please solve the CAPTCHA manually.")
                WebDriverWait(self.driver, 300).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "feed-identity-module"))  # Wait for home page to load
                )
                print("Captcha solved, proceeding to LinkedIn home page.")
            
            # Explicit wait for a more general indicator of LinkedIn's home page
            print("Waiting for LinkedIn home page to load...")
            time.sleep(random.uniform(2, 5))  
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//span[text()='My Network']"))
            )
            print("Successfully logged in, and LinkedIn home page is ready.")
            
            # Check if we're on the LinkedIn home page (could use current URL for confirmation)
            current_url = self.driver.current_url
            print(f"Current URL after login: {current_url}")
            time.sleep(random.uniform(2, 5))  
            if "feed" in current_url:
                print("Successfully reached LinkedIn home page.")
            else:
                print("Navigation issue after login.")
                
        except Exception as e:
            print(f"Error logging in: {e}")
            print("Couldn't log in to LinkedIn, please try again.")
            self.driver.quit()
            return

    

    def open_job_url(self):
        """Open the job application URL after successful login."""
        try:
            print(f"Opening the job URL: {self.job_url}")
            self.driver.get(self.job_url)
            print("Job application page opened successfully.")

            # Wait for the page to load and check for the Apply button (logged-in user case with aria-label)
            try:
                apply_button = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//button[contains(@aria-label, 'Apply to')]"))
                )
                print("Apply button found (logged-in user), clicking it.")
                apply_button.click()
                print("Apply button clicked successfully (logged-in).")
            
            except Exception as e:
                print(f"Apply button not found for logged-in user. Trying non-logged-in pattern: {e}")
                try:
                    apply_button = WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'apply-button') or contains(@class, 'sign-up-modal__outlet')]"))
                    )
                    print("Apply button found (non-logged-in), clicking it.")
                    apply_button.click()
                    print("Apply button clicked successfully (non-logged-in).")
                except Exception as e:
                    print(f"Error finding Apply button in non-logged-in scenario: {e}")
                    print("No Apply button found.")

            # Check if modal appears asking to share profile
            try:
                # Wait for the modal to appear
                modal = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@data-test-modal]"))
                )
                print("Profile share modal appeared.")

                # Corrected XPath for Continue button
                continue_button = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//button[normalize-space(text())='Continue']"))
                )
                print("Continue button found, clicking it.")
                continue_button.click()
                print("Continue button clicked successfully.")
            
            except Exception as e:
                print("No modal found or error while clicking Continue button:", e)
                print("Proceeding without clicking Continue.")

        except Exception as e:
            print(f"Error opening job URL or processing buttons: {e}")

    
    def extract_easy_apply_fields(self):
        """Extract fields from the Easy Apply modal."""
        try:
            print("Extracting fields from Easy Apply modal...")
            
            # Example: Extract Name field (adjust XPath based on actual modal structure)
            name_field = self.driver.find_element(By.XPATH, "//input[@placeholder='Enter your name']")
            print("Found Name field:", name_field.get_attribute('placeholder'))
            
            email_field = self.driver.find_element(By.XPATH, "//input[@placeholder='Enter your email']")
            print("Found Email field:", email_field.get_attribute('placeholder'))
            
            phone_field = self.driver.find_element(By.XPATH, "//input[@placeholder='Enter your phone number']")
            print("Found Phone field:", phone_field.get_attribute('placeholder'))
            
            # Other fields can be extracted similarly, e.g., experience, salary, etc.
            
            # Extract the modal's HTML to inspect all fields
            modal_html = self.driver.page_source
            print("HTML of Easy Apply modal:")
            print(modal_html)  # This will print the full HTML of the modal for further inspection
            
        except Exception as e:
            print(f"Error extracting fields from Easy Apply modal: {e}")


    def extract_application_fields(self):
        """Extract the required fields from the application form."""
        print("Extracting application fields...")
        fields = {}
        # print(self.driver.page_source)

        try:
            # Wait for the Name field using CSS Selector
            name_field = WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input[placeholder='Enter your name']"))
            )
            fields["name"] = name_field.get_attribute("value")
            print("Name:", fields["name"])
        except Exception as e:
            print("Name field not found: ", e)

        try:
            # Wait for the Email field using CSS Selector
            email_field = WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input[placeholder='Enter your email']"))
            )
            fields["email"] = email_field.get_attribute("value")
            print("Email:", fields["email"])
        except Exception as e:
            print("Email field not found: ", e)

        try:
            # Wait for the Phone field using CSS Selector
            phone_field = WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input[placeholder='Enter your phone number']"))
            )
            fields["phone"] = phone_field.get_attribute("value")
            print("Phone:", fields["phone"])
        except Exception as e:
            print("Phone field not found: ", e)

        try:
            # Wait for the Experience field using CSS Selector
            experience_field = WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input[placeholder='Enter your experience']"))
            )
            fields["experience"] = experience_field.get_attribute("value")
            print("Experience:", fields["experience"])
        except Exception as e:
            print("Experience field not found: ", e)

        try:
            # Wait for the Salary Currency field using CSS Selector
            salary_currency_field = WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input[placeholder='Salary Currency']"))
            )
            fields["salary_currency"] = salary_currency_field.get_attribute("value")
            print("Salary Currency:", fields["salary_currency"])
        except Exception as e:
            print("Salary Currency field not found: ", e)

        try:
            # Wait for the Current Salary field using CSS Selector
            current_salary_field = WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input[placeholder='Enter current salary']"))
            )
            fields["current_salary"] = current_salary_field.get_attribute("value")
            print("Current Salary:", fields["current_salary"])
        except Exception as e:
            print("Current Salary field not found: ", e)

        try:
            # Wait for the Expected Salary field using CSS Selector
            expected_salary_field = WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input[placeholder='Enter expected salary']"))
            )
            fields["expected_salary"] = expected_salary_field.get_attribute("value")
            print("Expected Salary:", fields["expected_salary"])
        except Exception as e:
            print("Expected Salary field not found: ", e)

        try:
            # Wait for the Relocation checkbox using CSS Selector
            relocate_checkbox = WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='relocate_bangalore']"))
            )
            fields["relocate_bangalore"] = relocate_checkbox.is_selected()
            print("Relocate:", fields["relocate_bangalore"])
        except Exception as e:
            print("Relocate checkbox not found: ", e)

        try:
            # Wait for the Privacy Policy checkbox using CSS Selector
            privacy_checkbox = WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='privacy_policy']"))
            )
            fields["privacy_policy"] = privacy_checkbox.is_selected()
            print("Privacy Policy:", fields["privacy_policy"])
        except Exception as e:
            print("Privacy Policy checkbox not found: ", e)

        print("Extracted fields:")
        print(fields)
        return fields

    
    def stay_on_homepage(self):
        """Keep the browser open for the specified duration."""
        print(f"Staying on LinkedIn home page for {self.time_to_stay} seconds...")
        time.sleep(self.time_to_stay)  # Stay on the home page for the desired amount of time
        print("Time's up, closing the browser now.")
        self.close_browser()

    def close_browser(self):
        """Close the browser."""
        self.driver.quit()

