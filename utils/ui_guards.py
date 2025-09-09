from __future__ import annotations

from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver


def dismiss_popups(driver: WebDriver) -> None:
    try:
        alert = driver.switch_to.alert
        alert.dismiss()
    except:
        pass
    try:
        alert = driver.switch_to.alert
        alert.dismiss()
    except NoAlertPresentException:
        pass

    # ESC для других всплывашек
    try:
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    except:
        pass
