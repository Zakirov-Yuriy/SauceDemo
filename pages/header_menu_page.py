from __future__ import annotations

import time

import allure
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage, Locator


class HeaderMenuPage(BasePage):
    BURGER_BTN: Locator = (By.ID, "react-burger-menu-btn")
    MENU_WRAP: Locator = (By.CLASS_NAME, "bm-menu-wrap")
    OVERLAY: Locator = (By.CLASS_NAME, "bm-overlay")
    LOGOUT_LINK: Locator = (By.ID, "logout_sidebar_link")

    def open_menu(self) -> None:

        # погасить возможные всплывашки/оверлеи
        try:
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        except Exception:
            pass

        for _ in range(3):
            self.click(*self.BURGER_BTN)
            try:
                # меню появилось
                self.wait.until(EC.any_of(
                    EC.visibility_of_element_located(self.MENU_WRAP),
                    EC.visibility_of_element_located(self.OVERLAY),
                ))
                # сам пункт Logout
                self.wait.until(EC.visibility_of_element_located(self.LOGOUT_LINK))
                return
            except TimeoutException:
                time.sleep(0.2)

        # дождаться Logout или упасть по таймауту
        self.wait.until(EC.visibility_of_element_located(self.LOGOUT_LINK))

    @allure.step("Выход пользователя через бургер-меню")
    def logout(self) -> None:
        self.open_menu()

        # Дождаться кликабельности и кликнуть обычным способом
        link = self.wait.until(EC.element_to_be_clickable(self.LOGOUT_LINK))
        assert link is not None
        try:
            link.click()
        except ElementClickInterceptedException:
            # Если анимация перехватили клик через Actions (не JS)
            ActionChains(self.driver).move_to_element(link).pause(0.05).click().perform()

        # возвращение на страницу логина и поле Username всегда выполняется
        self.wait.until(EC.url_matches(r"https://www\.saucedemo\.com/?$"))
        self.wait_visible(By.ID, "user-name")
