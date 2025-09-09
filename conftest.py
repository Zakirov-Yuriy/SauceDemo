from __future__ import annotations

import os
import platform
import shutil
import tempfile
from collections.abc import Generator, Mapping
from typing import Any, cast

import allure
import pytest
import selenium
from _pytest.fixtures import FixtureRequest
from _pytest.nodes import Item
from _pytest.runner import CallInfo
from selenium import webdriver

# Chrome
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService

# Firefox
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--browser", action="store", default="chrome")
    parser.addoption("--base-url", action="store", default="https://www.saucedemo.com")
    parser.addoption("--username", action="store", default="standard_user")
    parser.addoption("--password", action="store", default="secret_sauce")
    parser.addoption("--browser-version", action="store", default="latest")


@pytest.fixture(scope="session")
def base_url(request: FixtureRequest) -> str:
    return cast(str, request.config.getoption("--base-url"))


@pytest.fixture(scope="session")
def credentials(request: FixtureRequest) -> dict[str, str]:
    cfg = request.config
    return {
        "username": cast(str, cfg.getoption("--username")),
        "password": cast(str, cfg.getoption("--password")),
    }


@pytest.fixture(scope="session")
def browser(request: FixtureRequest) -> Generator[WebDriver, None, None]:
    browser_name = cast(str, request.config.getoption("--browser")).lower()
    browser_version = cast(str, request.config.getoption("--browser-version"))
    tmp_profile: str | None = None
    if browser_name == "chrome":
        ch_options = ChromeOptions()
        ch_options.add_argument("--window-size=1280,800")
        ch_options.add_argument("--incognito")
        ch_options.add_argument("--disable-sync")
        ch_options.add_argument("--disable-notifications")
        ch_options.add_argument("--disable-infobars")
        ch_options.add_argument("--no-first-run")
        ch_options.add_argument("--no-default-browser-check")
        ch_options.add_argument("--disable-extensions")
        ch_options.add_argument("--disable-popup-blocking")
        ch_options.add_argument("--password-store=basic")
        ch_options.browser_version = browser_version

        # Чистый пользовательский каталог на каждый запуск
        tmp_profile = tempfile.mkdtemp(prefix="chrome-profile-")

        ch_options.add_argument(f"--user-data-dir={tmp_profile}")

        # глушим менеджер паролей/проверку утечек/автозаполнение
        ch_options.add_argument(
            "--disable-features="
            "PasswordCheck,PasswordLeakDetection,"
            "PasswordManagerOnboarding,PasswordManagerRedesign,"
            "AutofillServerCommunication,AutofillEnableAccountWalletStorage",
        )

        # не предлагать сохранять пароли/карты/профили
        ch_prefs: dict[str, object] = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "autofill.profile_enabled": False,
            "autofill.credit_card_enabled": False,
            # на всякий: запрет нотификаций
            "profile.default_content_setting_values.notifications": 2,
        }
        ch_options.add_experimental_option("prefs", ch_prefs)
        ch_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        ch_options.add_experimental_option("useAutomationExtension", False)

        ch_service = ChromeService(ChromeDriverManager().install())
        driver: WebDriver = webdriver.Chrome(service=ch_service, options=ch_options)
    else:
        # Firefox
        ff_options = FirefoxOptions()
        ff_options.add_argument("--width=1280")
        ff_options.add_argument("--height=800")

        # отключаем менеджер паролей / автозаполнение / нотификации
        ff_options.set_preference("signon.rememberSignons", False)
        ff_options.set_preference("signon.autofillForms", False)
        ff_options.set_preference("signon.generation.enabled", False)
        ff_options.set_preference("dom.webnotifications.enabled", False)

        ff_service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=ff_service, options=ff_options)
    yield driver
    driver.quit()
    if tmp_profile is not None:
        shutil.rmtree(tmp_profile, ignore_errors=True)


def reset_state(browser: WebDriver, base_url: str) -> None:
    browser.delete_all_cookies()
    browser.get(base_url)
    # очистим local/session storage
    cast(Any, browser).execute_script(
        "window.localStorage.clear(); window.sessionStorage.clear();",
    )


def pytest_configure(config: pytest.Config) -> None:
    # Создаём/перезаписываем файл окружения в allure-results
    alluredir = config.getoption("--alluredir") or "allure-results"
    os.makedirs(alluredir, exist_ok=True)
    env_path = os.path.join(alluredir, "environment.properties")

    with open(env_path, "w", encoding="utf-8") as f:
        # из CLI/pytest.ini
        f.write(f"BaseURL={config.getoption('--base-url')}\n")
        f.write(f"Browser={config.getoption('--browser')}\n")
        # системная инфа
        f.write(f"OS={platform.platform()}\n")
        f.write(f"Python={platform.python_version()}\n")
        # версии зависимостей
        f.write(f"PyTest={pytest.__version__}\n")
        f.write(f"Selenium={getattr(selenium, '__version__', 'unknown')}\n")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(
        item: Item, call: CallInfo[Any],
) -> Generator[None, None, None]:
    outcome = yield

    rep = cast(Any, outcome).get_result()
    if rep.when != "call" or rep.passed:
        return

    funcargs = cast(Mapping[str, Any], getattr(item, "funcargs", {}))
    driver = funcargs.get("browser")

    if isinstance(driver, WebDriver):
        try:
            allure.attach(
                driver.current_url,
                name="current_url.txt",
                attachment_type=allure.attachment_type.TEXT,
            )

        except Exception:

            pass
        try:
            allure.attach(
                driver.page_source,
                name="page.html",
                attachment_type=allure.attachment_type.HTML,
            )
        except Exception:
            pass

        try:
            png = driver.get_screenshot_as_png()
            allure.attach(png, name="screenshot.png", attachment_type=allure.attachment_type.PNG)
        except Exception:
            pass
