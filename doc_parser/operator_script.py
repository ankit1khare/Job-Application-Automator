
from dotenv import load_dotenv
load_dotenv()
import openai
from playwright.sync_api import sync_playwright
import base64
import time
from PIL import Image
from io import BytesIO
import os
import traceback
import sys
import django

class LinkedInOperatorAutomation:
    def __init__(self, email, password, job_url, resume_data,latest_resume):
        self.email = email
        self.password = password
        self.job_url = job_url
        self.resume_data = resume_data
        self.latest_resume=latest_resume
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.tools = [{
            "type": "computer_use_preview",
            "display_width": 600,
            "display_height": 800,
            "environment": "browser",
        }]


    def show_image(self, base_64_image):
        image_data = base64.b64decode(base_64_image)
        image = Image.open(BytesIO(image_data))
        image.show()

    def get_screenshot(self, page):
        return page.screenshot()

    def send_screenshot_to_openai(self, page, response, last_call_id):
        screenshot_bytes = self.get_screenshot(page)
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")
        response = self.client.responses.create(
            model="computer-use-preview",
            previous_response_id=response.id,
            tools=self.tools,
            input=[{
                "call_id": last_call_id,
                "type": "computer_call_output",
                "output": {
                    "type": "input_image",
                    "image_url": f"data:image/png;base64,{screenshot_base64}"
                }
            }],
            truncation="auto"
        )
        return response

    def handle_model_action(self, page, action):
        try:
            if action.type == "click":
                page.mouse.click(action.x, action.y, button=action.button)
            elif action.type == "type":
                page.keyboard.type(action.text)
            elif action.type == "wait":
                time.sleep(2)
        except Exception as e:
            print(f"Error handling action {action}: {e}")
        return page

    def computer_use_loop(self, browser, page, response):
        while True:
            print(f"🔍 Response Output: {response.output}")  

            if hasattr(response, "output"):
                for item in response.output:
                    if item.type == "computer_call":
                        pending_safety_checks = getattr(item, "pending_safety_checks", [])
                        if pending_safety_checks:
                            acknowledgements = [{
                                "call_id": item.call_id,
                                "type": "safety_check_acknowledgement",
                                "accepted": True
                            }]
                            print(f"Acknowledging safety checks: {[s.code for s in pending_safety_checks]}")
                            response = self.client.responses.create(
                                model="computer-use-preview",
                                previous_response_id=response.id,
                                tools=self.tools,
                                input=acknowledgements,
                                truncation="auto"
                            )
                            continue

            computer_calls = [item for item in response.output if item.type == "computer_call"]
            if not computer_calls:
                break

            computer_call = computer_calls[0]
            last_call_id = computer_call.call_id
            action = computer_call.action

            page = self.handle_model_action(page, action)
            time.sleep(1)

            response = self.send_screenshot_to_openai(page, response, last_call_id)

        return response


    def login_and_apply(self):
        print(self.resume_data,"234567890-0987654")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            page.set_viewport_size({"width": 1280, "height": 800})

            try:

                print("Navigating to LinkedIn homepage..")
                page.goto("https://www.linkedin.com/", wait_until="domcontentloaded")

                context.clear_cookies()
                page.evaluate("localStorage.clear(); sessionStorage.clear();")


                login_prompt = [{
                    "role": "user",
                    "content": f"""
You're on LinkedIn homepage.

👉 Please:
1. Click "Sign in" if a modal appears.
2. Wait for login form.
3. Enter Email: {self.email}
4. Enter Password: {self.password}
5. Click Sign in
If CAPTCHA appears, stop and wait.
"""
                }]

                response = self.client.responses.create(
                    model="computer-use-preview",
                    input=login_prompt,
                    tools=self.tools,
                    reasoning={"generate_summary": "concise"},
                    truncation="auto"
                )

                print("🤖 Trying automatic login...")
                response = self.computer_use_loop(browser, page, response)

            except Exception as e:
                print("Auto-login failed.")
                traceback.print_exc()

            input("🔐 Please login manually and press ENTER...")

            print("Navigating to job page...")
            page.goto(self.job_url, wait_until="domcontentloaded")
            time.sleep(3)

            easy_apply_prompt = [{
                "role": "user",
                "content": f"""
            You're on a LinkedIn Easy Apply form.

            1️⃣ In the **Mobile phone number** field, clear the existing value (if any) and enter:
            `{self.resume_data['contact']['phone']}`

            Once this is done, wait for the user to upload their resume manually.
            2️⃣ Scroll to and visually highlight the **Submit application** button without clicking it.

            Only perform these actions. Do not rely on pre-filled values.
            """
            }]

            print("🤖 Starting Easy Apply...")
            response = self.client.responses.create(
                model="computer-use-preview",
                input=easy_apply_prompt,
                tools=self.tools,
                reasoning={"generate_summary": "concise"},
                truncation="auto"
            )
            response = self.computer_use_loop(browser, page, response)

            print(" Please upload your resume manually.")
            input(" Once your resume is uploaded, press ENTER to proceed...")

            time.sleep(3)

            submit_choice = input("Submit application now? (yes/no): ").strip().lower()
            if submit_choice == "yes":
                print("Submitting application...")
                submit_prompt = [{
                    "role": "user",
                    "content": "Click the **Submit application** button to finalize and submit the job application. make sure button is clicked and print response after submit the application."
                }]


                response = self.client.responses.create(
                    model="computer-use-preview",
                    input=submit_prompt,
                    tools=self.tools,
                    reasoning={"generate_summary": "concise"},
                    truncation="auto"
                )
                response = self.computer_use_loop(browser, page, response)
                print("Application submitted!")
            else:
                print("Submission cancelled.")

            input("🔚 Press ENTER to close browser...")
            browser.close()


