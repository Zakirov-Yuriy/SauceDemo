from __future__ import annotations

from selenium.webdriver.common.by import By

from .base_page import BasePage, Locator


class InventoryPage(BasePage):
    INVENTORY_LIST: Locator = (By.CLASS_NAME, "inventory_list")
    INVENTORY_ITEM: Locator = (By.CLASS_NAME, "inventory_item")

    def is_opened(self) -> bool:
        self.wait_visible(*self.INVENTORY_LIST)
        self.wait_visible(*self.TITLE)
        return "/inventory.html" in self.current_url()

    def items_count(self) -> int:
        return len(self.finds(*self.INVENTORY_ITEM))

    TITLE = (By.CLASS_NAME, "title")
