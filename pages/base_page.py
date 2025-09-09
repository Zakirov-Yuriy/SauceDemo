from __future__ import annotations

from typing import Any, cast

from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

Locator = tuple[str, str]


class BasePage:

    def __init__(self, driver: WebDriver, timeout: int = 10) -> None:
        self.driver: WebDriver = driver
        self.wait: WebDriverWait[Any] = WebDriverWait(driver, timeout)

    def open(self, url: str) -> None:
        self.driver.get(url)

    def find(self, by: str, selector: str) -> WebElement:
        return self.driver.find_element(by, selector)

    def finds(self, by: str, selector: str) -> list[WebElement]:
        return self.driver.find_elements(by, selector)

    def click(self, by: str, selector: str) -> None:
        try:
            elem = self.wait.until(EC.element_to_be_clickable((by, selector)))

            assert elem is not None
            elem.click()
        except (ElementClickInterceptedException, TimeoutException):
            # JS-клик с прокруткой к элементу
            el = self.find(by, selector)
            cast(Any, self.driver).execute_script(
                "arguments[0].scrollIntoView({block:'center'});", el,
            )
            cast(Any, self.driver).execute_script("arguments[0].click();", el)

    def type(self, by: str, selector: str, text: str, clear: bool = True) -> None:
        el = self.wait.until(EC.visibility_of_element_located((by, selector)))
        assert el is not None
        if clear:
            el.clear()
        el.send_keys(text)

    def wait_visible(self, by: str, selector: str) -> WebElement:
        el = self.wait.until(EC.visibility_of_element_located((by, selector)))
        assert el is not None
        return el

    def current_url(self) -> str:
        return self.driver.current_url
