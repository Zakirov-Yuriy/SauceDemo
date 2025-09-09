import allure
import pytest

from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


@allure.feature("Авторизация")
@allure.story("Успешный вход")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
def test_success_login_opens_products_page(browser, base_url, credentials):
    login = LoginPage(browser).open_login(base_url)
    login.login(credentials["username"], credentials["password"])

    inventory = InventoryPage(browser)
    assert inventory.is_opened()
    assert inventory.items_count() > 0
    assert "Products" in browser.page_source


# быстрый негативный кейс как пример расширения:
@pytest.mark.negative
@pytest.mark.parametrize(("username", "password"), [
    ("locked_out_user", "secret_sauce"),
    ("standard_user", "wrong_password"),
    ("", "secret_sauce"),
    ("standard_user", ""),
])
def test_login_negative_shows_error(browser, base_url, username, password):
    login = LoginPage(browser).open_login(base_url)
    login.login(username, password)
    # На невалидных данных ожидается ошибка
    assert "Epic sadface" in login.error_text()
