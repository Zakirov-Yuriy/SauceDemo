from __future__ import annotations

import allure
from selenium.webdriver.common.by import By

from .base_page import BasePage, Locator


class LoginPage(BasePage):
    USERNAME: Locator = (By.ID, "user-name")
    PASSWORD: Locator = (By.ID, "password")
    LOGIN_BTN: Locator = (By.ID, "login-button")
    ERROR_MSG: Locator = (By.CSS_SELECTOR, "[data-test='error']")

    def open_login(self, base_url: str) -> LoginPage:
        self.open(base_url)
        self.wait_visible(*self.USERNAME)
        return self

    @allure.step("Логин")
    def login(self, username: str, password: str) -> None:
        self.type(*self.USERNAME, text=username)
        self.type(*self.PASSWORD, text=password)
        self.click(*self.LOGIN_BTN)

    def error_text(self) -> str:
        return self.wait_visible(*self.ERROR_MSG).text
