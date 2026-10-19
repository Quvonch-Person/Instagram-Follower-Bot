import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    TimeoutException,
)

class InstaFollower:
    def __init__(self, username: str, password: str, target_account: str):
        self.username = username
        self.password = password
        self.target_account = target_account

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--start-maximized")
        # Useful for preventing bot flags on basic head requests
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    def login(self):
        """Navigates to login page, enters credentials, and handles prompt modals."""
        self.driver.get("https://www.instagram.com/accounts/login/")

        # Step A: Dismiss cookie banner if it appears
        try:
            cookie_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Decline') or contains(text(), 'Only allow essential')]")
                )
            )
            cookie_btn.click()
        except TimeoutException:
            pass

        # Step B: Enter user credentials
        user_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
        pass_field = self.driver.find_element(By.NAME, "password")

        user_field.clear()
        user_field.send_keys(self.username)
        pass_field.clear()
        pass_field.send_keys(self.password)
        pass_field.send_keys(Keys.ENTER)

        # Step C: Dismiss 'Save Your Login Info?' prompt
        try:
            save_info_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not now') or contains(text(), 'Not Now')]"))
            )
            save_info_btn.click()
        except TimeoutException:
            pass

        # Step D: Dismiss 'Turn on Notifications' prompt
        try:
            notification_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now') or contains(text(), 'Cancel')]"))
            )
            notification_btn.click()
        except TimeoutException:
            pass

    def find_followers(self, scroll_iterations: int = 5):
        """Navigates to target profile, opens follower modal, and scrolls to fetch list items."""
        self.driver.get(f"https://www.instagram.com/{self.target_account}/")

        # Locate the followers link by URL anchor pattern
        followers_link = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//a[contains(@href, '/{self.target_account}/followers/')]"))
        )
        followers_link.click()

        # Target the scrollable inner container of the popup dialog
        modal_container = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']//div[contains(@class, 'xyi19xy')] | //div[@role='dialog']//div[contains(@style, 'overflow')]"))
        )

        # Scroll down incrementally to trigger lazy loading of followers
        for _ in range(scroll_iterations):
            self.driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight", modal_container
            )
            time.sleep(2)

    def follow(self):
        """Iterates through loaded followers and clicks available 'Follow' buttons."""
        # Find all buttons that contain the exact text 'Follow' (ignoring 'Following' or 'Requested')
        follow_buttons = self.driver.find_elements(
            By.XPATH, "//div[@role='dialog']//button[descendant-or-self::*[text()='Follow']]"
        )

        print(f"Discovered {len(follow_buttons)} actionable follow targets.")

        for button in follow_buttons:
            try:
                button.click()
                time.sleep(1.5)  # Human simulation delay to mitigate rate-limiting

            except ElementClickInterceptedException:
                # Occurs if an unhandled confirmation overlay pops up (e.g. for private accounts)
                try:
                    cancel_btn = self.driver.find_element(
                        By.XPATH, "//button[contains(text(), 'Cancel') or contains(text(), 'Not Now')]"
                    )
                    cancel_btn.click()
                    time.sleep(1)
                except NoSuchElementException:
                    pass
            except Exception as e:
                print(f"Skipping button due to error: {e}")
                continue

    def close(self):
        self.driver.quit()