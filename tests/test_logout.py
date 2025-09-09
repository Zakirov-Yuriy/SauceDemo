import allure
import pytest
from selenium.webdriver.common.by import By

from pages.header_menu_page import HeaderMenuPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from utils.ui_guards import dismiss_popups


@allure.feature("Сессия")
@allure.story("Logout")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.logout
def test_user_can_logout(browser, base_url, credentials):
    # Шаг 1: логинимся валидным пользователем
    login = LoginPage(browser).open_login(base_url)
    login.login(credentials["username"], credentials["password"])

    # На всякий закрыть системные оверлеи
    dismiss_popups(browser)

    # Попали на страницу товаров
    inventory = InventoryPage(browser)
    assert inventory.is_opened(), "Не открылась страница товаров после логина"

    # Шаг 2-3: выходим через бургер-меню
    menu = HeaderMenuPage(browser)
    menu.logout()

    # Ожидаем страницу логина (поле Username видно)
    login_page = LoginPage(browser)
    login_page.wait_visible(By.ID, "user-name")
    assert "/" in login_page.current_url(), "После logout не вернулись на страницу логина"
